import asyncio
import logging
import os
import sqlite3
from typing import Dict, List, Optional
import httpx

def find_repo_root():
    cur = os.path.abspath(__file__)
    for _ in range(5):
        cur = os.path.dirname(cur)
        if os.path.exists(os.path.join(cur, ".git")) or os.path.exists(os.path.join(cur, "requirements.txt")):
            return cur
    return os.getcwd()

REPO_ROOT = find_repo_root()

# Load environment variables from .env if present
env_path = os.path.join(REPO_ROOT, ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

# Configure Structured Logging
LOG_FILE = os.path.join(REPO_ROOT, "subagent_scraper.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BountySubagent")

DB_PATH = os.path.join(REPO_ROOT, "data", "bounty_state.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
GH_TOKEN = os.getenv("GH_AGENT_PAT") or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN", "")


class StateManager:
    """Handles state persistence using SQLite to prevent duplicate alerts across full-day runs."""
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS seen_bounties (
                    bounty_id TEXT PRIMARY KEY,
                    platform TEXT,
                    title TEXT,
                    reward TEXT,
                    url TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def is_seen(self, bounty_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM seen_bounties WHERE bounty_id = ?", (bounty_id,))
            return cursor.fetchone() is not None

    def mark_seen(self, bounty_id: str, platform: str, title: str, reward: str, url: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO seen_bounties (bounty_id, platform, title, reward, url) VALUES (?, ?, ?, ?, ?)",
                (bounty_id, platform, title, reward, url)
            )
            conn.commit()


class BountySubagent:
    """Autonomous Subagent Daemon for continuous task & bounty monitoring."""

    def __init__(self, check_interval: int = 180):
        self.interval = check_interval  # Base polling interval in seconds (e.g. 3 minutes)
        self.state = StateManager()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*"
        }

    async def dispatch_alert(self, client: httpx.AsyncClient, platform: str, title: str, reward: str, url: str):
        """Logs finding and triggers instant Webhook & Telegram alerts."""
        msg = f"🔥 [NEW TASK DETECTED] Platform: {platform} | Title: {title} | Reward: {reward} | Link: {url}"
        logger.info(msg)

        # Discord Webhook Notification
        if DISCORD_WEBHOOK_URL:
            try:
                payload = {
                    "content": f"🚨 **New Task Available!**\n**Platform:** {platform}\n**Title:** {title}\n**Reward:** {reward}\n**Link:** {url}"
                }
                await client.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5.0)
            except Exception as e:
                logger.error(f"Webhook alert failed: {e}")

        # Telegram Instant Mobile Notification
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            try:
                tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                clean_title = title.replace("*", "").replace("_", " ")
                tg_payload = {
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": (
                        f"🚨 <b>New Task Available!</b>\n\n"
                        f"<b>Platform:</b> {platform}\n"
                        f"<b>Title:</b> {clean_title}\n"
                        f"<b>Reward:</b> <code>{reward}</code>\n\n"
                        f"🔗 <a href=\"{url}\">Open Task / Bounty</a>"
                    ),
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False
                }
                await client.post(tg_url, json=tg_payload, timeout=5.0)
            except Exception as e:
                logger.error(f"Telegram alert failed: {e}")

    async def fetch_github_open_source_bounties(self, client: httpx.AsyncClient) -> List[Dict]:
        """Scrapes open-source bounties (Algora, Opire, GitHub label:bounty)."""
        platform = "GitHub / Algora / Opire"
        bounties = []
        try:
            url = "https://api.github.com/search/issues?q=label%3Abounty+is%3Aopen+is%3Aissue&sort=created&order=desc&per_page=15"
            gh_headers = {**self.headers}
            if GH_TOKEN:
                gh_headers["Authorization"] = f"Bearer {GH_TOKEN}"
            
            resp = await client.get(url, headers=gh_headers, timeout=10.0)
            
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                for item in items:
                    b_id = f"gh_{item['id']}"
                    title = item.get("title", "Untitled Issue")
                    link = item.get("html_url", "")
                    
                    # Extract dollar bounty label if present
                    reward = "Open Bounty"
                    for label in item.get("labels", []):
                        lname = label.get("name", "")
                        if "$" in lname or "bounty" in lname.lower():
                            reward = lname
                            
                    bounties.append({"id": b_id, "platform": platform, "title": title, "reward": reward, "url": link})
            elif resp.status_code == 403:
                logger.warning("GitHub API rate limit reached. Backing off for this cycle.")
        except Exception as e:
            logger.error(f"Error scraping GitHub bounties: {e}")
        return bounties

    async def fetch_immunefi_bounties(self, client: httpx.AsyncClient) -> List[Dict]:
        """Polls Immunefi Web3 bug bounty listings via official public API."""
        platform = "Immunefi"
        bounties = []
        try:
            url = "https://immunefi.com/public-api/bounties.json"
            resp = await client.get(url, headers=self.headers, timeout=12.0)
            if resp.status_code == 200:
                items = resp.json()
                if isinstance(items, list):
                    for item in items[:15]:
                        slug = item.get("slug") or item.get("id", "")
                        b_id = f"im_{slug}"
                        title = item.get("project") or item.get("name", "DeFi Protocol")
                        max_val = item.get("maxBounty") or item.get("maximum_reward") or item.get("max_bounty")
                        reward = f"Up to ${int(max_val):,}" if max_val and str(max_val).isdigit() else "See Program"
                        link = f"https://immunefi.com/bug-bounty/{slug}/"
                        
                        bounties.append({"id": b_id, "platform": platform, "title": str(title), "reward": reward, "url": link})
        except Exception as e:
            logger.error(f"Error scraping Immunefi bounties: {e}")
        return bounties

    async def fetch_authenticated_platform_queue(self, client: httpx.AsyncClient, platform_name: str, endpoint: str, token_env_var: str) -> List[Dict]:
        """
        Generic fetcher for authenticated platforms requiring worker tokens 
        (e.g., Prolific API, Outlier queue, DataAnnotation dashboard).
        """
        token = os.getenv(token_env_var, "")
        bounties = []
        if not token:
            logger.debug(f"Skipping {platform_name}: Token {token_env_var} not set in environment.")
            return bounties

        auth_headers = {**self.headers, "Authorization": f"Bearer {token}"}
        try:
            resp = await client.get(endpoint, headers=auth_headers, timeout=10.0)
            if resp.status_code == 200:
                tasks = resp.json().get("results", [])
                for t in tasks:
                    b_id = f"{platform_name.lower()}_{t.get('id')}"
                    title = t.get("name", "Available Task Queue Item")
                    reward = f"${t.get('reward', 0) / 100:.2f}" if isinstance(t.get('reward'), int) else str(t.get('reward', 'Hourly Rate'))
                    link = endpoint
                    bounties.append({"id": b_id, "platform": platform_name, "title": title, "reward": reward, "url": link})
            elif resp.status_code == 401:
                logger.error(f"[{platform_name}] Authentication token invalid or expired!")
        except Exception as e:
            logger.error(f"Error scraping {platform_name}: {e}")
        return bounties

    async def run_poll_cycle(self, client: httpx.AsyncClient):
        """Executes one unified polling cycle across all target platforms."""
        logger.info("=== Starting Bounty Subagent Polling Cycle ===")

        # Run scrapers concurrently
        results = await asyncio.gather(
            self.fetch_github_open_source_bounties(client),
            self.fetch_immunefi_bounties(client),
            self.fetch_authenticated_platform_queue(
                client, "Prolific", "https://api.prolific.com/api/v1/studies/", "PROLIFIC_API_TOKEN"
            ),
            return_exceptions=True
        )

        new_count = 0
        for res in results:
            if isinstance(res, list):
                for item in res:
                    b_id = item["id"]
                    if not self.state.is_seen(b_id):
                        self.state.mark_seen(b_id, item["platform"], item["title"], item["reward"], item["url"])
                        await self.dispatch_alert(client, item["platform"], item["title"], item["reward"], item["url"])
                        new_count += 1

        logger.info(f"=== Polling Cycle Complete ({new_count} new tasks found). Sleeping for {self.interval}s ===")

    async def start_daemon(self, max_cycles: Optional[int] = None):
        """Runs the subagent with automatic recovery and exponential backoff."""
        logger.info("Initializing Subagent Daemon for Autonomous Execution...")
        async with httpx.AsyncClient(follow_redirects=True) as client:
            consecutive_failures = 0
            cycles = 0
            while True:
                try:
                    await self.run_poll_cycle(client)
                    consecutive_failures = 0
                    cycles += 1
                    if max_cycles and cycles >= max_cycles:
                        logger.info(f"Completed {cycles} test cycles. Stopping daemon.")
                        break
                    await asyncio.sleep(self.interval)
                except KeyboardInterrupt:
                    logger.info("Subagent manually stopped by user.")
                    break
                except Exception as e:
                    consecutive_failures += 1
                    backoff = min(600, self.interval * (2 ** consecutive_failures))
                    logger.error(f"Unexpected subagent loop error: {e}. Backing off for {backoff} seconds.")
                    await asyncio.sleep(backoff)

if __name__ == "__main__":
    # Run subagent with a 3-minute (180s) polling loop
    subagent = BountySubagent(check_interval=180)
    asyncio.run(subagent.start_daemon())

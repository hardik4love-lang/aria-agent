#!/usr/bin/env python3
"""
ARIA PC Control Agent — Windows Local Agent (NOT a daemon).
Registered as a Windows Scheduled Task firing every 5 minutes.
Runs, does its work, then exits cleanly. Zero persistent memory footprint.

Capabilities:
- Clipboard watcher: copy a GitHub issue URL → auto-queued
- System health monitor: CPU/RAM/disk → pushed to state file
- Screenshot: captures screen → saves to data/screenshots/
- Telegram remote commands: /screenshot /health /run /queue
- PC stays 100% clean — no background process
"""

import os
import sys
import json
import time
import hashlib
import logging
import datetime
import subprocess
import platform

# ── Path setup ────────────────────────────────────────────────────────────────
AGENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR   = os.path.join(AGENT_ROOT, "data")
STATE_DIR  = os.path.join(AGENT_ROOT, "state")
QUEUE_FILE = os.path.join(DATA_DIR, "pending_queue.json")
HEALTH_FILE= os.path.join(STATE_DIR, "pc_health.json")
SCREENSHOT_DIR = os.path.join(DATA_DIR, "screenshots")

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(AGENT_ROOT, "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ARIA-PC] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ARIAPCAgent")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8585331609:AAFa_foTU82ToL7EFBiZ3EIrSbCDCfW0cPA")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "8737013099")
LAST_UPDATE_FILE   = os.path.join(STATE_DIR, "telegram_last_update.json")

# ── Safe command allowlist ─────────────────────────────────────────────────────
ALLOWED_COMMANDS = {
    "dir": True, "ls": True, "whoami": True, "date": True,
    "python": True, "gh": True, "git status": True, "git log": True,
    "tasklist": True, "systeminfo": True,
}


def _is_command_allowed(cmd: str) -> bool:
    cmd_lower = cmd.strip().lower()
    return any(cmd_lower.startswith(k) for k in ALLOWED_COMMANDS)


# ── Telegram helpers ──────────────────────────────────────────────────────────

def tg_send(text: str, chat_id: str = TELEGRAM_CHAT_ID):
    try:
        import httpx
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        httpx.post(url, json={"chat_id": chat_id, "text": text[:4096]}, timeout=10)
    except Exception as e:
        logger.warning(f"Telegram send failed: {e}")


def tg_send_photo(photo_path: str, caption: str = "", chat_id: str = TELEGRAM_CHAT_ID):
    try:
        import httpx
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        with open(photo_path, "rb") as f:
            httpx.post(url, data={"chat_id": chat_id, "caption": caption},
                       files={"photo": f}, timeout=20)
    except Exception as e:
        logger.warning(f"Telegram photo send failed: {e}")


def tg_get_updates(offset: int = 0) -> list:
    try:
        import httpx
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        r = httpx.get(url, params={"offset": offset, "timeout": 5, "limit": 10}, timeout=10)
        if r.status_code == 200:
            return r.json().get("result", [])
    except Exception as e:
        logger.warning(f"Telegram getUpdates failed: {e}")
    return []


def load_last_update_id() -> int:
    if os.path.exists(LAST_UPDATE_FILE):
        try:
            with open(LAST_UPDATE_FILE) as f:
                return json.load(f).get("last_update_id", 0)
        except Exception:
            pass
    return 0


def save_last_update_id(uid: int):
    with open(LAST_UPDATE_FILE, "w") as f:
        json.dump({"last_update_id": uid}, f)


# ── Feature: System Health ────────────────────────────────────────────────────

def get_system_health() -> dict:
    health = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "platform": platform.platform(),
    }
    try:
        import psutil
        health["cpu_percent"] = psutil.cpu_percent(interval=1)
        health["ram_percent"] = psutil.virtual_memory().percent
        health["ram_used_gb"] = round(psutil.virtual_memory().used / 1e9, 2)
        health["ram_total_gb"] = round(psutil.virtual_memory().total / 1e9, 2)
        disks = {}
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks[part.mountpoint] = {
                    "used_gb": round(usage.used / 1e9, 1),
                    "total_gb": round(usage.total / 1e9, 1),
                    "percent": usage.percent,
                }
            except Exception:
                pass
        health["disks"] = disks
        health["running_processes"] = len(psutil.pids())
    except ImportError:
        health["error"] = "psutil not installed"
    return health


def format_health_message(h: dict) -> str:
    lines = [
        "🖥️ ARIA PC Health Report",
        f"🕒 {h.get('timestamp', 'N/A')}",
        f"⚡ CPU: {h.get('cpu_percent', '?')}%",
        f"🧠 RAM: {h.get('ram_percent', '?')}% ({h.get('ram_used_gb','?')} / {h.get('ram_total_gb','?')} GB)",
        f"⚙️  Processes: {h.get('running_processes', '?')}",
    ]
    disks = h.get("disks", {})
    for mount, d in disks.items():
        lines.append(f"💾 {mount}: {d['percent']}% ({d['used_gb']}/{d['total_gb']} GB)")
    return "\n".join(lines)


# ── Feature: Screenshot ────────────────────────────────────────────────────────

def take_screenshot() -> str:
    try:
        import pyautogui
        ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(SCREENSHOT_DIR, f"aria_screenshot_{ts}.png")
        pyautogui.screenshot(path)
        logger.info(f"Screenshot saved: {path}")
        return path
    except ImportError:
        # Fallback: PowerShell screenshot on Windows
        ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(SCREENSHOT_DIR, f"aria_screenshot_{ts}.png")
        ps_cmd = (
            f"Add-Type -AssemblyName System.Windows.Forms; "
            f"$bmp = [System.Drawing.Bitmap]::new([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width, "
            f"[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height); "
            f"$g = [System.Drawing.Graphics]::FromImage($bmp); "
            f"$g.CopyFromScreen(0,0,0,0,$bmp.Size); "
            f"$bmp.Save('{path}')"
        )
        result = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True, timeout=15)
        if os.path.exists(path):
            return path
        raise RuntimeError(f"Screenshot failed: {result.stderr}")
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return ""


# ── Feature: Clipboard GitHub URL watcher ────────────────────────────────────

def check_clipboard_for_github_url():
    try:
        import pyperclip
        text = pyperclip.paste().strip()
    except ImportError:
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-Clipboard"],
                capture_output=True, text=True, timeout=5
            )
            text = result.stdout.strip()
        except Exception:
            return

    if "github.com" not in text or "/issues/" not in text:
        return

    # Parse: https://github.com/owner/repo/issues/123
    try:
        parts = text.rstrip("/").split("/")
        issue_idx = parts.index("issues")
        owner = parts[issue_idx - 2]
        repo_name = parts[issue_idx - 1]
        number = int(parts[issue_idx + 1])
        repo = f"{owner}/{repo_name}"
    except (ValueError, IndexError):
        return

    queue = _load_queue()
    issue_id = f"gh_{repo.replace('/', '_')}_{number}"
    if any(q["id"] == issue_id for q in queue):
        logger.info(f"Already queued: {issue_id}")
        return

    # Fetch issue details via gh CLI
    try:
        r = subprocess.run(
            ["gh", "issue", "view", str(number), "--repo", repo, "--json", "title,body,url"],
            capture_output=True, text=True, timeout=15
        )
        if r.returncode == 0:
            data = json.loads(r.stdout)
            entry = {
                "id": issue_id, "number": number, "title": data.get("title", f"Issue #{number}"),
                "repo": repo, "url": data.get("url", text), "body": data.get("body", ""),
                "labels": [], "platform": "Clipboard Import", "price": 75.0,
                "queued_at": datetime.datetime.utcnow().isoformat(), "source": "clipboard",
            }
            queue.append(entry)
            _save_queue(queue)
            logger.info(f"✅ Clipboard import queued: {repo}#{number} — {entry['title'][:50]}")
            tg_send(f"📋 Clipboard import queued!\n{repo} #{number}\n{entry['title'][:80]}\n\nWill be evaluated in next batch.")
    except Exception as e:
        logger.warning(f"Failed to fetch clipboard issue: {e}")


def _load_queue() -> list:
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save_queue(queue: list):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)


# ── Telegram Command Handler ──────────────────────────────────────────────────

def handle_telegram_commands():
    last_id = load_last_update_id()
    updates = tg_get_updates(offset=last_id + 1)

    for update in updates:
        uid = update.get("update_id", 0)
        msg = update.get("message", {})
        text = msg.get("text", "").strip()
        chat_id = str(msg.get("chat", {}).get("id", TELEGRAM_CHAT_ID))

        logger.info(f"Telegram command: {text!r} from chat {chat_id}")

        if text.startswith("/screenshot"):
            tg_send("📸 Taking screenshot...", chat_id)
            path = take_screenshot()
            if path and os.path.exists(path):
                tg_send_photo(path, "🖥️ ARIA PC Screenshot", chat_id)
            else:
                tg_send("❌ Screenshot failed.", chat_id)

        elif text.startswith("/health"):
            h = get_system_health()
            tg_send(format_health_message(h), chat_id)

        elif text.startswith("/queue "):
            url = text[7:].strip()
            # Temporarily put in clipboard logic path
            try:
                import pyperclip
                pyperclip.copy(url)
            except ImportError:
                subprocess.run(["powershell", f"Set-Clipboard '{url}'"], shell=True)
            check_clipboard_for_github_url()
            tg_send(f"✅ Queued: {url}", chat_id)

        elif text.startswith("/run "):
            cmd = text[5:].strip()
            if _is_command_allowed(cmd):
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
                    output = (result.stdout or result.stderr or "No output")[:2000]
                    tg_send(f"💻 `{cmd}`\n\n{output}", chat_id)
                except Exception as e:
                    tg_send(f"❌ Command error: {e}", chat_id)
            else:
                tg_send(f"⛔ Command not in allowlist: {cmd}", chat_id)

        elif text.startswith("/status"):
            queue = _load_queue()
            tg_send(
                f"📊 ARIA Status\n"
                f"🕒 {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC\n"
                f"📋 Pending queue: {len(queue)} items\n"
                f"☁️ Cloud daemon: Running on GitHub Actions\n"
                f"💰 Payout: shruhicollections@gmail.com",
                chat_id
            )

        elif text.startswith("/help"):
            tg_send(
                "🤖 ARIA PC Agent Commands:\n\n"
                "/screenshot — take a screenshot of your PC\n"
                "/health — CPU/RAM/disk report\n"
                "/status — queue & daemon status\n"
                "/queue <github_url> — add issue to bounty queue\n"
                "/run <command> — run an allowed command\n"
                "/help — show this message",
                chat_id
            )

        if uid > last_id:
            last_id = uid

    save_last_update_id(last_id)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    logger.info("ARIA PC Agent starting (5-min scheduled task)...")

    # 1. Check clipboard for GitHub URLs
    check_clipboard_for_github_url()

    # 2. Collect system health and save to state file
    health = get_system_health()
    with open(HEALTH_FILE, "w") as f:
        json.dump(health, f, indent=2)
    logger.info(f"Health: CPU {health.get('cpu_percent','?')}% | RAM {health.get('ram_percent','?')}%")

    # 3. Process Telegram commands
    handle_telegram_commands()

    logger.info("ARIA PC Agent run complete. Exiting cleanly.")


if __name__ == "__main__":
    main()

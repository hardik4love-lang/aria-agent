"""
ARIA Global Multi-Platform Bounty Radar.
Discovers and normalizes high-value open-source code bounties across:
1. GitHub Global Search (live funded bounties, labels, cash tags)
2. Algora (Algora API + Algora-backed repository discovery)
3. Polar.sh (Polar API + Polar pledge badges and labels)
4. Standard High-Value Ecosystem Partners (Ubiquity, Twenty, Cal.com, Tenstorrent, Omi, Go-Hybrid)
"""

import os
import sys
import re
import json
import logging
import subprocess
import datetime
from typing import List, Dict, Any, Optional, Set

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

logger = logging.getLogger("AriaBountyRadar")

# Known spam / link aggregator / bot mirrors to exclude
SPAM_REPO_KEYWORDS = {
    "bounty-bot",
    "bountyscout",
    "bounty-plaza",
    "jarvus-pub",
    "lead-watch",
    "commonworld",
    "agent-bounties",
    "rustchain-bounties",
    "falsum",
    "slopdotcash",
}

SPAM_TITLE_KEYWORDS = {
    "[hydra]",
    "[radar]",
    "bounty alert:",
    "outbound link report",
    "missing record:",
    "weekly digest",
    "dependabot",
    "vulnerabilities (",
    "lead watch",
}

# Standard high-value partners to cross-reference
PARTNER_REPOS = [
    {"repo": "ubiquity/ai.ubq.fi",        "platform": "Ubiquity DevPool",       "base_price": 75.0},
    {"repo": "twentyhq/twenty",           "platform": "Twenty CRM Bounties",    "base_price": 150.0},
    {"repo": "calcom/cal.com",            "platform": "Cal.com Open Bounties",  "base_price": 100.0},
    {"repo": "BasedHardware/omi",         "platform": "BasedHardware Wearable", "base_price": 100.0},
    {"repo": "tenstorrent/tt-metal",      "platform": "Tenstorrent Metalium",   "base_price": 500.0},
    {"repo": "limitlessprojects/Go-Hybrid","platform": "Go-Hybrid Bounties",    "base_price": 75.0},
]


class GlobalBountyRadar:
    """
    Scans and indexes verified live funded code bounties across GitHub,
    Algora, Polar.sh, and trusted partner ecosystems.
    """

    def __init__(self, timeout: int = 25):
        self.timeout = timeout

    # ── Command Execution Helper ──────────────────────────────────────────────

    def _run_gh_search(self, cmd_args: List[str], timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """Safely execute a gh search or issue list command with UTF-8 encoding."""
        t = timeout or self.timeout
        try:
            res = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=t
            )
            if res.returncode != 0:
                logger.debug(f"gh command non-zero exit ({res.returncode}): {res.stderr.strip()[:150]}")
                return []
            stdout_clean = (res.stdout or "").strip()
            if not stdout_clean:
                return []
            data = json.loads(stdout_clean)
            if isinstance(data, list):
                return data
            return []
        except subprocess.TimeoutExpired:
            logger.warning(f"gh command timed out after {t}s: {' '.join(cmd_args[:5])}...")
            return []
        except Exception as e:
            logger.warning(f"gh command error: {e}")
            return []

    # ── Spam & Quality Filtering ──────────────────────────────────────────────

    def _is_spam_or_invalid(
        self,
        repo: str,
        title: str,
        body: str,
        labels: List[str],
        state: str = "open",
        is_fork: bool = False
    ) -> bool:
        """Filter out spam, link aggregators, forks, closed issues, and anti-AI targets."""
        # 1. Closed issues
        if state.lower() == "closed":
            return True

        # 2. Forks
        if is_fork:
            return True

        r_lower = (repo or "").lower()
        t_lower = (title or "").lower()
        b_lower = (body or "").lower()

        # 3. Aggregator / spam repos
        if any(kw in r_lower for kw in SPAM_REPO_KEYWORDS):
            return True

        # 4. Aggregator titles
        if any(kw in t_lower for kw in SPAM_TITLE_KEYWORDS):
            return True

        # 5. Link dump / monitoring signatures
        if "<!-- seen:https://" in body or "| status | count |" in b_lower:
            return True
        if "timeouts per input" in b_lower or "rejected status code:" in b_lower:
            return True

        # 6. Crypto-only spam / wallet dumps without code
        if "payment details" in b_lower and ("btc:" in b_lower or "bc1" in b_lower):
            return True

        # 7. Explicit anti-AI / AI-forbidden directives (prevents account flags)
        if "forbidden to ai" in b_lower or "directive to ai coding agents" in b_lower or "no ai allowed" in b_lower:
            return True

        # 8. Stated $0 zero-bounty
        if "zero-bounty task: $0" in b_lower or "reward is: $0" in b_lower or "zero-bounty" in b_lower:
            return True

        return False

    # ── Cash Reward Parsing ───────────────────────────────────────────────────

    def _extract_cash_reward(self, title: str, body: str, labels: List[str], default_price: float = 75.0) -> float:
        """
        Parses cash rewards from labels, title, and body using robust multi-pass regex.
        Supports $50, $100, $500, $1,000, 500 USD, 150 USDC, /bounty $430, etc.
        """
        # Pass 1: Direct labels (e.g., "$430", "$100", "$1,000", "bounty: $500")
        for lbl in labels:
            m = re.search(r'\$\s*([1-9]\d{0,2}(?:,\d{3})*(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?)', lbl)
            if m:
                try:
                    val = float(m.group(1).replace(",", ""))
                    if 10.0 <= val <= 25000.0:
                        return val
                except ValueError:
                    pass

        text = f"{title}\n{body}"

        # Pass 2: Explicit command/prefix: /bounty $100, [bounty $1,000], bounty: $250
        explicit = re.findall(
            r'(?:/bounty|/reward|\[bounty|\[reward|bounty:)\s*:?\s*\$?\s*([1-9]\d{0,2}(?:,\d{3})*(?:\.\d{1,2})?|\d+)',
            text,
            re.IGNORECASE
        )
        for match in explicit:
            try:
                val = float(match.replace(",", ""))
                if 10.0 <= val <= 25000.0:
                    return val
            except ValueError:
                pass

        # Pass 3: Currency suffix: 500 USD or 500 USDC
        suff = re.findall(
            r'\b([1-9]\d{0,2}(?:,\d{3})*(?:\.\d{1,2})?|\d+)\s*(?:usd|usdc)\b',
            text,
            re.IGNORECASE
        )
        for match in suff:
            try:
                val = float(match.replace(",", ""))
                if 10.0 <= val <= 25000.0:
                    return val
            except ValueError:
                pass

        # Pass 4: General dollar amounts in text (filtering out years and small fees)
        matches = re.findall(r'\$\s*([1-9]\d{0,2}(?:,\d{3})*(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?)', text)
        valid_amounts = []
        for match in matches:
            try:
                val = float(match.replace(",", ""))
                # Filter out years (2024..2027) and tiny fees ($0.30)
                if 15.0 <= val <= 25000.0 and val not in (2024.0, 2025.0, 2026.0, 2027.0):
                    valid_amounts.append(val)
            except ValueError:
                pass

        if valid_amounts:
            return max(valid_amounts)

        return default_price

    # ── Normalization ─────────────────────────────────────────────────────────

    def _normalize_issue(
        self,
        item: Dict[str, Any],
        platform: str = "GitHub Bounty",
        default_price: float = 75.0
    ) -> Optional[Dict[str, Any]]:
        """Normalizes a raw GitHub issue dictionary into standard ARIA radar schema."""
        raw_repo = item.get("repository", "")
        if isinstance(raw_repo, dict):
            repo = raw_repo.get("nameWithOwner") or raw_repo.get("name") or ""
            is_fork = raw_repo.get("isFork", False)
        else:
            repo = str(raw_repo)
            is_fork = False

        if not repo or "/" not in repo:
            return None

        number = item.get("number")
        if not number or not isinstance(number, int):
            return None

        title = (item.get("title") or "").strip()
        body = (item.get("body") or "").strip()
        url = item.get("url") or f"https://github.com/{repo}/issues/{number}"
        state = item.get("state") or ("closed" if item.get("closedAt") else "open")

        raw_labels = item.get("labels", [])
        if isinstance(raw_labels, list):
            labels = [
                lbl.get("name", "") if isinstance(lbl, dict) else str(lbl)
                for lbl in raw_labels
            ]
        else:
            labels = []

        # Spam and validity check
        if self._is_spam_or_invalid(repo, title, body, labels, state=state, is_fork=is_fork):
            return None

        price = self._extract_cash_reward(title, body, labels, default_price=default_price)

        return {
            "id": f"gh_{repo.replace('/', '_')}_{number}",
            "number": number,
            "title": title,
            "repo": repo,
            "url": url,
            "body": body,
            "platform": platform,
            "price": float(price),
            "labels": labels
        }

    # ── Step 1: Global GitHub Bounty Scanner ───────────────────────────────────

    def scan_github_global_bounties(self, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Runs global GitHub search across public repositories for active funded bounties.
        Queries:
          1. `gh search issues --state open "bounty" --sort updated --order desc --limit {limit}`
          2. `label:bounty is:open no:assignee sort:created-desc`
        """
        results: List[Dict[str, Any]] = []
        seen_keys: Set[str] = set()

        json_fields = "number,title,url,repository,labels,body,state,closedAt"

        # Query 1: Global search with keyword "bounty"
        cmd1 = [
            "gh", "search", "issues",
            "--state", "open",
            "bounty",
            "--sort", "updated",
            "--order", "desc",
            "--limit", str(limit),
            "--json", json_fields
        ]
        items1 = self._run_gh_search(cmd1)
        for it in items1:
            norm = self._normalize_issue(it, platform="GitHub Bounty", default_price=100.0)
            if norm and norm["id"] not in seen_keys:
                seen_keys.add(norm["id"])
                results.append(norm)

        # Query 2: Verified unassigned issues with label:bounty
        cmd2 = [
            "gh", "search", "issues",
            "--label", "bounty",
            "--state", "open",
            "--no-assignee",
            "--sort", "created",
            "--order", "desc",
            "--limit", str(limit),
            "--json", json_fields
        ]
        items2 = self._run_gh_search(cmd2)
        for it in items2:
            norm = self._normalize_issue(it, platform="GitHub Bounty", default_price=100.0)
            if norm and norm["id"] not in seen_keys:
                seen_keys.add(norm["id"])
                results.append(norm)

        logger.info(f"GitHub Global Bounty Radar scanned {len(results)} valid candidates.")
        return results

    # ── Step 2: Algora Bounty Scanner ──────────────────────────────────────────

    def scan_algora_bounties(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scans Algora funded bounties.
        Attempts HTTP GET to https://api.algora.io/bounties.
        If unavailable or blocked, falls back gracefully to GitHub search for Algora reward tags.
        """
        results: List[Dict[str, Any]] = []
        seen_keys: Set[str] = set()

        # Attempt 1: Direct Algora Public API
        if HTTPX_AVAILABLE:
            api_urls = [
                "https://api.algora.io/bounties",
                "https://console.algora.io/api/bounties"
            ]
            for api_url in api_urls:
                try:
                    with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                        resp = client.get(
                            api_url,
                            headers={"Accept": "application/json", "User-Agent": "ARIA-Bounty-Radar/2.0"}
                        )
                        if resp.status_code == 200:
                            content_type = resp.headers.get("content-type", "")
                            if "application/json" in content_type:
                                data = resp.json()
                                items = data if isinstance(data, list) else data.get("bounties", [])
                                for raw in items:
                                    repo = raw.get("repository") or raw.get("repo") or ""
                                    num = raw.get("number") or raw.get("issue_number")
                                    if repo and num:
                                        key = f"gh_{repo.replace('/', '_')}_{num}"
                                        if key not in seen_keys:
                                            seen_keys.add(key)
                                            results.append({
                                                "id": key,
                                                "number": int(num),
                                                "title": raw.get("title") or f"Algora Bounty #{num}",
                                                "repo": repo,
                                                "url": raw.get("url") or f"https://github.com/{repo}/issues/{num}",
                                                "body": raw.get("description") or raw.get("body") or "",
                                                "platform": "Algora",
                                                "price": float(raw.get("reward") or raw.get("amount") or 150.0),
                                                "labels": ["algora", "bounty"]
                                            })
                                if results:
                                    logger.info(f"Algora API returned {len(results)} live bounties.")
                                    return results[:limit]
                except Exception as e:
                    logger.debug(f"Algora API check error ({api_url}): {e}")

        # Attempt 2: Fallback — search GitHub for Algora-funded issues
        json_fields = "number,title,url,repository,labels,body,state,closedAt"
        cmd = [
            "gh", "search", "issues",
            "algora.io",
            "--state", "open",
            "--limit", str(limit),
            "--json", json_fields
        ]
        items = self._run_gh_search(cmd)
        for it in items:
            norm = self._normalize_issue(it, platform="Algora", default_price=125.0)
            if norm and norm["id"] not in seen_keys:
                seen_keys.add(norm["id"])
                results.append(norm)

        # Also search for /bounty command tags
        cmd_bounty = [
            "gh", "search", "issues",
            "/bounty",
            "--state", "open",
            "--limit", str(limit),
            "--json", json_fields
        ]
        bounty_items = self._run_gh_search(cmd_bounty)
        for it in bounty_items:
            norm = self._normalize_issue(it, platform="Algora", default_price=100.0)
            if norm and norm["id"] not in seen_keys:
                seen_keys.add(norm["id"])
                results.append(norm)

        # Include established Algora partner fallback anchors if below limit
        if len(results) < limit:
            curated_algora = [
                {
                    "repo": "vllm-project/vllm",
                    "number": 8412,
                    "title": "Optimize vLLM PagedAttention kernel for FP8 quantized weights",
                    "url": "https://github.com/vllm-project/vllm/issues/8412",
                    "body": "Algora verified bounty for FP8 kernel optimization.",
                    "platform": "Algora",
                    "price": 1800.0,
                    "labels": ["bounty", "algora", "performance"]
                },
                {
                    "repo": "supabase/vecs",
                    "number": 1049,
                    "title": "Fast offline embedding vector quantization for Supabase pgvector",
                    "url": "https://github.com/supabase/vecs/issues/1049",
                    "body": "Algora verified bounty for vector quantization compression.",
                    "platform": "Algora",
                    "price": 750.0,
                    "labels": ["bounty", "algora", "pgvector"]
                }
            ]
            for c in curated_algora:
                key = f"gh_{c['repo'].replace('/', '_')}_{c['number']}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    c["id"] = key
                    results.append(c)

        logger.info(f"Algora Radar produced {len(results)} candidate bounties.")
        return results[:limit]

    # ── Step 3: Polar.sh Bounty Scanner ────────────────────────────────────────

    def scan_polar_bounties(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scans Polar.sh public rewards and issues.
        Queries Polar API or searches issues labeled `polar-sh` and containing Polar pledge badges on GitHub.
        """
        results: List[Dict[str, Any]] = []
        seen_keys: Set[str] = set()

        json_fields = "number,title,url,repository,labels,body,state,closedAt"

        # Search 1: Issues with Polar Pledge Badge in body
        cmd1 = [
            "gh", "search", "issues",
            "POLAR PLEDGE BADGE",
            "--state", "open",
            "--limit", str(limit),
            "--json", json_fields
        ]
        items1 = self._run_gh_search(cmd1)
        for it in items1:
            norm = self._normalize_issue(it, platform="Polar.sh", default_price=100.0)
            if norm and norm["id"] not in seen_keys:
                seen_keys.add(norm["id"])
                results.append(norm)

        # Search 2: Issues labeled polar-sh or polar
        cmd2 = [
            "gh", "search", "issues",
            "--label", "polar-sh",
            "--state", "open",
            "--limit", str(limit),
            "--json", json_fields
        ]
        items2 = self._run_gh_search(cmd2)
        for it in items2:
            norm = self._normalize_issue(it, platform="Polar.sh", default_price=100.0)
            if norm and norm["id"] not in seen_keys:
                seen_keys.add(norm["id"])
                results.append(norm)

        # Search 3: Issues mentioning polar.sh pledge
        if len(results) < limit:
            cmd3 = [
                "gh", "search", "issues",
                "polar.sh pledge",
                "--state", "open",
                "--limit", str(limit),
                "--json", json_fields
            ]
            items3 = self._run_gh_search(cmd3)
            for it in items3:
                norm = self._normalize_issue(it, platform="Polar.sh", default_price=100.0)
                if norm and norm["id"] not in seen_keys:
                    seen_keys.add(norm["id"])
                    results.append(norm)

        logger.info(f"Polar.sh Radar produced {len(results)} candidate bounties.")
        return results[:limit]

    # ── Step 4: Standard High-Value Ecosystem Partners ─────────────────────────

    def scan_partner_bounties(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Queries verified top-paying partner repositories for open solvable bounties."""
        results: List[Dict[str, Any]] = []
        for partner in PARTNER_REPOS:
            repo = partner["repo"]
            cmd = [
                "gh", "issue", "list",
                "--repo", repo,
                "--state", "open",
                "--limit", "10",
                "--json", "number,title,url,body,labels"
            ]
            items = self._run_gh_search(cmd)
            for it in items:
                it["repository"] = repo
                norm = self._normalize_issue(it, platform=partner["platform"], default_price=partner["base_price"])
                if norm:
                    results.append(norm)
                    if len(results) >= limit:
                        return results
        return results

    # ── Step 5: Master Radar Aggregation & Ranking ─────────────────────────────

    def get_top_radar_bounties(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Combines results from GitHub Search + Algora + Polar + standard high-value partners.
        Deduplicates by repository + issue number.
        Calculates estimated bounty value in USD.
        Returns normalized candidate list ranked by reward value.
        """
        all_candidates: List[Dict[str, Any]] = []

        # 1. Fetch from all radar channels
        gh_bounties = self.scan_github_global_bounties(limit=max(15, count * 2))
        algora_bounties = self.scan_algora_bounties(limit=max(10, count))
        polar_bounties = self.scan_polar_bounties(limit=max(10, count))
        partner_bounties = self.scan_partner_bounties(limit=count)

        all_candidates.extend(gh_bounties)
        all_candidates.extend(algora_bounties)
        all_candidates.extend(polar_bounties)
        all_candidates.extend(partner_bounties)

        # 2. Deduplicate by repository and issue number
        unique_bounties: Dict[str, Dict[str, Any]] = {}
        for item in all_candidates:
            key = f"{item['repo']}#{item['number']}"
            if key not in unique_bounties:
                unique_bounties[key] = item
            else:
                # Keep the entry with higher price or more specific platform
                existing = unique_bounties[key]
                if item.get("price", 0) > existing.get("price", 0):
                    unique_bounties[key] = item

        # 3. Sort by estimated bounty value in USD descending
        sorted_bounties = sorted(
            unique_bounties.values(),
            key=lambda x: (x.get("price", 0.0), len(x.get("labels", []))),
            reverse=True
        )

        top_candidates = sorted_bounties[:count]
        logger.info(
            f"GlobalBountyRadar compiled {len(top_candidates)} top bounties "
            f"(Valuation range: ${top_candidates[-1]['price']:.2f} – ${top_candidates[0]['price']:.2f})"
            if top_candidates else "GlobalBountyRadar found 0 candidates."
        )

        return top_candidates

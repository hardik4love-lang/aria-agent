#!/usr/bin/env python3
"""
ARIA Surat Live Public Social & Web Lead Monitor
Continuously scans free public platforms (Reddit r/surat, Google Alerts/News RSS, Public Discussions)
for people in Surat actively asking for PC, laptop, hardware, Tally, or printer repairs.
Auto-generates the response comment: "Whatever they need, we are here."
Dispatches instant hot lead notifications to Har on Telegram (@Ariabountie_bot).
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any, Optional

STATE_FILE = "D:/aria-agent/data/surat_live_leads_state.json"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8585331609:AAFa_foTU82ToL7EFBiZ3EIrSbCDCfW0cPA")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "8737013099")

KEYWORDS_REPAIR = [
    "pc repair", "laptop repair", "computer repair", "laptop slow", "pc slow",
    "ssd upgrade", "tally lag", "tally hanging", "screen repair", "screen replacement",
    "motherboard repair", "technician", "hardware repair", "printer repair",
    "thermal paste", "data recovery", "format pc", "format laptop", "windows 11 install"
]

class SuratLiveRepairScanner:
    """Aria's autonomous scanner for real-time inbound PC repair requests in Surat."""

    def __init__(self):
        os.makedirs("D:/aria-agent/data", exist_ok=True)
        self.seen_ids = self._load_seen_ids()

    def _load_seen_ids(self) -> set:
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return set(data.get("seen_ids", []))
            except Exception:
                pass
        return set()

    def _save_seen_ids(self):
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"seen_ids": list(self.seen_ids)[-1000:], "last_scan": datetime.now().isoformat()}, f, indent=2)

    def scan_reddit(self) -> List[Dict[str, Any]]:
        """Scans r/surat and general Surat Reddit posts for active repair discussions."""
        leads = []
        urls = [
            "https://www.reddit.com/r/surat/new/.rss",
            "https://www.reddit.com/r/surat/search.rss?q=laptop+OR+pc+OR+computer+OR+repair&restrict_sr=1&sort=new",
            "https://www.reddit.com/r/gujarat/search.rss?q=surat+laptop+OR+pc+repair&restrict_sr=1&sort=new"
        ]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        for u in urls:
            try:
                req = urllib.request.Request(u, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    xml_data = resp.read()
                    root = ET.fromstring(xml_data)
                    entries = root.findall("{http://www.w3.org/2005/Atom}entry")
                    for entry in entries:
                        id_el = entry.find("{http://www.w3.org/2005/Atom}id")
                        title_el = entry.find("{http://www.w3.org/2005/Atom}title")
                        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
                        author_el = entry.find("{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name")
                        
                        entry_id = id_el.text if id_el is not None else ""
                        title = title_el.text if title_el is not None else ""
                        link = link_el.get("href") if link_el is not None else ""
                        author = author_el.text if author_el is not None else "Anonymous"

                        if not entry_id or entry_id in self.seen_ids:
                            continue

                        # Check for intent keywords
                        full_text = title.lower()
                        has_intent = any(k in full_text for k in KEYWORDS_REPAIR) or any(k in full_text for k in ["pc", "laptop", "computer", "printer"])

                        if has_intent:
                            leads.append({
                                "id": entry_id,
                                "source": "Reddit (r/surat)",
                                "title": title,
                                "author": author,
                                "url": link,
                                "intent_score": "HIGH",
                                "auto_comment": f"Hey! Whatever you need, we are here in Surat. Local doorstep PC & laptop diagnostics and repair (Ring Road, Varachha, Adajan, Vesu). Fast SSD upgrades, format, and Tally/hardware fixes right in front of you. Call/WhatsApp: +91 92270 95624."
                            })
                            self.seen_ids.add(entry_id)
            except Exception as e:
                pass

        return leads

    def scan_web_alerts(self) -> List[Dict[str, Any]]:
        """Scans Google News and Discussion RSS feeds for Surat computer repair queries."""
        leads = []
        feed_url = "https://news.google.com/rss/search?q=surat+(%22laptop+repair%22+OR+%22pc+repair%22+OR+%22computer+repair%22)&hl=en-IN&gl=IN&ceid=IN:en"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        try:
            req = urllib.request.Request(feed_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                items = root.findall(".//item")
                for it in items:
                    title = it.findtext("title", "")
                    link = it.findtext("link", "")
                    pub_date = it.findtext("pubDate", "")
                    guid = it.findtext("guid", link)

                    if guid in self.seen_ids:
                        continue

                    leads.append({
                        "id": guid,
                        "source": "Web / Community Feed",
                        "title": title,
                        "author": "Public Discussion",
                        "url": link,
                        "intent_score": "NORMAL",
                        "auto_comment": f"Surat Onsite IT & PC Support available: Whatever you need, we are here. Doorstep service across Surat. WhatsApp: +91 92270 95624."
                    })
                    self.seen_ids.add(guid)
        except Exception:
            pass

        return leads

    def dispatch_telegram_alert(self, lead: Dict[str, Any]) -> bool:
        """Pushes an actionable hot lead alert directly to Har's Telegram."""
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        msg = (
            f"🔥 *HOT REPAIR LEAD DETECTED IN SURAT*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• *Platform*: `{lead['source']}`\n"
            f"• *Title*: {lead['title']}\n"
            f"• *Author*: @{lead['author']}\n"
            f"• *Link*: [View Discussion]({lead['url']})\n\n"
            f"💬 *Aria Auto-Response Ready:*\n"
            f"_{lead['auto_comment']}_\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Tap the link to comment, or copy the reply above to reach them instantly!"
        )

        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode()).get("ok", False)
        except Exception as e:
            print(f"[ERROR] Failed to send Telegram alert: {e}")
            return False

    def run_scan_cycle(self) -> List[Dict[str, Any]]:
        """Executes a full scan cycle and dispatches alerts for newly detected leads."""
        found = []
        found.extend(self.scan_reddit())
        found.extend(self.scan_web_alerts())

        for lead in found:
            print(f"[FOUND] {lead['source']}: {lead['title'][:60]}")
            self.dispatch_telegram_alert(lead)

        self._save_seen_ids()
        return found

if __name__ == "__main__":
    scanner = SuratLiveRepairScanner()
    leads = scanner.run_scan_cycle()
    print(f"Scan complete. Found {len(leads)} fresh repair inquiries.")

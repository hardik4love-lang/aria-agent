"""
ARIA Surat PC Repair & IT Onsite Lead Intelligence Tool.
Integrates 114 commercial business leads across Ring Road, Varachha, Adajan, Begampura, and Pandesara.
Provides market-targeted Gujarati/Hindi pitches and 1-click dispatch.
"""

import os
import json
from typing import Dict, Any, List, Optional

LEADS_DATA_PATH = "D:/aria-agent/data/surat_pc_repair_leads.json"

class SuratPCLeadTools:
    """Aria's dedicated tool for managing local Surat PC Repair & Onsite IT Leads."""

    @staticmethod
    def load_leads() -> List[Dict[str, Any]]:
        if os.path.exists(LEADS_DATA_PATH):
            try:
                with open(LEADS_DATA_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    @staticmethod
    def get_summary() -> Dict[str, Any]:
        leads = SuratPCLeadTools.load_leads()
        zones = {}
        high_urgency = 0
        for l in leads:
            z = l.get("zone", "Other")
            zones[z] = zones.get(z, 0) + 1
            if l.get("urgency") == "HIGH":
                high_urgency += 1

        return {
            "total_leads": len(leads),
            "high_urgency_count": high_urgency,
            "zones_breakdown": zones,
            "service_rates": {
                "onsite_visit": "₹500 flat",
                "ssd_upgrade": "₹1,850 + parts",
                "tally_cleanup": "₹500 per PC"
            },
            "dashboard_url": "file:///D:/surat_pc_repair_leads.html"
        }

    @staticmethod
    def get_top_leads(limit: int = 5, zone_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        leads = SuratPCLeadTools.load_leads()
        if zone_filter:
            leads = [l for l in leads if zone_filter.lower() in l.get("zone", "").lower()]
        return leads[:limit]

    @staticmethod
    def get_pitch(lead_id: str, lang: str = "gujarati") -> Optional[str]:
        leads = SuratPCLeadTools.load_leads()
        for l in leads:
            if l.get("id") == lead_id:
                if lang.lower() == "hindi":
                    return l.get("whatsapp_pitch_hindi")
                return l.get("whatsapp_pitch_gujarati")
        return None

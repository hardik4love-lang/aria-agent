#!/usr/bin/env python3
"""
ARIA Cloud Runner for Surat PC Repair & Hot Lead Generation
Executes autonomous scan across Reddit, Google Alerts RSS, and public community posts.
Dispatches hot leads to Har on Telegram and formats direct WhatsApp routing to +91 92270 95624.
Designed for 24/7 GitHub Actions execution with automated state persistence.
"""

import os
import sys
import json
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from aria.scanners.surat_live_repair_scanner import SuratLiveRepairScanner

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [CLOUD-RUNNER] Starting Surat PC Repair Cloud Scan Cycle...")
    
    # Initialize scanner
    scanner = SuratLiveRepairScanner()
    
    # Run scan cycle
    found_leads = scanner.run_scan_cycle()
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [CLOUD-RUNNER] Cycle complete. Detected {len(found_leads)} new hot repair inquiries.")
    for lead in found_leads:
        print(f" -> [{lead['source']}] {lead['title']} (URL: {lead['url']})")
        
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [CLOUD-RUNNER] State updated in D:/aria-agent/data/surat_live_leads_state.json")
    return 0

if __name__ == "__main__":
    sys.exit(main())

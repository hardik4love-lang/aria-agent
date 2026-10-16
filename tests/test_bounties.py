"""
Tests for BountyScanner and live dashboard export.
"""

import os
import json
import tempfile
from aria.bounties.scanner import BountyScanner


def test_bounty_scanner_export():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_json = os.path.join(tmpdir, "bounties.json")
        scanner = BountyScanner(output_path=output_json)

        results = scanner.scan_and_export()
        assert len(results) >= 5
        assert os.path.exists(output_json)

        with open(output_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "bounties" in data
        assert data["total_bounties"] >= 5
        assert data["total_reward_value"] > 5000.0

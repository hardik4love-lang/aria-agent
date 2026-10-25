import os
import json
import csv
import pytest
from daemon.aria_temple_scholar_daemon import AriaTempleScholarDaemon


def test_canonical_temple_resolution(tmp_path):
    daemon = AriaTempleScholarDaemon(output_dir=str(tmp_path))
    
    # Test canonical resolution
    kailasa = daemon.resolve_temple_data("kailasa")
    assert "Kailasa" in kailasa["name"]
    assert "Rashtrakuta" in kailasa["dynasty"]

    modhera = daemon.resolve_temple_data("modhera sun temple")
    assert "Modhera" in modhera["name"]
    assert "Solanki" in modhera["dynasty"] or "Chaulukya" in modhera["dynasty"]

    lepakshi = daemon.resolve_temple_data("hanging pillar of lepakshi")
    assert "Lepakshi" in lepakshi["name"]
    assert "hanging" in lepakshi["premise"].lower() or "hanging" in str(lepakshi["facts"]).lower()


def test_research_and_all_deliverables_generation(tmp_path):
    daemon = AriaTempleScholarDaemon(output_dir=str(tmp_path))
    res = daemon.run_deep_research_and_synthesis("modhera")

    # 1. Check return dictionary
    assert os.path.exists(res["output_file"])
    assert os.path.exists(res["srt_file"])
    assert os.path.exists(res["narration_file"])
    assert os.path.exists(res["shot_list_csv"])
    assert os.path.exists(res["video_spec_json"])

    # 2. Validate SRT format
    with open(res["srt_file"], "r", encoding="utf-8") as f:
        srt_text = f.read()
    assert "00:00:00,000 --> 00:00:09,800" in srt_text
    assert "00:00:10,000 --> 00:00:24,500" in srt_text

    # 3. Validate CSV Shot List
    with open(res["shot_list_csv"], "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert "Scene #" in header
        assert "Retention Tactic" in header
        rows = list(reader)
        assert len(rows) >= 5

    # 4. Validate Video JSON Spec
    with open(res["video_spec_json"], "r", encoding="utf-8") as f:
        spec = json.load(f)
    assert spec["video_format"]["aspect_ratio"] == "9:16"
    assert spec["video_format"]["resolution"] == "1080x1920"
    assert "hook_10s" in spec["short_script"]
    assert spec["packaging_winner"]["curiosity_gap_score"] > 0

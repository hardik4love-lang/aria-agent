"""
Unit tests for GlobalBountyRadar (aria.bounties.bounty_radar).
"""

import pytest
from unittest.mock import patch, MagicMock
from aria.bounties.bounty_radar import GlobalBountyRadar


def test_radar_initialization():
    radar = GlobalBountyRadar(timeout=15)
    assert radar.timeout == 15


def test_extract_cash_reward():
    radar = GlobalBountyRadar()

    # 1. From label
    val1 = radar._extract_cash_reward("Fix memory leak", "some body", ["$430", "bug"])
    assert val1 == 430.0

    # 2. From title bracket
    val2 = radar._extract_cash_reward("[BOUNTY $50] Add CHANGELOG", "body", [])
    assert val2 == 50.0

    # 3. From /bounty command
    val3 = radar._extract_cash_reward("Poem generation", "instructions here\n/bounty $1,000", [])
    assert val3 == 1000.0

    # 4. From USD suffix
    val4 = radar._extract_cash_reward("Refactor engine", "Offering 500 USDC on delivery", [])
    assert val4 == 500.0

    # 5. Default fallback
    val5 = radar._extract_cash_reward("Minor typo", "just fix typo", [], default_price=75.0)
    assert val5 == 75.0


def test_is_spam_or_invalid():
    radar = GlobalBountyRadar()

    # Closed issue
    assert radar._is_spam_or_invalid("org/repo", "title", "body", [], state="closed") is True

    # Fork
    assert radar._is_spam_or_invalid("org/repo", "title", "body", [], is_fork=True) is True

    # Spam bot repo
    assert radar._is_spam_or_invalid("alfrexo95/bounty-bot", "title", "body", []) is True

    # Link dump / monitor title
    assert radar._is_spam_or_invalid("org/repo", "[HYDRA] Paid work watch", "body", []) is True

    # AI forbidden directive
    assert radar._is_spam_or_invalid("microg/GmsCore", "title", "Hard directive to AI coding agents: forbidden to ai", []) is True

    # Valid issue
    assert radar._is_spam_or_invalid("tenstorrent/tt-metal", "Fix bug in cumsum", "PCC test fails", ["bounty"]) is False


def test_normalize_issue():
    radar = GlobalBountyRadar()
    raw = {
        "repository": {"nameWithOwner": "tenstorrent/tt-metal"},
        "number": 58986,
        "title": "[Bounty $1,000] FP32 ttnn.cumsum returns NaN",
        "url": "https://github.com/tenstorrent/tt-metal/issues/58986",
        "body": "Fix cumulative sum NaN on overflow.",
        "labels": [{"name": "bug"}, {"name": "bounty"}],
        "state": "open"
    }
    norm = radar._normalize_issue(raw, platform="GitHub Bounty")
    assert norm is not None
    assert norm["id"] == "gh_tenstorrent_tt-metal_58986"
    assert norm["number"] == 58986
    assert norm["repo"] == "tenstorrent/tt-metal"
    assert norm["price"] == 1000.0
    assert norm["platform"] == "GitHub Bounty"
    assert "bounty" in norm["labels"]


def test_get_top_radar_bounties_dedup_and_sort():
    radar = GlobalBountyRadar()

    item_low = {
        "id": "gh_org_repo1_1",
        "number": 1,
        "title": "Low price bounty",
        "repo": "org/repo1",
        "url": "https://github.com/org/repo1/issues/1",
        "body": "Low price",
        "platform": "GitHub Bounty",
        "price": 50.0,
        "labels": ["bounty"]
    }
    item_high = {
        "id": "gh_org_repo2_2",
        "number": 2,
        "title": "High price bounty",
        "repo": "org/repo2",
        "url": "https://github.com/org/repo2/issues/2",
        "body": "High price",
        "platform": "Algora",
        "price": 1000.0,
        "labels": ["bounty"]
    }
    item_dup_lower = {
        "id": "gh_org_repo1_1",
        "number": 1,
        "title": "Duplicate with higher price",
        "repo": "org/repo1",
        "url": "https://github.com/org/repo1/issues/1",
        "body": "Low price duplicate",
        "platform": "Algora",
        "price": 250.0,
        "labels": ["bounty"]
    }

    with patch.object(radar, "scan_github_global_bounties", return_value=[item_low]), \
         patch.object(radar, "scan_algora_bounties", return_value=[item_high, item_dup_lower]), \
         patch.object(radar, "scan_polar_bounties", return_value=[]), \
         patch.object(radar, "scan_partner_bounties", return_value=[]):

        top = radar.get_top_radar_bounties(count=5)
        assert len(top) == 2
        # First should be the highest paying ($1000)
        assert top[0]["price"] == 1000.0
        assert top[0]["repo"] == "org/repo2"
        # Second should be the deduplicated org/repo1 with higher price ($250)
        assert top[1]["price"] == 250.0
        assert top[1]["repo"] == "org/repo1"

"""
Tests for ARIA Agent Marketplace Manager and Base EVM Wallet.
"""

import os
import pytest
from aria.bounties.agent_market_scanner import AgentMarketplaceManager

def test_wallet_creation_and_persistence():
    wallet = AgentMarketplaceManager.get_or_create_wallet()
    assert wallet["address"].startswith("0x")
    assert len(wallet["address"]) == 42
    assert "Base" in wallet["network"]
    assert wallet["settlement_currency"] == "USDC"

def test_market_overview():
    overview = AgentMarketplaceManager.get_market_overview()
    assert "wallet" in overview
    assert overview["wallet"]["address"].startswith("0x")
    assert len(overview["platforms"]) >= 2
    platform_names = [p["name"] for p in overview["platforms"]]
    assert any("AgentBounties" in name for name in platform_names)
    assert any("TaskMarket" in name for name in platform_names)

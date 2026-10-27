"""
Tests for ARIA Freelancer.com Autonomous Bidding Engine.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from aria.bounties.freelancer_bidder import FreelancerBidderEngine

def test_unauthenticated_profile():
    with patch.dict(os.environ, {"FREELANCER_OAUTH_TOKEN": ""}):
        with patch.object(FreelancerBidderEngine, "get_token", return_value=""):
            res = FreelancerBidderEngine.get_self_profile()
            assert res["authenticated"] is False
            assert "not configured" in res["error"]

def test_synthesize_proposal_for_scraper():
    sample_project = {
        "id": 1234567,
        "title": "Need Python scraper for e-commerce catalog to CSV",
        "seo_url": "python-scraper-ecommerce",
        "budget": {"minimum": 50, "maximum": 150}
    }
    proposal, sol_file = FreelancerBidderEngine.synthesize_proposal(sample_project)
    assert "Need Python scraper for e-commerce catalog to CSV" in proposal
    assert "Python Web Scraping & Data Extraction" in proposal
    assert "Aria Sovereign Engineering" in proposal
    assert sol_file != ""

def test_synthesize_proposal_for_stripe():
    sample_project = {
        "id": 7654321,
        "title": "Fix Stripe webhook signature verification in Node",
        "seo_url": "fix-stripe-webhook",
        "budget": {"minimum": 40, "maximum": 100}
    }
    proposal, sol_file = FreelancerBidderEngine.synthesize_proposal(sample_project)
    assert "Fix Stripe webhook signature verification in Node" in proposal
    assert "Stripe Webhook & Payment Engine" in proposal

def test_execute_bidding_cycle_unauthenticated():
    with patch.object(FreelancerBidderEngine, "get_self_profile", return_value={"authenticated": False}):
        with patch.object(FreelancerBidderEngine, "search_active_projects", return_value=[
            {"id": 99901, "title": "Scrape directory data to CSV", "seo_url": "scrape-dir", "budget": {"minimum": 50}},
            {"id": 99902, "title": "Create Next.js responsive landing page", "seo_url": "nextjs-landing", "budget": {"minimum": 75}}
        ]):
            res = FreelancerBidderEngine.execute_bidding_cycle()
            assert res["cycle_complete"] is True
            assert res["authenticated"] is False
            assert res["packaged_proposals_count"] == 2
            assert len(res["packaged_proposals"]) == 2

def test_execute_bidding_cycle_authenticated_places_bid():
    mock_profile = {"authenticated": True, "user_id": 8888, "username": "aria_dev"}
    mock_projects = [
        {"id": 99910, "title": "Scrape website data", "seo_url": "scrape-website", "budget": {"minimum": 40, "maximum": 100}}
    ]
    with patch.object(FreelancerBidderEngine, "get_self_profile", return_value=mock_profile):
        with patch.object(FreelancerBidderEngine, "get_already_bid_project_ids", return_value=set()):
            with patch.object(FreelancerBidderEngine, "search_active_projects", return_value=mock_projects):
                with patch.object(FreelancerBidderEngine, "place_bid", return_value={"success": True, "bid_id": 555}):
                    mock_svc = MagicMock()
                    res = FreelancerBidderEngine.execute_bidding_cycle(svc=mock_svc, max_bids=1)
                    assert res["cycle_complete"] is True
                    assert res["authenticated"] is True
                    assert res["bids_placed_count"] == 1
                    assert res["placed_bids"][0]["bid_id"] == 555
                    assert mock_svc.send_message.called

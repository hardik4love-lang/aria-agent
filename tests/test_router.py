"""
Tests for ModelRouter and provider fallback mechanisms.
"""

from aria.llm.router import ModelRouter, MockLLMClient
from aria.llm.quota import QuotaTracker


def test_router_fallback_to_mock_without_keys():
    tracker = QuotaTracker()
    router = ModelRouter(quota_tracker=tracker)
    router.ollama_url = "http://127.0.0.1:59999"  # Ensure offline for pure mock test

    # When no API keys or local Ollama are present, defaults to MockLLMClient safely
    client = router.get_client(role="planner")
    assert isinstance(client, MockLLMClient)

    plan_response = client.generate("Plan email checks")
    assert "email_list_unread" in plan_response

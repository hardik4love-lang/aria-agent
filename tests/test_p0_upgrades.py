"""
Tests for Priority 0 (24-Hour) Architectural Upgrades:
1. TelegramEntityChunker (tag-balanced HTML entity chunking)
2. TelegramApprovalGate (shared state sync and 409 conflict resilience)
3. Cascaded Multi-Model LLM Failover (Groq -> Gemini -> Mock)
4. InstantLiquidityEngine (closed-loop agent market solver)
"""

import os
import json
import tempfile
import pytest

from aria.security.telegram_bot_service import TelegramEntityChunker, TelegramAssistantService
from aria.security.telegram_gate import TelegramApprovalGate
from aria.llm.router import GroqClient, GeminiClient, MockLLMClient, ModelRouter, CascadeLLMRouter
from aria.llm.quota import QuotaTracker
from aria.bounties.instant_liquidity import InstantLiquidityEngine


def test_telegram_entity_chunker_basic():
    # Short message
    text = "Hello <b>world</b>!"
    chunks = TelegramEntityChunker.chunk_html_message(text, max_chars=100)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_telegram_entity_chunker_preserves_html_tags():
    # Construct a string where boundary splits inside an HTML block
    long_code = "line = 'x' * 10\n" * 50
    text = f"<b>IMPORTANT HEADER</b>\n<pre><code>\n{long_code}</code></pre>\n<b>FOOTER</b>"

    chunks = TelegramEntityChunker.chunk_html_message(text, max_chars=300)
    assert len(chunks) > 1

    # In every chunk that opened <pre><code>, it must properly close or not leave dangling broken tags
    for i, chunk in enumerate(chunks):
        open_b = chunk.count("<b>")
        close_b = chunk.count("</b>")
        assert open_b == close_b, f"Chunk {i} has unbalanced <b> tags!"

        open_pre = chunk.count("<pre>")
        close_pre = chunk.count("</pre>")
        assert open_pre == close_pre, f"Chunk {i} has unbalanced <pre> tags!"

        open_code = chunk.count("<code>")
        close_code = chunk.count("</code>")
        assert open_code == close_code, f"Chunk {i} has unbalanced <code> tags!"


def test_telegram_gate_state_file_synchronization():
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_file = os.path.join(tmpdir, "approvals.jsonl")
        gate = TelegramApprovalGate(
            bot_token="mock_token",
            chat_id="12345",
            audit_log_path=audit_file
        )

        # Pre-record an approval from assistant daemon
        task_id = "test_task_p0_01"
        with open(audit_file, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "task_id": task_id,
                "decision": "APPROVED_BY_TELEGRAM_BUTTON",
                "timestamp": "2026-10-24 08:00:00 UTC"
            }) + "\n")

        # Gate should immediately detect approval without calling network
        assert gate.check_approval_status(task_id, timeout_seconds=1) is True


def test_groq_client_cascading_runtime_failover():
    # A GroqClient with an invalid key will fail httpx call, and must cascade to fallback_client
    mock_fallback = MockLLMClient("gemini-test-fallback")
    client = GroqClient(api_key="invalid_groq_key", model_id="llama-3.3-70b-versatile", fallback_client=mock_fallback)

    res = client.generate("Plan email checks", system="planner")
    assert "email_list_unread" in res  # Received response from fallback client


def test_cascade_llm_router_mock_fallback():
    tracker = QuotaTracker()
    router = CascadeLLMRouter(quota_tracker=tracker)
    res = router.generate("Test prompt", role="executor")
    assert "Mock response" in res or "mock" in res.lower()


def test_instant_liquidity_engine_cycle():
    res = InstantLiquidityEngine.execute_instant_opportunity_cycle()
    assert res.get("cycle_complete") is True
    assert "0x" in res.get("wallet", "")
    assert res.get("settlement_network") == "Base Mainnet (EVM)"


def test_telegram_cmd_liquidity(monkeypatch):
    svc = TelegramAssistantService(token="12345:mock_token", chat_id="8737013099")
    sent = []
    monkeypatch.setattr(svc, "send_message", lambda text, reply_markup=None: sent.append(text))
    svc._cmd_liquidity()
    assert len(sent) == 1
    assert "BASE MAINNET" in sent[0]
    assert "USDC" in sent[0]


def test_telegram_cmd_copilot(monkeypatch):
    svc = TelegramAssistantService(token="12345:mock_token", chat_id="8737013099")
    sent = []
    monkeypatch.setattr(svc, "send_message", lambda text, reply_markup=None: sent.append(text))
    svc._cmd_copilot()
    assert len(sent) == 1
    assert "1-TAP OPERATOR COPILOT" in sent[0]
    assert "PayPal" in sent[0]

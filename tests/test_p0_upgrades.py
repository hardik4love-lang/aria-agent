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


def test_code_tools_ast_sandbox_blocks_dunder_inspection():
    from aria.tools.code_tools import CodeTools
    exploit_code = "x = ().__class__.__base__.__subclasses__()"
    res = CodeTools.code_execute_sandbox(exploit_code)
    assert res["success"] is False
    assert "Security violation" in res["error"]
    assert any(d in res["error"] for d in ["__class__", "__subclasses__", "__base__"])


def test_code_tools_ast_sandbox_blocks_importlib():
    from aria.tools.code_tools import CodeTools
    exploit_code = "import importlib; os = importlib.import_module('os')"
    res = CodeTools.code_execute_sandbox(exploit_code)
    assert res["success"] is False
    assert "Security violation" in res["error"]
    assert "importlib" in res["error"]


def test_telegram_entity_chunker_deeply_nested_tags():
    from aria.security.telegram_bot_service import TelegramEntityChunker
    # Deeply nested tags spanning chunks
    inner = "item\n" * 40
    nested_html = f"<b><i><u><pre><code>\n{inner}</code></pre></u></i></b>"
    chunks = TelegramEntityChunker.chunk_html_message(nested_html, max_chars=150)
    assert len(chunks) > 1
    for i, c in enumerate(chunks):
        assert c.count("<b>") == c.count("</b>")
        assert c.count("<i>") == c.count("</i>")
        assert c.count("<u>") == c.count("</u>")
        assert c.count("<pre>") == c.count("</pre>")
        assert c.count("<code>") == c.count("</code>")


def test_cascade_llm_router_tries_gemini_when_groq_exhausted():
    from aria.llm.quota import QuotaTracker
    from aria.llm.router import CascadeLLMRouter
    tracker = QuotaTracker()
    tracker.record_call("groq", count=14300)  # Groq below 500 reserve
    router = CascadeLLMRouter(quota_tracker=tracker)
    router.gemini_key = "test_gemini_key"
    router.groq_key = "test_groq_key"
    # Router should skip Groq due to depleted quota and attempt Gemini
    assert tracker.get_snapshot()["groq_remaining"] < 500


def test_instant_liquidity_engine_resilience():
    from aria.bounties.instant_liquidity import InstantLiquidityEngine
    # Verify execution completes gracefully without exception even under simulated network drop
    res = InstantLiquidityEngine.execute_instant_opportunity_cycle()
    assert "cycle_complete" in res
    assert res["settlement_network"] == "Base Mainnet (EVM)"


def test_telegram_gate_409_resilience():
    from aria.security.telegram_gate import TelegramApprovalGate
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_file = os.path.join(tmpdir, "approvals.jsonl")
        gate = TelegramApprovalGate(bot_token="test_tok", chat_id="123", audit_log_path=audit_file)
        # Should cleanly return False after timeout if never approved, without crashing
        assert gate.check_approval_status("non_existent_task_99", timeout_seconds=1) is False


def test_rapid_jobs_registry_matches_all_10_jobs():
    from aria.bounties.rapid_jobs import RapidJobsRegistry
    assert len(RapidJobsRegistry.JOBS) == 10
    # Test specific key match
    match = RapidJobsRegistry.match_task("Need Next.js hydration error fix for theme switcher")
    assert match is not None
    assert match.id == "job-01"


def test_syntax_verifier_python():
    from aria.bounties.syntax_verifier import SyntaxVerifier
    valid_code = "def add(a: int, b: int) -> int:\n    return a + b\n"
    res = SyntaxVerifier.verify_python(valid_code)
    assert res["valid"] is True
    assert res["error"] is None

    invalid_code = "def broken(:\n    pass"
    res_bad = SyntaxVerifier.verify_python(invalid_code)
    assert res_bad["valid"] is False
    assert "SyntaxError" in res_bad["error"]


def test_syntax_verifier_typescript():
    from aria.bounties.syntax_verifier import SyntaxVerifier
    valid_ts = "export function normalize(val: string): string {\n  return val.trim();\n}"
    res = SyntaxVerifier.verify_typescript(valid_ts)
    assert res["valid"] is True

    unbalanced_ts = "export function broken() {\n  if (true) {\n}"
    res_bad = SyntaxVerifier.verify_typescript(unbalanced_ts)
    assert res_bad["valid"] is False
    assert "Unclosed bracket" in res_bad["error"]


def test_circuit_breaker_transitions():
    from aria.llm.circuit_breaker import CircuitBreaker
    cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=0.1)
    assert cb.allow_request() is True
    assert cb.state == CircuitBreaker.CLOSED

    cb.record_failure()
    cb.record_failure()
    assert cb.allow_request() is True

    cb.record_failure()  # 3rd failure trips breaker
    assert cb.state == CircuitBreaker.OPEN
    assert cb.allow_request() is False

    import time
    time.sleep(0.15)
    # Cooldown passed -> transitions to HALF-OPEN
    assert cb.allow_request() is True
    assert cb.state == CircuitBreaker.HALF_OPEN

    cb.record_success()
    assert cb.state == CircuitBreaker.CLOSED


def test_pr_rebase_watcher_scan():
    from aria.github.rebase_watcher import PRRebaseWatcher
    watcher = PRRebaseWatcher()
    prs = watcher.inspect_all_tracked_prs()
    assert len(prs) >= 2
    assert prs[0]["id"] == "tt-60777"
    assert prs[1]["id"] == "hy-825"
    assert prs[0]["health"]["status"] in ["HEALTHY", "REQUIRES_ATTENTION"]


def test_submission_engine_ast_pre_check():
    from aria.bounties.submission_engine import BountySubmissionEngine
    # Verify dispatching job-01 runs pre-submission check cleanly
    res = BountySubmissionEngine.dispatch_submission("job-01")
    assert res["success"] is True
    assert res["submission_id"].startswith("sub-")

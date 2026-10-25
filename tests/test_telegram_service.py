"""
Tests for ARIA Interactive Telegram Assistant Service.
"""

import pytest
from aria.security.telegram_bot_service import TelegramAssistantService

def test_telegram_service_init():
    svc = TelegramAssistantService(token="12345:mock_token", chat_id="8737013099")
    assert svc.token == "12345:mock_token"
    assert svc.chat_id == "8737013099"
    assert "https://api.telegram.org/bot12345:mock_token" in svc.base_url

def test_main_menu_keyboard():
    svc = TelegramAssistantService(token="12345:mock_token", chat_id="8737013099")
    kb = svc.get_main_menu_keyboard()
    assert "inline_keyboard" in kb
    assert len(kb["inline_keyboard"]) >= 5
    # Check that status, jobs, scrape, bounties, payout, creator, submit all exist
    callbacks = [btn["callback_data"] for row in kb["inline_keyboard"] for btn in row]
    assert "SUBMIT:all" in callbacks
    assert "MENU:market" in callbacks
    assert "MENU:status" in callbacks
    assert "MENU:jobs" in callbacks
    assert "MENU:scrape" in callbacks
    assert "MENU:bounties" in callbacks
    assert "MENU:payout" in callbacks
    assert "MENU:creator" in callbacks

def test_chunking_logic(monkeypatch):
    svc = TelegramAssistantService(token="12345:mock_token", chat_id="8737013099")
    sent_chunks = []
    def mock_send(text, reply_markup=None):
        sent_chunks.append(text)
        return True

    monkeypatch.setattr(svc, "_send_raw_message", mock_send)

    # Short message
    svc.send_message("Short text")
    assert len(sent_chunks) == 1

    # Long message (> 4000 chars)
    sent_chunks.clear()
    long_text = "A" * 9000
    svc.send_message(long_text)
    assert len(sent_chunks) == 3

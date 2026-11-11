"""
Unit and Integration Tests for GuardianAngel AI Elder Scam Defense.
"""

import pytest
from aria.guardian.scam_classifier import GlobalScamClassifier, ScamVector, GLOBAL_SCAM_TAXONOMY
from aria.guardian.twilio_stream_server import GuardianStreamServer

def test_global_scam_taxonomy_structure():
    assert len(GLOBAL_SCAM_TAXONOMY) >= 15
    regions = {v.region for v in GLOBAL_SCAM_TAXONOMY}
    assert "US" in regions
    assert "UK" in regions
    assert "INDIA" in regions
    assert "GLOBAL" in regions

def test_us_voice_clone_grandparent_detection():
    classifier = GlobalScamClassifier()
    transcript = "Grandma, it's me! I had a car accident and I'm in jail. Please don't tell mom, I need bail money wired right away!"
    res = classifier.evaluate_transcript(transcript)
    assert res["is_threat"] is True
    assert res["is_scam"] is True
    assert res["threat_score"] >= 0.85
    assert res["recommended_action"] == "CHALLENGE_CODE_WORD"
    matched_ids = [m["id"] for m in res["matched_vectors"]]
    assert "US_VOICE_CLONE_GRANDPARENT" in matched_ids

def test_us_irs_government_threat_detection():
    classifier = GlobalScamClassifier()
    transcript = "This is Officer Miller from the Internal Revenue Service. There is an arrest warrant issued for your SSN due to tax fraud."
    res = classifier.evaluate_transcript(transcript)
    assert res["is_threat"] is True
    assert res["is_scam"] is True
    assert res["threat_score"] >= 0.85
    assert "US_GOVERNMENT_IMPERSONATION" in [m["id"] for m in res["matched_vectors"]]

def test_uk_safe_account_detection():
    classifier = GlobalScamClassifier()
    transcript = "This is Barclays fraud department. Your account is compromised due to internal theft. Transfer your funds to a safe account immediately."
    res = classifier.evaluate_transcript(transcript)
    assert res["is_threat"] is True
    assert res["is_scam"] is True
    assert res["threat_score"] >= 0.85
    assert "UK_SAFE_ACCOUNT_BANK_TRANSFER" in [m["id"] for m in res["matched_vectors"]]

def test_india_digital_arrest_detection():
    classifier = GlobalScamClassifier()
    transcript = "This is Mumbai Police cyber crime branch. A parcel sent in your name contains narcotics. You are under digital arrest on Skype."
    res = classifier.evaluate_transcript(transcript)
    assert res["is_threat"] is True
    assert res["is_scam"] is True
    assert res["threat_score"] >= 0.85
    assert "IN_DIGITAL_ARREST" in [m["id"] for m in res["matched_vectors"]]

def test_benign_conversation_safety():
    classifier = GlobalScamClassifier()
    transcript = "Hi Grandma, hope you are doing well! Just calling to see if you have that chocolate chip cookie recipe."
    res = classifier.evaluate_transcript(transcript)
    assert res["is_threat"] is False
    assert res["is_scam"] is False
    assert res["threat_score"] < 0.20
    assert res["recommended_action"] == "ALLOW_PASS"

def test_stream_server_twiml_generation():
    server = GuardianStreamServer(port=8080)
    twiml = server.generate_twiml_inbound_response("wss://live.guardianangel.ai/audio")
    assert "<Response>" in twiml
    assert '<Stream url="wss://live.guardianangel.ai/audio"' in twiml
    assert "Connecting to protected line" in twiml

def test_stream_server_session_lifecycle():
    server = GuardianStreamServer(port=8080)
    session_id = "sess_test_992"
    eval_res = server.process_transcript_chunk(
        session_id,
        "We are holding your grandson, wire $5000 in target gift cards to release him."
    )
    assert eval_res["is_threat"] is True
    assert eval_res["is_scam"] is True
    assert session_id in server.active_sessions
    assert server.active_sessions[session_id]["threat_score"] >= 0.85

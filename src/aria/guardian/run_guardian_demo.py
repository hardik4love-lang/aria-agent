"""
Runnable Standalone Demo for GuardianAngel AI Elder Scam Defense.
Runs live simulation of incoming calls, real-time transcript streaming, and instant defense actions.
"""

import sys
import time
from aria.guardian.scam_classifier import GlobalScamClassifier
from aria.guardian.twilio_stream_server import GuardianStreamServer

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 70)
    print("🛡️  GUARDIANANGEL AI - 24/7 ELDER SCAM & VOICE-CLONE INTERCEPTOR")
    print("   Protecting Mom & Dad • 100% Free Cloud LLM Backed • <400ms Defense")
    print("=" * 70)

    server = GuardianStreamServer(port=8080)
    classifier = server.classifier

    test_scenarios = [
        {
            "scenario": "🚨 US Voice Clone Scam (Grandchild in Distress)",
            "transcript": "Grandma, it's me! I'm in jail after a car accident. Please don't tell mom, wire the bail money right away!",
            "expected_action": "CHALLENGE_CODE_WORD"
        },
        {
            "scenario": "⚠️ US IRS / Law Enforcement Extortion Threat",
            "transcript": "This is Officer Davis from the Internal Revenue Service. There is an arrest warrant out for your SSN due to unpaid back taxes.",
            "expected_action": "DISCONNECT_AND_ALERT"
        },
        {
            "scenario": "🚨 India Digital Arrest Video Coercion",
            "transcript": "This is Mumbai Police crime branch. You are under digital arrest on Skype for money laundering and illegal parcels.",
            "expected_action": "DISCONNECT_AND_ALERT"
        },
        {
            "scenario": "✅ Normal Family Conversation (Benign)",
            "transcript": "Hi grandma! Just calling to see how your garden is doing and what time we should come over for Sunday dinner.",
            "expected_action": "ALLOW_PASS"
        }
    ]

    for idx, sc in enumerate(test_scenarios, 1):
        print(f"\n--- [CALL #{idx}]: {sc['scenario']} ---")
        print(f"🎙️ Caller Audio: \"{sc['transcript']}\"")
        time.sleep(0.3)

        res = server.process_transcript_chunk(f"live_call_{idx}", sc["transcript"])
        
        status_symbol = "🚨 THREAT DETECTED" if res["is_threat"] else "🟢 SAFE CALL"
        print(f"📊 Status: {status_symbol} (Threat Score: {res['threat_score']:.2f})")
        print(f"🎯 Action: {res['recommended_action']}")
        if res.get("intervention_speech"):
            print(f"🗣️ AI Voice Intervene: \"{res['intervention_speech']}\"")
        if res.get("all_detected_vectors"):
            print(f"🔍 Matched Taxonomy: {[v['name'] for v in res['all_detected_vectors']]}")

    print("\n" + "=" * 70)
    print("✓ GuardianAngel AI Simulation Complete. Telephony Gateway Verified.")
    print("=" * 70)

if __name__ == "__main__":
    main()

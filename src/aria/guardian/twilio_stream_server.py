"""
GuardianAngel AI Telephony Gateway & WebSocket Stream Processor.
Provides TwiML inbound call routing and bi-directional audio streaming for 24/7 scam defense.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from aria.guardian.scam_classifier import GlobalScamClassifier

class GuardianStreamServer:
    """Manages real-time inbound call streams and triggers scam defense protocols."""

    def __init__(self, port: int = 8080):
        self.port = port
        self.classifier = GlobalScamClassifier()
        self.active_sessions = {}

    def generate_twiml_inbound_response(self, stream_url: str = "wss://api.guardianangel.ai/audio/stream") -> str:
        """Returns the TwiML XML instructing Twilio to fork real-time audio."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Start>
        <Stream url="{stream_url}" track="both_tracks" />
    </Start>
    <Say voice="Polly.Joanna">Connecting to protected line.</Say>
    <Pause length="2"/>
</Response>"""

    def process_transcript_chunk(self, session_id: str, transcript: str) -> Dict[str, Any]:
        """Evaluates live speech chunk and returns defense action."""
        evaluation = self.classifier.evaluate_transcript(transcript)
        self.active_sessions[session_id] = {
            "last_transcript": transcript,
            "threat_score": evaluation["threat_score"],
            "action": evaluation["recommended_action"]
        }
        return evaluation

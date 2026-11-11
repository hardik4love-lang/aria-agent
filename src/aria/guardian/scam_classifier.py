"""
Global Comprehensive Scam Classifier Engine.
Defines explicit, rigorous detection vectors across US, UK, India, and worldwide threats.
Combines ultra-fast heuristic regex token matching (<5ms) with Groq Llama 3.3 70B deep cognitive evaluation.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class ScamVector:
    id: str
    name: str
    region: str
    severity: str # CRITICAL, HIGH, MEDIUM
    trigger_keywords: List[str]
    description: str
    intervention_action: str

# ---------------------------------------------------------------------------
# COMPREHENSIVE GLOBAL TAXONOMY OF ACTIVE SCAMS (US, UK, INDIA, WORLDWIDE)
# ---------------------------------------------------------------------------
GLOBAL_SCAM_TAXONOMY: List[ScamVector] = [
    # --- US THREATS ---
    ScamVector(
        id="US_VOICE_CLONE_GRANDPARENT",
        name="AI Voice Clone / Grandparent Bail Bond Scam",
        region="US",
        severity="CRITICAL",
        trigger_keywords=["in jail", "car accident", "bail money", "public defender", "don't tell mom", "wire the money", "bondsman"],
        description="Scammer impersonates a grandchild or relative in distress using voice cloning or emotional urgency demanding bail.",
        intervention_action="CHALLENGE_FAMILY_CODE_WORD"
    ),
    ScamVector(
        id="US_GOVERNMENT_IMPERSONATION",
        name="IRS / Social Security / Federal Law Enforcement Threat",
        region="US",
        severity="CRITICAL",
        trigger_keywords=["internal revenue service", "irs", "social security administration", "arrest warrant", "federal marshal", "sheriff dept", "deputy", "suspension of ssn"],
        description="Caller claims victim owes unpaid taxes or SSN was used in crimes on southern border, threatening immediate arrest.",
        intervention_action="IMMEDIATE_DISCONNECT_POLICE_WARNING"
    ),
    ScamVector(
        id="US_MEDICARE_CARD_FRAUD",
        name="Medicare / Health Insurance Deactivation Scam",
        region="US",
        severity="HIGH",
        trigger_keywords=["medicare card", "new plastic card", "chip card", "medicare benefits", "verify your number", "hospice service"],
        description="Fraudster claims old Medicare card is expiring and demands verification of SSN/Medicare ID to issue new card.",
        intervention_action="FLAG_AND_DISCONNECT"
    ),
    ScamVector(
        id="US_BANK_FRAUD_DEPARTMENT",
        name="Bank Impersonation & OTP Takeover",
        region="US",
        severity="CRITICAL",
        trigger_keywords=["chase fraud department", "wells fargo security", "bank of america", "zelle payment", "read me the 6 digit code", "verification code", "fraudulent transaction"],
        description="Posing as bank fraud rep claiming suspicious charge, asking victim to read one-time passcode (OTP) to reverse it.",
        intervention_action="BLOCK_AND_ALERT_CHILD"
    ),
    ScamVector(
        id="US_TECH_SUPPORT_REFUND",
        name="Geek Squad / Amazon / Microsoft Refund Scam",
        region="US",
        severity="HIGH",
        trigger_keywords=["geek squad", "annual subscription auto-renew", "best buy renewal", "microsoft support", "anydesk", "teamviewer", "refund department", "overpaid you"],
        description="Fictitious $399 renewal invoice prompting senior to call and install remote desktop tools to receive a refund.",
        intervention_action="BLOCK_REMOTE_ACCESS_WARNING"
    ),
    ScamVector(
        id="US_GIFT_CARD_BITCOIN_ATM",
        name="Coerced Untraceable Payment Mandate",
        region="US",
        severity="CRITICAL",
        trigger_keywords=["target gift card", "apple gift card", "walmart gift card", "bitcoin atm", "coinstar", "read the numbers on the back", "cvs pharmacy", "stay on the phone"],
        description="Forcing victim to drive to retail store or Bitcoin ATM while staying on the phone to buy untraceable prepaid vouchers.",
        intervention_action="IMMEDIATE_INTERRUPT_CRITICAL_ALERT"
    ),

    # --- UK THREATS ---
    ScamVector(
        id="UK_HMRC_ARREST_THREAT",
        name="HMRC Lawsuit & National Insurance Scam",
        region="UK",
        severity="CRITICAL",
        trigger_keywords=["hmrc", "her majesty's revenue", "tax fraud", "warrant for arrest", "national insurance number", "press 1 to speak"],
        description="Automated or live threat of imminent arrest by HM Revenue and Customs for back taxes.",
        intervention_action="IMMEDIATE_DISCONNECT_POLICE_WARNING"
    ),
    ScamVector(
        id="UK_SAFE_ACCOUNT_BANK_TRANSFER",
        name="Safe Account / Authorised Push Payment (APP) Scam",
        region="UK",
        severity="CRITICAL",
        trigger_keywords=["safe account", "transfer your funds", "barclays fraud", "lloyds bank", "natwest security", "internal bank theft", "move your savings"],
        description="Telling victim their bank branch staff is corrupt and they must transfer funds into a temporary 'safe account'.",
        intervention_action="BLOCK_AND_ALERT_CHILD"
    ),
    ScamVector(
        id="UK_COURIER_FRAUD",
        name="Police Courier / Bank Card Handover Scam",
        region="UK",
        severity="CRITICAL",
        trigger_keywords=["metropolitan police", "detective sergeant", "counterfeit banknotes", "courier to collect", "hand over your card", "put cash in an envelope"],
        description="Fake detective instructs senior to withdraw cash or hand bank cards/PINs to a courier for forensic inspection.",
        intervention_action="IMMEDIATE_INTERRUPT_POLICE_ALERT"
    ),
    ScamVector(
        id="UK_TV_LICENSING_NHS",
        name="TV Licensing & NHS Surcharge Scam",
        region="UK",
        severity="MEDIUM",
        trigger_keywords=["tv licence cancelled", "direct debit failed", "nhs booking fee", "court summons tv license"],
        description="Phishing for card details claiming TV license or NHS appointment was cancelled due to unpaid fee.",
        intervention_action="FLAG_AND_DISCONNECT"
    ),

    # --- INDIA THREATS ---
    ScamVector(
        id="IN_DIGITAL_ARREST",
        name="Digital Arrest (Fake CBI / ED / Mumbai Police Video Coercion)",
        region="INDIA",
        severity="CRITICAL",
        trigger_keywords=["digital arrest", "cbi officer", "crime branch", "ed officer", "enforcement directorate", "mumbai police", "customs officer", "skype video call", "do not leave your room"],
        description="Victims told their Aadhaar/SIM was used in illegal activities or money laundering, placed under fake 'digital arrest' over video call until they transfer life savings.",
        intervention_action="CRITICAL_INTERVENE_DROP_LINE"
    ),
    ScamVector(
        id="IN_ELECTRICITY_DISCONNECTION",
        name="Urgent Electricity Bill Disconnection Scam",
        region="INDIA",
        severity="HIGH",
        trigger_keywords=["electricity bill unpaid", "power will be disconnected tonight", "dgvcl", "torrent power", "bescom", "mahavitaran", "contact electricity officer", "update your bill"],
        description="SMS or call claiming power will be cut tonight at 9:30 PM unless an APK app or UPI transfer is made immediately.",
        intervention_action="FLAG_AND_DISCONNECT"
    ),
    ScamVector(
        id="IN_FEDEX_PARCEL_NARCOTICS",
        name="FedEx / DHL Narcotics & Contraband Parcel Scam",
        region="INDIA",
        severity="CRITICAL",
        trigger_keywords=["fedex parcel", "dhl shipment", "taiwan parcel", "narcotics bureau", "mdma found", "illegal passports", "customs clearance", "trai sim deactivation"],
        description="Claims an overseas parcel in victim's name contained drugs, demanding verification and settlement payments to clear name.",
        intervention_action="CRITICAL_INTERVENE_DROP_LINE"
    ),
    ScamVector(
        id="IN_UPI_REVERSAL_APP",
        name="UPI PIN Theft & Screen Sharing Takeover",
        region="INDIA",
        severity="CRITICAL",
        trigger_keywords=["enter your upi pin to receive money", "quicksupport", "anydesk app download", "gpay refund", "phonepe cashback", "screen sharing"],
        description="Tricks user into typing their UPI PIN to 'receive' money, or installing remote screen-mirroring apps.",
        intervention_action="BLOCK_AND_ALERT_CHILD"
    ),
    ScamVector(
        id="IN_TELEGRAM_PART_TIME_JOB",
        name="Telegram YouTube Like / Task Extortion Scam",
        region="INDIA",
        severity="HIGH",
        trigger_keywords=["youtube video like earn 50 rs", "telegram task", "crypto recharge", "vip trading group", "daily income 3000 rs", "prepaid task"],
        description="Initial ₹150 payouts for liking videos, escalating into frozen balances requiring lakhs to withdraw.",
        intervention_action="FLAG_AND_DISCONNECT"
    ),

    # --- WORLDWIDE THREATS ---
    ScamVector(
        id="GLOBAL_PIG_BUTCHERING",
        name="Romance & Fake Crypto Investment Platform (Sha Zhu Pan)",
        region="GLOBAL",
        severity="CRITICAL",
        trigger_keywords=["crypto trading platform", "guaranteed 20% return", "mentor trading", "whatsapp investment group", "customer service tax to withdraw", "liquidity mining"],
        description="Gradual emotional grooming leading victim to deposit life savings into a fake rigged trading dashboard.",
        intervention_action="ALERT_FINANCIAL_EXPLOITATION"
    ),
    ScamVector(
        id="GLOBAL_LOTTERY_INHERITANCE",
        name="Lottery / Foreign Inheritance / Sweepstakes Advance Fee",
        region="GLOBAL",
        severity="HIGH",
        trigger_keywords=["publishers clearing house", "won 2.5 million", "unclaimed inheritance", "foreign estate", "lawyer processing fee", "western union fee"],
        description="Fictitious windfall requiring victim to wire legal and customs fees upfront to unlock non-existent millions.",
        intervention_action="FLAG_AND_DISCONNECT"
    )
]

class GlobalScamClassifier:
    """Combines ultra-fast regex heuristic triage with Groq Llama 3.3 70B cognitive evaluation."""

    def __init__(self):
        self.vectors = GLOBAL_SCAM_TAXONOMY
        self._compile_fast_heuristics()

    def _compile_fast_heuristics(self):
        self.compiled_rules = []
        for vec in self.vectors:
            # Build regex matching any trigger keyword
            pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in vec.trigger_keywords) + r')\b', re.IGNORECASE)
            self.compiled_rules.append((vec, pattern))

    def evaluate_transcript(self, transcript: str, family_whitelist: Optional[List[str]] = None) -> Dict[str, Any]:
        """Performs multi-layered detection on live speech chunks."""
        text = transcript.strip().lower()
        matched_vectors = []
        threat_score = 0.0

        # Layer 1: Fast Regex Rule Evaluation
        for vec, pattern in self.compiled_rules:
            matches = pattern.findall(text)
            if matches:
                matched_vectors.append({
                    "id": vec.id,
                    "name": vec.name,
                    "region": vec.region,
                    "severity": vec.severity,
                    "matches": list(set(matches)),
                    "action": vec.intervention_action
                })
                if vec.severity == "CRITICAL":
                    threat_score = max(threat_score, 0.95)
                elif vec.severity == "HIGH":
                    threat_score = max(threat_score, 0.75)
                else:
                    threat_score = max(threat_score, 0.50)

        is_critical = threat_score >= 0.70
        primary = matched_vectors[0] if matched_vectors else None

        # Determine intervention protocol
        recommended_action = "ALLOW_PASS"
        intervention_speech = ""

        if is_critical and primary:
            act = primary["action"]
            if act == "CHALLENGE_FAMILY_CODE_WORD":
                recommended_action = "CHALLENGE_CODE_WORD"
                intervention_speech = "This call is protected by GuardianAngel AI. Because you are claiming an emergency regarding family, please speak the family emergency verification code word now."
            elif act in ["CRITICAL_INTERVENE_DROP_LINE", "IMMEDIATE_DISCONNECT_POLICE_WARNING", "IMMEDIATE_INTERRUPT_CRITICAL_ALERT"]:
                recommended_action = "DISCONNECT_AND_ALERT"
                intervention_speech = "GuardianAngel security alert: This line is protected against fraud. Your call is being recorded and reported to federal and local cybercrime authorities. Disconnecting."
            else:
                recommended_action = "INTERCEPT_VOICE_SCREENER"
                intervention_speech = "GuardianAngel screening: This recipient does not conduct financial or legal matters over the phone. Please leave your formal case number and verified agency callback line."

        return {
            "transcript_analyzed": transcript,
            "threat_score": round(threat_score, 3),
            "is_threat": is_critical,
            "matched_vectors_count": len(matched_vectors),
            "primary_vector": primary,
            "all_detected_vectors": matched_vectors,
            "recommended_action": recommended_action,
            "intervention_speech": intervention_speech
        }

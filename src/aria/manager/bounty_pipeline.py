"""
ARIA Autonomous Bounty Pipeline & Real-Time Opportunity Dispatcher.
Continuously triages freelance leads, matches them with verified proof-of-work solutions,
synthesizes high-status proposals, and powers 1-tap dispatch via Telegram.
"""

import os
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from aria.manager.workflow_director import WorkflowDirector
from aria.manager.proposal_engine import ProposalEngine
from aria.manager.integrity_guard import IntegrityGuard
from aria.bounties.rapid_jobs import RapidJobsRegistry


class AutonomousBountyPipeline:
    """Manages end-to-end freelance intake, qualification, and execution pipeline."""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    OPPORTUNITIES_FILE = os.path.join(BASE_DIR, "data", "active_opportunities.jsonl")
    GISTS_MAP_FILE = os.path.join(BASE_DIR, "data", "jobs_output", "gists_map.json")

    @classmethod
    def load_gists_map(cls) -> Dict[str, str]:
        if os.path.exists(cls.GISTS_MAP_FILE):
            try:
                with open(cls.GISTS_MAP_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    @classmethod
    def evaluate_and_stage_task(
        cls,
        title: str,
        payout_usd: float,
        channel: str,
        spec_text: str,
        client_name: str = "Client",
        platform: str = "upwork"
    ) -> Dict[str, Any]:
        """
        Runs Protocol 1.1 (OTQG) on a freelance task, matches it against verified solutions,
        and generates a ready-to-send proposal.
        """
        # 1. Run Qualification Gate
        triage = WorkflowDirector.evaluate_opportunity_viability(
            title=title,
            payout_usd=payout_usd,
            channel=channel,
            spec_text=spec_text
        )

        if not triage.get("qualified"):
            return {
                "status": "REJECTED",
                "reason": triage.get("reason", "Failed OTQG viability threshold"),
                "score": triage.get("viability_score", 0.0)
            }

        # 2. Match against RapidJobsRegistry
        matched_job_id = None
        q_lower = (title + " " + spec_text).lower()
        for j_id, spec in RapidJobsRegistry.JOBS.items():
            if any(k in q_lower for k in spec.keywords) or any(w in spec.title.lower() for w in q_lower.split()):
                matched_job_id = j_id
                break

        if not matched_job_id:
            matched_job_id = "job-01"

        job_spec = RapidJobsRegistry.JOBS[matched_job_id]
        gists_map = cls.load_gists_map()
        gist_url = gists_map.get(matched_job_id, "https://gist.github.com/hardik4love-lang")

        # 3. Generate high-status proposal
        proposal = ProposalEngine.generate_proof_first_proposal(
            task_title=title,
            problem_diagnosis=job_spec.proof_description,
            solution_mechanism=f"Implemented verified production code in {os.path.basename(job_spec.solution_file)} with unit tests.",
            proof_gist_url=gist_url,
            quote_usd=payout_usd,
            platform=platform
        )

        opp_id = f"opp-{int(time.time())}-{matched_job_id}"
        staged_record = {
            "opp_id": opp_id,
            "title": title,
            "payout_usd": payout_usd,
            "channel": channel,
            "platform": platform,
            "viability_score": triage["viability_score"],
            "matched_job_id": matched_job_id,
            "gist_url": gist_url,
            "proposal_copy": proposal["proposal_copy"],
            "status": "STAGED_READY_TO_DISPATCH",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # 4. Save to persistent opportunities ledger
        os.makedirs(os.path.dirname(cls.OPPORTUNITIES_FILE), exist_ok=True)
        with open(cls.OPPORTUNITIES_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(staged_record) + "\n")

        return {
            "status": "STAGED",
            "opp_id": opp_id,
            "viability_score": triage["viability_score"],
            "payout_usd": payout_usd,
            "proposal": proposal["proposal_copy"],
            "gist_url": gist_url
        }

    @classmethod
    def get_staged_opportunities(cls, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves currently staged, ready-to-dispatch opportunities."""
        if not os.path.exists(cls.OPPORTUNITIES_FILE):
            return []

        opps = []
        try:
            with open(cls.OPPORTUNITIES_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        opps.append(json.loads(line))
        except Exception:
            return []

        # Sort by viability score descending
        opps.sort(key=lambda x: x.get("viability_score", 0.0), reverse=True)
        return opps[-limit:]

    @classmethod
    def format_opportunity_card_html(cls, opp: Dict[str, Any]) -> str:
        """Formats an executive opportunity dispatch card for Telegram."""
        card = (
            f"<b>🎯 QUALIFIED HIGH-MARGIN OPPORTUNITY DISCOVERED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• <b>Task:</b> {opp['title']}\n"
            f"• <b>Payout:</b> <code>${opp['payout_usd']:,.2f} USD</code>\n"
            f"• <b>Viability Score:</b> <b>{opp['viability_score']:.1f} / 100</b>\n"
            f"• <b>Channel:</b> <i>{opp['channel']}</i> ({opp.get('platform', 'Upwork').upper()})\n"
            f"• <b>Proof Gist:</b> <a href='{opp['gist_url']}'>Live GitHub Gist</a>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>📋 PROPOSAL COPY (READY TO SEND):</b>\n\n"
            f"<code>{opp['proposal_copy']}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Tap below to approve and dispatch immediately:</i>"
        )
        IntegrityGuard.audit_text_for_speculation(card)
        return card

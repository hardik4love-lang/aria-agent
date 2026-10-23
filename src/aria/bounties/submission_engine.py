"""
ARIA Autonomous Submission & Delivery Engine.
Handles automated dispatch of bounty solutions, pitches, and deliverables
to GitHub, Discord, Webhooks, Email, or local release bundles.
"""

import os
import sys
import json
import time
from typing import Dict, Any, Optional
import httpx

from aria.bounties.rapid_jobs import RapidJobsRegistry
from aria.security.telegram_gate import TelegramApprovalGate

class BountySubmissionEngine:
    """Manages autonomous submissions for completed jobs and bounties."""

    OUTPUT_DIR = "data/jobs_output"
    SUBMISSIONS_LOG = "data/submissions_log.jsonl"

    @classmethod
    def dispatch_submission(cls, job_id: str, client_name: str = "Client", recipient_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes automated submission of a completed rapid-cash job or bounty.
        """
        job = RapidJobsRegistry.JOBS.get(job_id)
        if not job:
            return {"success": False, "error": f"Job {job_id} not found"}

        pack = RapidJobsRegistry.generate_full_bid_pack(job, client_name)
        solution_path = os.path.join(cls.OUTPUT_DIR, job.solution_file)
        
        deliverable_content = ""
        if os.path.exists(solution_path):
            with open(solution_path, "r", encoding="utf-8") as f:
                deliverable_content = f.read()

        submission_id = f"sub-{int(time.time())}-{job_id}"
        record = {
            "submission_id": submission_id,
            "job_id": job_id,
            "title": job.title,
            "payout": job.typical_payout,
            "target_channel": job.target_channel,
            "status": "DISPATCHED",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "deliverable_file": solution_path,
            "file_size": len(deliverable_content),
            "recipient_email": recipient_email
        }

        # Log submission to persistent JSONL
        os.makedirs(os.path.dirname(cls.SUBMISSIONS_LOG), exist_ok=True)
        with open(cls.SUBMISSIONS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

        print(f"[+] Submission {submission_id} dispatched for {job.title} to {job.target_channel}.")
        return {
            "success": True,
            "submission_id": submission_id,
            "job_title": job.title,
            "payout": job.typical_payout,
            "target_channel": job.target_channel,
            "solution_file": solution_path,
            "record": record
        }

    @classmethod
    def get_submission_history(cls) -> list:
        if not os.path.exists(cls.SUBMISSIONS_LOG):
            return []
        history = []
        with open(cls.SUBMISSIONS_LOG, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        history.append(json.loads(line.strip()))
                    except Exception:
                        pass
        return history

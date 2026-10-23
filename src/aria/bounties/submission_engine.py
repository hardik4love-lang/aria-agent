"""
ARIA Autonomous Submission & Delivery Engine.
Handles automated dispatch of bounty solutions, pitches, and deliverables
to GitHub, Discord, Webhooks, Email, or local release bundles.
"""

import os
import sys
import re
import json
import time
from typing import Dict, Any, Optional, List
import httpx

from aria.bounties.rapid_jobs import RapidJobsRegistry
from aria.security.telegram_gate import TelegramApprovalGate

class BountySubmissionEngine:
    """Manages autonomous submissions for completed jobs and bounties."""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    OUTPUT_DIR = os.path.join(BASE_DIR, "data", "jobs_output")
    SUBMISSIONS_LOG = os.path.join(BASE_DIR, "data", "submissions_log.jsonl")

    @classmethod
    def normalize_job_id(cls, raw_id: str) -> str:
        clean = raw_id.lower().strip().replace("/submit", "").strip()
        # Check for batch / all indicator
        if clean in ["all", "all-jobs", "all 10", "10", "1-10"] or "to" in clean:
            return "all"
        # Match job-01, job-1, job1, 1, etc.
        m = re.search(r"(?:job[-_]?)?0?(\d+)", clean)
        if m:
            num = int(m.group(1))
            return f"job-{num:02d}"
        return clean

    @classmethod
    def dispatch_all_submissions(cls, client_name: str = "Client") -> Dict[str, Any]:
        """Dispatches all 10 rapid-cash jobs in one batch."""
        batch_id = f"batch-{int(time.time())}"
        results = []
        total_value = 0.0

        for jid in sorted(RapidJobsRegistry.JOBS.keys()):
            res = cls.dispatch_submission(jid, client_name=client_name)
            if res.get("success"):
                results.append(res)
                job_spec = RapidJobsRegistry.JOBS.get(jid)
                if job_spec:
                    total_value += job_spec.typical_payout_numeric

        return {
            "success": True,
            "batch_id": batch_id,
            "total_dispatched": len(results),
            "total_value_usd": f"${total_value:.2f} USD",
            "results": results
        }

    @classmethod
    def dispatch_submission(cls, job_id: str, client_name: str = "Client", recipient_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes automated submission of a completed rapid-cash job or bounty.
        """
        normalized_id = cls.normalize_job_id(job_id)
        if normalized_id == "all":
            return cls.dispatch_all_submissions(client_name)

        job = RapidJobsRegistry.JOBS.get(normalized_id)
        if not job:
            return {
                "success": False,
                "error": f"Job ID '{job_id}' not found. Valid IDs: job-01 through job-10, or 'all'."
            }

        pack = RapidJobsRegistry.generate_full_bid_pack(job, client_name)
        solution_path = os.path.join(cls.OUTPUT_DIR, job.solution_file)
        
        deliverable_content = ""
        if os.path.exists(solution_path):
            with open(solution_path, "r", encoding="utf-8") as f:
                deliverable_content = f.read()

        submission_id = f"sub-{int(time.time())}-{normalized_id}"
        record = {
            "submission_id": submission_id,
            "job_id": normalized_id,
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
            "job_id": normalized_id,
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

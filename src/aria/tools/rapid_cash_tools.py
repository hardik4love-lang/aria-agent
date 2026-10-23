"""
ARIA Rapid Cash & Bounty Tool Interface.
Allows LangGraph nodes and operator CLI to match jobs, generate pitches, and verify solutions.
"""

from typing import Dict, Any, List
from aria.bounties.rapid_jobs import RapidJobsRegistry, RapidTaskScanner, RapidJobSpec

class RapidCashTools:
    """Tools for rapid micro-bounty execution."""

    @staticmethod
    def list_ready_jobs() -> Dict[str, Any]:
        """Returns all 10 pre-tested jobs ready for conversion into cash."""
        jobs = []
        for j in RapidJobsRegistry.JOBS.values():
            jobs.append({
                "id": j.id,
                "title": j.title,
                "category": j.category,
                "payout": j.typical_payout,
                "target_channel": j.target_channel,
                "solution_file": j.solution_file
            })
        return {
            "total_jobs": len(jobs),
            "jobs": jobs,
            "payout_rails": {
                "paypal": "shruhicollections@gmail.com",
                "upi": ""
            }
        }

    @staticmethod
    def solve_and_generate_pitch(client_request: str, client_name: str = "Client") -> Dict[str, Any]:
        """
        Analyzes a client request, matches the best technical solution,
        and generates the rule-compliant $bid comment and private DM pitch.
        """
        match = RapidJobsRegistry.match_task(client_request)
        if not match:
            return {
                "matched": False,
                "message": "No direct pre-tested solution matched the prompt. Defaulting to general full-stack pitch."
            }

        pack = RapidJobsRegistry.generate_full_bid_pack(match, client_name)
        return {
            "matched": True,
            "job_id": match.id,
            "job_title": match.title,
            "payout": match.typical_payout,
            "public_bid_comment": pack["public_comment"],
            "private_dm_pitch": pack["private_dm"],
            "solution_file": pack["solution_file"],
            "sample_proof": match.sample_proof_snippet
        }

    @staticmethod
    def scan_live_reddit_tasks() -> Dict[str, Any]:
        """
        Scans live r/slavelabour for real [TASK] listings, automatically rejecting [OFFER] posts.
        """
        scanned = RapidTaskScanner.scan_reddit_slavelabour(limit=15)
        valid_tasks = [t for t in scanned if t.is_valid_task]
        return {
            "scanned_count": len(scanned),
            "valid_tasks_count": len(valid_tasks),
            "valid_tasks": [
                {
                    "title": t.title,
                    "author": t.author,
                    "url": t.url,
                    "matched_job": t.matched_job_id,
                    "ready_to_pitch": bool(t.private_dm_pitch)
                }
                for t in valid_tasks
            ]
        }

"""
ARIA Instant Liquidity Engine.
Closed-loop solver connecting AgentBounties.app (Base Mainnet / USDC)
and TaskMarket.dev (x402 protocol) to AutonomousJobSolvers for immediate automated settlement.
Zero Cost of Ownership ($0.00 / month).
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Optional

from aria.bounties.agent_market_scanner import AgentMarketplaceManager
from aria.bounties.autonomous_solvers import AutonomousJobSolvers
from aria.bounties.rapid_jobs import RapidJobsRegistry

logger = logging.getLogger("InstantLiquidityEngine")

class InstantLiquidityEngine:
    """Executes closed-loop discovery, solution generation, and instant on-chain submission."""

    SUBMISSIONS_LOG = "data/submissions_log.jsonl"

    @classmethod
    def execute_instant_opportunity_cycle(cls) -> Dict[str, Any]:
        """Scans agent-native markets and automatically dispatches solutions for instant payout."""
        from aria.bounties.fast_cash_engine import FastCashEngine
        master_res = FastCashEngine.execute_master_fast_cash_cycle()
        wallet = AgentMarketplaceManager.get_or_create_wallet()
        logger.info(f"Scanning agent markets for Base wallet: {wallet['address']}")

        # 1. Scan TaskMarket.dev
        tm_scan = AgentMarketplaceManager.scan_taskmarket()
        tasks = tm_scan.get("tasks", [])
        dispatched = []

        for task in tasks:
            task_id = task.get("id")
            title = task.get("title", "")
            description = task.get("description", "")
            reward = task.get("rewardUsdc", 0.0)

            # Match against Rapid Job templates
            matched_job = RapidJobsRegistry.match_task(f"{title} {description}")
            if matched_job:
                logger.info(f"[+] TaskMarket Match: '{title}' -> {matched_job.id} (${reward} USDC)")
                solver_method = getattr(AutonomousJobSolvers, f"solve_{matched_job.id.replace('-', '_')}", None)
                if solver_method:
                    solve_res = solver_method()
                    sol_file = solve_res.get("file")
                    if sol_file and os.path.exists(sol_file):
                        sub_res = AgentMarketplaceManager.submit_taskmarket_solution(task_id, sol_file)
                        record = {
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
                            "platform": "TaskMarket.dev (Base USDC)",
                            "task_id": task_id,
                            "job_id": matched_job.id,
                            "reward": f"${reward} USDC",
                            "status": "SUBMITTED" if sub_res.get("success") else "SUBMISSION_ATTEMPTED",
                            "wallet": wallet["address"],
                            "deliverable": sol_file
                        }
                        os.makedirs(os.path.dirname(cls.SUBMISSIONS_LOG) or ".", exist_ok=True)
                        with open(cls.SUBMISSIONS_LOG, "a", encoding="utf-8") as f:
                            f.write(json.dumps(record) + "\n")
                        dispatched.append(record)

        return {
            "cycle_complete": True,
            "wallet": wallet["address"],
            "settlement_network": "Base Mainnet (EVM)",
            "dispatched_count": len(dispatched),
            "opportunities": dispatched
        }

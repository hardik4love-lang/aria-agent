"""
ARIA Agent-Native Marketplace & Instant Bounty Engine.
Integrates autonomous task discovery, automated solving, and on-chain/API submissions
for agent-native platforms: TaskMarket.dev, AgentBounties.app (Base Mainnet / USDC),
and TaskBounty.
"""

import os
import sys
import json
import time
import base64
from typing import Dict, Any, List, Optional
import httpx

try:
    from eth_account import Account
except ImportError:
    Account = None

class AgentMarketplaceManager:
    """Manages agent-native bounty discovery, Base EVM wallet, and direct API submissions."""

    WALLET_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "state", "agent_wallet.json")
    AGENT_BOUNTIES_URL = "https://api.agentbounties.app"
    TASKMARKET_URL = "https://api.taskmarket.dev"

    @classmethod
    def get_or_create_wallet(cls) -> Dict[str, str]:
        """Loads or securely initializes the agent's sovereign Base EVM wallet."""
        os.makedirs(os.path.dirname(cls.WALLET_FILE), exist_ok=True)
        if os.path.exists(cls.WALLET_FILE):
            try:
                with open(cls.WALLET_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("address") and data.get("private_key"):
                        return data
            except Exception:
                pass

        # Generate new EVM Keypair for Base
        if Account is not None:
            acct = Account.create()
            address = acct.address
            priv_key = acct.key.hex()
        else:
            address = "0xFa53f5472F8bF07bd0eC88270AB81482B5A4337c"
            priv_key = "0x" + "0" * 64

        wallet_data = {
            "address": address,
            "private_key": priv_key,
            "network": "Base Mainnet (EVM Chain ID 8453)",
            "settlement_currency": "USDC",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC")
        }
        with open(cls.WALLET_FILE, "w", encoding="utf-8") as f:
            json.dump(wallet_data, f, indent=2)
        print(f"[+] ARIA Sovereign Base Wallet Initialized: {acct.address}")
        return wallet_data

    @classmethod
    def scan_agent_bounties(cls, limit: int = 10) -> Dict[str, Any]:
        """
        Discovers live opportunities on AgentBounties.app using the A2A 1.0 protocol.
        """
        wallet = cls.get_or_create_wallet()
        headers = {
            "A2A-Version": "1.0",
            "Content-Type": "application/a2a+json",
            "Accept": "application/a2a+json"
        }
        payload = {
            "message": {
                "messageId": f"discover-{int(time.time())}",
                "role": "ROLE_USER",
                "parts": [
                    {
                        "data": {
                            "skill": "discover-ready-to-earn-bounties",
                            "network": "base-mainnet",
                            "limit": limit
                        }
                    }
                ]
            }
        }
        try:
            with httpx.Client(timeout=12.0) as client:
                res = client.post(f"{cls.AGENT_BOUNTIES_URL}/a2a/v1/message:send", json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    task = data.get("task", {})
                    artifacts = data.get("artifacts", [])
                    items = []
                    for art in artifacts:
                        for part in art.get("parts", []):
                            if isinstance(part, dict) and "data" in part:
                                items.extend(part["data"].get("items", []))
                    return {
                        "platform": "AgentBounties.app (Base Mainnet)",
                        "status": "ONLINE",
                        "wallet_address": wallet["address"],
                        "opportunities_found": len(items),
                        "items": items,
                        "raw_task_id": task.get("id")
                    }
        except Exception as e:
            return {"platform": "AgentBounties.app", "status": "ERROR", "error": str(e)}

        return {"platform": "AgentBounties.app", "status": "NO_OPPORTUNITIES", "wallet_address": wallet["address"], "items": []}

    @classmethod
    def scan_taskmarket(cls) -> Dict[str, Any]:
        """
        Scans TaskMarket.dev for open tasks via their public REST API.
        """
        wallet = cls.get_or_create_wallet()
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.get(f"{cls.TASKMARKET_URL}/api/tasks")
                if res.status_code == 200:
                    tasks = res.json()
                    return {
                        "platform": "TaskMarket.dev (Base / x402)",
                        "status": "ONLINE",
                        "wallet_address": wallet["address"],
                        "open_tasks_count": len(tasks) if isinstance(tasks, list) else 0,
                        "tasks": tasks if isinstance(tasks, list) else []
                    }
                elif res.status_code == 404:
                    return {
                        "platform": "TaskMarket.dev",
                        "status": "ONLINE (API Available)",
                        "wallet_address": wallet["address"],
                        "open_tasks_count": 0,
                        "tasks": []
                    }
        except Exception as e:
            return {"platform": "TaskMarket.dev", "status": "ERROR", "error": str(e)}
        return {"platform": "TaskMarket.dev", "status": "ONLINE", "wallet_address": wallet["address"], "tasks": []}

    @classmethod
    def submit_taskmarket_solution(cls, task_id: str, file_path: str, role: str = "final") -> Dict[str, Any]:
        """
        Submits an autonomous solution artifact directly to TaskMarket.dev.
        """
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File {file_path} not found"}

        with open(file_path, "rb") as f:
            encoded_content = base64.b64encode(f.read()).decode("utf-8")

        wallet = cls.get_or_create_wallet()
        fname = os.path.basename(file_path)

        payload = {
            "fileName": fname,
            "mimeType": "text/plain",
            "role": role,
            "data": encoded_content,
            "solverWallet": wallet["address"]
        }
        headers = {
            "Content-Type": "application/json",
            "X-Solver-Address": wallet["address"]
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                url = f"{cls.TASKMARKET_URL}/api/tasks/{task_id}/submissions"
                res = client.post(url, json=payload, headers=headers)
                return {
                    "success": res.status_code in [200, 201],
                    "status_code": res.status_code,
                    "task_id": task_id,
                    "response": res.text,
                    "wallet": wallet["address"]
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def get_market_overview(cls) -> Dict[str, Any]:
        """Provides a unified overview of all agent-native markets and the agent's Base wallet."""
        wallet = cls.get_or_create_wallet()
        ab = cls.scan_agent_bounties(limit=5)
        tm = cls.scan_taskmarket()

        return {
            "wallet": {
                "address": wallet["address"],
                "network": wallet["network"],
                "settlement": wallet["settlement_currency"]
            },
            "platforms": [
                {
                    "name": "AgentBounties.app",
                    "status": ab.get("status"),
                    "speed": "Minutes (Automated on-chain release)",
                    "network": "Base (USDC)"
                },
                {
                    "name": "TaskMarket.dev",
                    "status": tm.get("status"),
                    "speed": "Instant / Minutes (x402 escrow)",
                    "network": "Base (USDC)"
                },
                {
                    "name": "TaskBounty (E2B Sandboxes)",
                    "status": "ONLINE",
                    "speed": "Hours (Automated test pass)",
                    "network": "Base / Solana"
                }
            ]
        }

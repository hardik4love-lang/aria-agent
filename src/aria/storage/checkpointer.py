"""
LangGraph Checkpoint Serialization and Persistence.
Integrates with Supabase (Free Tier PostgreSQL) and local JSON snapshotting.
"""

import os
import json
from typing import Optional, Dict, Any


class CheckpointManager:
    """Manages serializing agent execution state across ephemeral runner handoffs."""

    def __init__(self, local_dir: str = "state/checkpoints"):
        self.local_dir = local_dir
        self.supabase_url = os.environ.get("SUPABASE_DB_URL")
        os.makedirs(self.local_dir, exist_ok=True)

    def save_checkpoint(self, thread_id: str, checkpoint_version: int, state: Dict[str, Any]) -> str:
        """Saves a checkpoint snapshot to local state and Supabase if configured."""
        os.makedirs(self.local_dir, exist_ok=True)
        filename = f"{thread_id}_v{checkpoint_version}.json"
        local_path = os.path.join(self.local_dir, filename)

        # Sanitize state for serialization
        serializable_state = {
            "thread_id": thread_id,
            "version": checkpoint_version,
            "state": state
        }

        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(serializable_state, f, indent=2, default=str)

        # Update latest pointer
        latest_path = os.path.join(self.local_dir, f"{thread_id}_latest.json")
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump({"latest_version": checkpoint_version, "file": filename}, f)

        # Sync to Supabase PostgreSQL if DB URL available
        if self.supabase_url:
            self._sync_to_supabase(thread_id, checkpoint_version, serializable_state)

        return local_path

    def load_checkpoint(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Loads the most recent checkpoint for a given thread_id."""
        latest_path = os.path.join(self.local_dir, f"{thread_id}_latest.json")
        if not os.path.exists(latest_path):
            return None

        try:
            with open(latest_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            target_file = os.path.join(self.local_dir, meta["file"])
            if os.path.exists(target_file):
                with open(target_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("state")
        except Exception:
            return None
        return None

    def _sync_to_supabase(self, thread_id: str, version: int, payload: Dict[str, Any]) -> None:
        """Writes checkpoint row into Supabase agent_checkpoints table."""
        try:
            import psycopg2
            conn = psycopg2.connect(self.supabase_url)
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS agent_checkpoints (
                        thread_id TEXT,
                        version INT,
                        state JSONB,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        PRIMARY KEY (thread_id, version)
                    );
                """)
                cur.execute("""
                    INSERT INTO agent_checkpoints (thread_id, version, state)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (thread_id, version) DO UPDATE SET state = EXCLUDED.state;
                """, (thread_id, version, json.dumps(payload, default=str)))
            conn.commit()
            conn.close()
        except Exception:
            # Failure to reach Supabase is non-fatal; local git checkpoint remains authoritative
            pass

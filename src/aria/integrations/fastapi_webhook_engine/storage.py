"""
Idempotent Webhook Storage & Ingestion Layer.
Stores received webhook events in SQLite / PostgreSQL with deduplication guards.
"""

import sqlite3
import json
import time
import threading
from typing import Optional, Dict, Any, List

class WebhookStore:
    """Manages idempotent persistence of incoming webhook events."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._lock = threading.Lock()
        # For in-memory databases, keep a persistent connection so tables persist across calls
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        with self._lock:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS webhook_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'received',
                    received_at REAL NOT NULL,
                    processed_at REAL,
                    retry_count INTEGER DEFAULT 0,
                    error_message TEXT,
                    UNIQUE(source, event_id)
                )
            """)
            self._conn.commit()

    def record_event(self, source: str, event_id: str, event_type: str, payload: Dict[str, Any]) -> bool:
        """
        Records a new webhook event.
        Returns True if the event was newly inserted, False if it was already recorded (idempotency guard).
        """
        payload_str = json.dumps(payload)
        now = time.time()
        with self._lock:
            try:
                self._conn.execute(
                    """
                    INSERT INTO webhook_events (event_id, source, event_type, payload, status, received_at)
                    VALUES (?, ?, ?, ?, 'received', ?)
                    """,
                    (event_id, source, event_type, payload_str, now)
                )
                self._conn.commit()
                return True
            except sqlite3.IntegrityError:
                # Already exists - duplicate/replay prevented
                return False

    def mark_processed(self, source: str, event_id: str, success: bool = True, error: Optional[str] = None):
        """Updates event status after background processing."""
        now = time.time()
        status = "processed" if success else "failed"
        with self._lock:
            self._conn.execute(
                """
                UPDATE webhook_events
                SET status = ?, processed_at = ?, error_message = ?
                WHERE source = ? AND event_id = ?
                """,
                (status, now, error, source, event_id)
            )
            self._conn.commit()

    def get_event(self, source: str, event_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an event by source and ID."""
        with self._lock:
            cursor = self._conn.execute(
                "SELECT * FROM webhook_events WHERE source = ? AND event_id = ?",
                (source, event_id)
            )
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d["payload"] = json.loads(d["payload"])
                return d
            return None

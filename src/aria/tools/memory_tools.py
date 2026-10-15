"""
Long-Term Memory and Semantic Storage Tools.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional


class MemoryTools:
    """Manages persistent semantic facts, episodic summaries, and user context."""

    def __init__(self, memory_file: str = "state/memory_store.json"):
        self.memory_file = memory_file
        self.supabase_url = os.environ.get("SUPABASE_DB_URL")
        os.makedirs(os.path.dirname(self.memory_file) or ".", exist_ok=True)

    def _load_local_store(self) -> Dict[str, Any]:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"items": []}

    def _save_local_store(self, data: Dict[str, Any]) -> None:
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def memory_store(self, key: str, value: str, namespace: str = "general") -> Dict[str, Any]:
        """Stores a piece of information or preference into memory."""
        store = self._load_local_store()
        entry = {
            "key": key,
            "value": value,
            "namespace": namespace,
            "created_at": time.time(),
            "access_count": 0
        }
        # Update if key in namespace exists, else append
        existing = False
        for item in store["items"]:
            if item["key"] == key and item["namespace"] == namespace:
                item["value"] = value
                item["updated_at"] = time.time()
                existing = True
                break

        if not existing:
            store["items"].append(entry)

        self._save_local_store(store)
        return {"success": True, "stored_key": key, "namespace": namespace}

    def memory_retrieve(self, query: str, namespace: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves memories matching query keywords or namespace."""
        store = self._load_local_store()
        query_words = set(query.lower().split())
        scored_items = []

        for item in store.get("items", []):
            if namespace and item.get("namespace") != namespace:
                continue
            text = f"{item.get('key', '')} {item.get('value', '')}".lower()
            overlap = len([w for w in query_words if w in text])
            item["access_count"] = item.get("access_count", 0) + 1
            scored_items.append((overlap, item))

        self._save_local_store(store)
        scored_items.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored_items[:limit]]

    def memory_summarize_old_context(self, max_items: int = 50) -> Dict[str, Any]:
        """Consolidates old memories to prevent storage bloat."""
        store = self._load_local_store()
        total_before = len(store.get("items", []))
        if total_before > max_items:
            # Keep highest accessed items
            items = sorted(store["items"], key=lambda x: x.get("access_count", 0), reverse=True)
            store["items"] = items[:max_items]
            self._save_local_store(store)
            return {"status": "pruned", "pruned_count": total_before - max_items}
        return {"status": "no_pruning_needed", "count": total_before}

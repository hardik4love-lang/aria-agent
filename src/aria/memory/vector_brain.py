"""
ARIA Vector Brain — Semantic Long-Term Memory using ChromaDB.
Persists lessons, PR outcomes, and repo knowledge across GitHub Actions runs.
Data stored in data/vector_brain/ and committed to the repo.
"""

import os
import json
import hashlib
import datetime
import logging
from typing import Optional

logger = logging.getLogger("ARIAVectorBrain")

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logger.warning("chromadb not installed — vector brain will use flat JSON fallback")


class ARIAVectorBrain:
    """
    Semantic memory for ARIA. Stores facts as vector embeddings.
    Falls back to flat JSON if chromadb is unavailable.
    """

    def __init__(self, data_dir: str = None):
        base = data_dir or os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        self.vector_dir = os.path.join(base, "vector_brain")
        self.fallback_file = os.path.join(base, "vector_brain_fallback.json")
        os.makedirs(self.vector_dir, exist_ok=True)

        if CHROMA_AVAILABLE:
            try:
                self.client = chromadb.PersistentClient(path=self.vector_dir)
                self.collection = self.client.get_or_create_collection(
                    name="aria_memory",
                    metadata={"hnsw:space": "cosine"}
                )
                self._use_chroma = True
                logger.info(f"Vector brain online — {self.collection.count()} memories loaded.")
            except Exception as e:
                logger.warning(f"ChromaDB init failed: {e} — using flat fallback")
                self._use_chroma = False
        else:
            self._use_chroma = False

        self._fallback: list = self._load_fallback()

    # ── Flat JSON fallback ────────────────────────────────────────────────────

    def _load_fallback(self) -> list:
        if os.path.exists(self.fallback_file):
            try:
                with open(self.fallback_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_fallback(self):
        with open(self.fallback_file, "w", encoding="utf-8") as f:
            json.dump(self._fallback[-500:], f, indent=2)  # keep last 500

    # ── Public API ────────────────────────────────────────────────────────────

    def remember(self, text: str, metadata: Optional[dict] = None):
        """Store a lesson, PR outcome, or repo fact."""
        metadata = metadata or {}
        metadata["stored_at"] = datetime.datetime.utcnow().isoformat()
        doc_id = hashlib.md5((text + metadata.get("stored_at", "")).encode()).hexdigest()

        if self._use_chroma:
            try:
                self.collection.upsert(
                    documents=[text],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
                return
            except Exception as e:
                logger.warning(f"ChromaDB upsert failed: {e}")

        # Flat fallback
        self._fallback.append({"id": doc_id, "text": text, "metadata": metadata})
        self._save_fallback()

    def recall(self, query: str, n: int = 5) -> list:
        """Return most relevant past memories for a query."""
        if self._use_chroma:
            try:
                results = self.collection.query(query_texts=[query], n_results=min(n, max(self.collection.count(), 1)))
                docs = results.get("documents", [[]])[0]
                metas = results.get("metadatas", [[]])[0]
                return [{"text": d, "metadata": m} for d, m in zip(docs, metas)]
            except Exception as e:
                logger.warning(f"ChromaDB query failed: {e}")

        # Flat fallback: simple keyword match
        query_lower = query.lower()
        matches = [m for m in self._fallback if query_lower in m["text"].lower()]
        return matches[-n:]

    def record_pr_outcome(self, repo: str, issue_number: int, title: str,
                          outcome: str, reason: str = ""):
        """
        Record a PR submission outcome.
        outcome: 'merged', 'rejected', 'closed', 'pending', 'blocked'
        """
        text = (
            f"PR outcome for {repo} issue #{issue_number}: {outcome}. "
            f"Title: {title}. Reason: {reason}"
        )
        self.remember(text, metadata={
            "type": "pr_outcome",
            "repo": repo,
            "issue": issue_number,
            "outcome": outcome,
            "title": title,
        })
        logger.info(f"Remembered PR outcome: {repo}#{issue_number} → {outcome}")

    def repo_score_adjustment(self, repo: str) -> float:
        """
        Return a score multiplier (0.5 to 1.5) based on past PR success rate for this repo.
        >1.0 = historically successful, <1.0 = historically rejected.
        """
        memories = self.recall(f"PR outcome for {repo}", n=20)
        if not memories:
            return 1.0  # neutral — no history

        merged = sum(1 for m in memories if "merged" in m["text"].lower())
        rejected = sum(1 for m in memories if "rejected" in m["text"].lower() or "closed" in m["text"].lower())
        blocked = sum(1 for m in memories if "blocked" in m["text"].lower())

        if blocked > 0:
            return 0.3  # repo blocks external PRs — strong penalty
        if merged + rejected == 0:
            return 1.0

        win_rate = merged / (merged + rejected)
        # Scale: 0% win → 0.5, 50% win → 1.0, 100% win → 1.5
        return round(0.5 + win_rate, 2)

    def count(self) -> int:
        if self._use_chroma:
            try:
                return self.collection.count()
            except Exception:
                pass
        return len(self._fallback)

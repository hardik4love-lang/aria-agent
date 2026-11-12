"""
Asynchronous Background Task Queue with Automated Exponential Backoff Retries.
Ensures webhook handlers return 200 OK fast (<50ms) while handling heavy processing asynchronously.
"""

import asyncio
import logging
from typing import Callable, Coroutine, Dict, Any, Optional

logger = logging.getLogger("webhook_queue")

class BackgroundRetryQueue:
    """Processes webhook tasks in the background with exponential backoff retries."""

    def __init__(self, max_retries: int = 3, base_delay: float = 0.5):
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def execute_with_retry(
        self,
        task_id: str,
        handler: Callable[..., Coroutine[Any, Any, Any]],
        *args,
        **kwargs
    ) -> bool:
        """Executes an async task with automatic retries on failure."""
        for attempt in range(1, self.max_retries + 1):
            try:
                await handler(*args, **kwargs)
                return True
            except Exception as e:
                logger.warning(
                    f"[Attempt {attempt}/{self.max_retries}] Task {task_id} failed: {e}"
                )
                if attempt == self.max_retries:
                    logger.error(f"[FAILED] Task {task_id} exceeded maximum retries.")
                    return False
                delay = self.base_delay * (2 ** (attempt - 1))
                await asyncio.sleep(delay)
        return False

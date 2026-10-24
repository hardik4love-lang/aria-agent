"""
ARIA Centralized HTTP Connection Pooling & Client Management.
Provides persistent connection pooling with keepalive to eliminate TCP/TLS handshake latency.
Zero Cost of Ownership ($0.00 / month).
"""

import threading
from typing import Optional
import httpx

_sync_client: Optional[httpx.Client] = None
_async_client: Optional[httpx.AsyncClient] = None
_lock = threading.Lock()

POOL_LIMITS = httpx.Limits(
    max_keepalive_connections=20,
    max_connections=50,
    keepalive_expiry=60.0
)

DEFAULT_TIMEOUT = httpx.Timeout(timeout=15.0, connect=5.0)


def get_http_client(timeout: Optional[float] = None) -> httpx.Client:
    """Returns a shared, thread-safe synchronous HTTP client with connection pooling."""
    global _sync_client
    with _lock:
        if _sync_client is None or _sync_client.is_closed:
            client_timeout = httpx.Timeout(timeout=timeout or 15.0, connect=5.0)
            _sync_client = httpx.Client(
                limits=POOL_LIMITS,
                timeout=client_timeout,
                headers={"User-Agent": "ARIA-Sovereign-Agent/2.0"}
            )
        return _sync_client


async def get_async_http_client(timeout: Optional[float] = None) -> httpx.AsyncClient:
    """Returns a shared asynchronous HTTP client with connection pooling."""
    global _async_client
    if _async_client is None or _async_client.is_closed:
        client_timeout = httpx.Timeout(timeout=timeout or 15.0, connect=5.0)
        _async_client = httpx.AsyncClient(
            limits=POOL_LIMITS,
            timeout=client_timeout,
            headers={"User-Agent": "ARIA-Sovereign-Agent/2.0"}
        )
    return _async_client


def close_http_clients() -> None:
    """Closes all active HTTP clients cleanly."""
    global _sync_client, _async_client
    with _lock:
        if _sync_client and not _sync_client.is_closed:
            try:
                _sync_client.close()
            except Exception:
                pass
            _sync_client = None


async def close_async_http_clients() -> None:
    """Closes active async HTTP clients cleanly."""
    global _async_client
    if _async_client and not _async_client.is_closed:
        try:
            await _async_client.aclose()
        except Exception:
            pass
        _async_client = None

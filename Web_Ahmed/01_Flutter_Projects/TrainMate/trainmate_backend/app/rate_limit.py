"""Simple in-memory rate limiting for auth endpoints."""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request, status

_lock = Lock()
_buckets: dict[str, list[float]] = defaultdict(list)


def _client_key(request: Request, scope: str) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    ip = forwarded.split(",")[0].strip() if forwarded else None
    if not ip and request.client:
        ip = request.client.host
    return f"{scope}:{ip or 'unknown'}"


def enforce_rate_limit(
    request: Request,
    *,
    scope: str,
    max_attempts: int,
    window_seconds: int,
) -> None:
    now = time.monotonic()
    key = _client_key(request, scope)
    with _lock:
        hits = _buckets[key]
        cutoff = now - window_seconds
        _buckets[key] = hits = [t for t in hits if t > cutoff]
        if len(hits) >= max_attempts:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Please try again later.",
            )
        hits.append(now)

import time
import threading
from typing import Callable, Iterable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class FixedWindowRateLimiter:
    """Simple fixed-window in-memory rate limiter.
    Keyed by identifier (IP address or user id). Not distributed.
    """
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # mapping: key -> (window_start_ts, count)
        self._data: dict[str, tuple[float, int]] = {}
        self._lock = threading.Lock()

    def allow_request(self, key: str) -> bool:
        now = time.time()
        window = now - (now % self.window_seconds)
        with self._lock:
            if key not in self._data:
                self._data[key] = (window, 1)
                return True
            start, count = self._data[key]
            if start < window:
                # new window
                self._data[key] = (window, 1)
                return True
            if count < self.max_requests:
                self._data[key] = (start, count + 1)
                return True
            return False

    def get_state(self, key: str):
        with self._lock:
            return self._data.get(key, (0, 0))

    def cleanup(self, older_than_seconds: int = 3600):
        # remove entries older than threshold to avoid memory growth
        cutoff = time.time() - older_than_seconds
        with self._lock:
            keys_to_delete = []
            for k, (start, _) in self._data.items():
                if start < cutoff:
                    keys_to_delete.append(k)
            for k in keys_to_delete:
                del self._data[k]


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limiter: FixedWindowRateLimiter, exempt_paths: Iterable[str] | None = None, get_identifier: Callable[[Request], str] | None = None):
        super().__init__(app)
        self.limiter = limiter
        self.exempt_paths = set(exempt_paths or [])
        # get_identifier: function to extract key from request (e.g., user id or IP)
        self.get_identifier = get_identifier or (lambda request: request.client.host if request.client else "unknown")

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # Skip docs and openapi and exempt paths
        if path.startswith("/docs") or path.startswith("/openapi.json") or path.startswith("/redoc"):
            return await call_next(request)
        for ep in self.exempt_paths:
            if path.startswith(ep):
                return await call_next(request)

        try:
            key = self.get_identifier(request)
        except Exception:
            key = request.client.host if request.client else "unknown"

        allowed = self.limiter.allow_request(key)
        if not allowed:
            # 429 Too Many Requests
            return Response(content="Too Many Requests", status_code=429)

        response = await call_next(request)
        # Optionally set rate-limit headers
        start, count = self.limiter.get_state(key)
        response.headers["X-RateLimit-Limit"] = str(self.limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.limiter.max_requests - count))
        response.headers["X-RateLimit-Reset"] = str(int(start + self.limiter.window_seconds))
        return response

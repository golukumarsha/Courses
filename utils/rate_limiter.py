"""
utils/rate_limiter.py
In-memory Rate Limiter — Redis ki zarurat nahi!
Sliding Window algorithm use karta hai.
"""
import time
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from utils.logger import get_logger

logger = get_logger("rate_limiter")

# ─── Rate Limit Rules ─────────────────────────────────
RATE_LIMIT_RULES = {
    # path_prefix : (max_requests, window_seconds)
    "/auth/login":    (5,  60),   # 5 login attempts per minute
    "/auth/register": (3,  60),   # 3 register attempts per minute
    "/create":        (10, 60),   # 10 creates per minute
    "/update":        (20, 60),   # 20 updates per minute
    "/delete":        (10, 60),   # 10 deletes per minute
    "/search":        (30, 60),   # 30 searches per minute
    "/reviews":       (15, 60),   # 15 review actions per minute
    "/enrollments":   (20, 60),   # 20 enrollment actions per minute
    "default":        (60, 60),   # 60 requests per minute for everything else
}

# ─── Skip paths (rate limit nahi lagegi) ──────────────
SKIP_PATHS = {"/", "/docs", "/openapi.json", "/redoc"}

# ─── In-memory store ──────────────────────────────────
# { "ip:path_rule" : deque([timestamp1, timestamp2, ...]) }
_request_store: dict = defaultdict(deque)


def _get_rule(path: str) -> tuple[int, int]:
    """Path ke liye sahi rule dhundho"""
    for prefix, rule in RATE_LIMIT_RULES.items():
        if prefix != "default" and path.startswith(prefix):
            return rule
    return RATE_LIMIT_RULES["default"]


def _get_client_ip(request: Request) -> str:
    """Real IP dhundho — proxy ke peeche bhi"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"


async def rate_limit_middleware(request: Request, call_next):
    """
    Sliding Window Rate Limiter Middleware.
    Har request pe check karta hai:
    1. Client ka IP lo
    2. Path ke liye rule dhundho
    3. Last N seconds mein kitni requests hain check karo
    4. Limit se zyada hain toh 429 return karo
    """
    path = request.url.path

    # Static files aur docs skip karo
    if path in SKIP_PATHS or path.startswith("/static"):
        return await call_next(request)

    client_ip = _get_client_ip(request)
    max_req, window = _get_rule(path)

    # Rule key banao
    rule_key = None
    for prefix in RATE_LIMIT_RULES:
        if prefix != "default" and path.startswith(prefix):
            rule_key = prefix
            break
    rule_key = rule_key or "default"

    store_key = f"{client_ip}:{rule_key}"
    now = time.time()
    window_start = now - window

    # Purani requests hata do (window se bahar)
    timestamps = _request_store[store_key]
    while timestamps and timestamps[0] < window_start:
        timestamps.popleft()

    current_count = len(timestamps)
    remaining = max_req - current_count - 1
    reset_time = int(
        timestamps[0] + window) if timestamps else int(now + window)

    # Limit check karo
    if current_count >= max_req:
        retry_after = int(reset_time - now) + 1
        logger.warning(
            f"RATE LIMIT exceeded — IP: {client_ip} | "
            f"Path: {path} | Rule: {rule_key} | "
            f"Count: {current_count}/{max_req} | "
            f"Retry after: {retry_after}s"
        )
        raise HTTPException(
            status_code=429,
            detail={
                "error":       "Too Many Requests",
                "message":     f"Aap bahut zyada requests kar rahe hain! {retry_after} second baad try karein.",
                "limit":       max_req,
                "window":      f"{window} seconds",
                "retry_after": retry_after,
            },
            headers={
                "Retry-After":              str(retry_after),
                "X-RateLimit-Limit":        str(max_req),
                "X-RateLimit-Remaining":    "0",
                "X-RateLimit-Reset":        str(reset_time),
            }
        )

    # Request count karo
    timestamps.append(now)

    # Response mein rate limit headers add karo
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(max_req)
    response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
    response.headers["X-RateLimit-Reset"] = str(reset_time)
    response.headers["X-RateLimit-Window"] = f"{window}s"

    return response


def get_rate_limit_status() -> dict:
    """Current rate limit status — monitoring ke liye"""
    now = time.time()
    status = {}
    for key, timestamps in _request_store.items():
        if timestamps:
            ip, rule = key.rsplit(":", 1)
            max_req, window = RATE_LIMIT_RULES.get(
                rule, RATE_LIMIT_RULES["default"])
            recent = [t for t in timestamps if t > now - window]
            if recent:
                status[key] = {
                    "ip":        ip,
                    "rule":      rule,
                    "count":     len(recent),
                    "limit":     max_req,
                    "remaining": max(0, max_req - len(recent)),
                }
    return status

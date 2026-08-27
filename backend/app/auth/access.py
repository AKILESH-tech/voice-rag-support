import time, hashlib, secrets
from fastapi import HTTPException, Header, Request
from app.config import settings
from app.db.database import get_db

ACCESS_PASSCODE = "demo2024"  # overridden by ACCESS_PASSCODE env var

def get_passcode() -> str:
    return getattr(settings, 'access_passcode', ACCESS_PASSCODE)

def _session_key(request: Request) -> str:
    ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    ip = ip.split(",")[0].strip()
    return hashlib.sha256(ip.encode()).hexdigest()[:16]

def verify_access(request: Request, x_access_token: str = Header(default="")):
    """Verify passcode token. Token = sha256(passcode + date)."""
    today = time.strftime("%Y-%m-%d")
    expected = hashlib.sha256(f"{get_passcode()}{today}".encode()).hexdigest()
    if not secrets.compare_digest(x_access_token, expected):
        raise HTTPException(status_code=401, detail="Access denied. Use the provided access code.")
    return True

def check_rate_limit(request: Request, endpoint: str = "default"):
    """Allow max 3 AI calls per session per day."""
    session_key = _session_key(request)
    today = time.strftime("%Y-%m-%d")
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS rate_limits (
            session_key TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            date TEXT NOT NULL,
            count INTEGER DEFAULT 0,
            PRIMARY KEY (session_key, endpoint, date)
        )""")
        row = conn.execute(
            "SELECT count FROM rate_limits WHERE session_key=? AND endpoint=? AND date=?",
            (session_key, endpoint, today)
        ).fetchone()
        count = row["count"] if row else 0
        if count >= 3:
            raise HTTPException(
                status_code=429,
                detail="You've used all 3 evaluations for today. Come back tomorrow to continue! 🌅"
            )
        if row:
            conn.execute(
                "UPDATE rate_limits SET count=count+1 WHERE session_key=? AND endpoint=? AND date=?",
                (session_key, endpoint, today)
            )
        else:
            conn.execute(
                "INSERT INTO rate_limits (session_key, endpoint, date, count) VALUES (?,?,?,1)",
                (session_key, endpoint, today)
            )
    return count + 1

def get_usage(request: Request, endpoint: str = "default") -> dict:
    session_key = _session_key(request)
    today = time.strftime("%Y-%m-%d")
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS rate_limits (
            session_key TEXT NOT NULL, endpoint TEXT NOT NULL, date TEXT NOT NULL,
            count INTEGER DEFAULT 0, PRIMARY KEY (session_key, endpoint, date)
        )""")
        row = conn.execute(
            "SELECT count FROM rate_limits WHERE session_key=? AND endpoint=? AND date=?",
            (session_key, endpoint, today)
        ).fetchone()
    count = row["count"] if row else 0
    return {"used": count, "limit": 3, "remaining": max(0, 3 - count)}

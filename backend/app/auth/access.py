import time
import hashlib
from fastapi import HTTPException, Header, Request
from app.config import settings
from app.db.database import get_db


def _session_key(request: Request, user_uid: str | None = None) -> str:
    if user_uid:
        return hashlib.sha256(f"user:{user_uid}".encode()).hexdigest()[:16]
    ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    ip = ip.split(",")[0].strip()
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def verify_access(authorization: str = Header(default="")) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    if not settings.firebase_project_id:
        if settings.firebase_allow_dev_auth and token.startswith("dev_"):
            uid = token.replace("dev_", "", 1)
            return {"uid": uid, "email": f"{uid}@dev.local", "provider": "dev"}
        raise HTTPException(status_code=401, detail="Firebase not configured on server")

    try:
        import firebase_admin
        from firebase_admin import auth, credentials

        if not firebase_admin._apps:
            cred_path = settings.google_application_credentials
            if cred_path:
                cred = credentials.Certificate(cred_path)
            else:
                cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)

        decoded = auth.verify_id_token(token, check_revoked=True)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired Firebase token")

    if decoded.get("aud") != settings.firebase_project_id:
        raise HTTPException(status_code=401, detail="Token audience does not match Firebase project")

    return {
        "uid": decoded["uid"],
        "email": decoded.get("email", ""),
        "provider": decoded.get("firebase", {}).get("sign_in_provider", "google.com"),
    }


def check_rate_limit(request: Request, endpoint: str = "default", user_uid: str | None = None):
    """Allow max 3 AI calls per authenticated user per day."""
    session_key = _session_key(request, user_uid)
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


def get_usage(request: Request, endpoint: str = "default", user_uid: str | None = None) -> dict:
    session_key = _session_key(request, user_uid)
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

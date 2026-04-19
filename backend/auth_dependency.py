from fastapi import Header, HTTPException
from auth import verify_token


def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        token = authorization.split(" ")[1]  # Bearer <token>
        payload = verify_token(token)
        return payload["user_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
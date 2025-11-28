from datetime import datetime, timezone, timedelta
from flask import current_app
import jwt

JWT_EXPIRATION_WEEKS = 13


def generate_token(user_id, username, is_admin):
    payload = {
        "user_id": user_id,
        "username": username,
        "is_admin": is_admin,
        "exp": datetime.now(timezone.utc) + timedelta(weeks=JWT_EXPIRATION_WEEKS),
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, current_app.config["SECRET"], algorithm="HS256")
    return token

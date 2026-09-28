from datetime import datetime, timedelta, timezone
from hashlib import pbkdf2_hmac
from hmac import compare_digest, new as hmac_new

import base64
import hashlib
import json
import os

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from .config import get_settings
from .database import get_db


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",
    auto_error=False,
)


def hash_password(password: str) -> str:
    salt = os.urandom(16)

    digest = pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        210_000,
    )

    return (
        "pbkdf2_sha256$210000$"
        f"{base64.urlsafe_b64encode(salt).decode()}$"
        f"{base64.urlsafe_b64encode(digest).decode()}"
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, rounds, salt_b64, digest_b64 = stored.split("$", 3)

        if scheme != "pbkdf2_sha256":
            return False

        salt = base64.urlsafe_b64decode(
            salt_b64.encode()
        )

        expected = base64.urlsafe_b64decode(
            digest_b64.encode()
        )

        actual = pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt,
            int(rounds),
        )

        return compare_digest(actual, expected)

    except Exception:
        return False


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(
        value + "=" * (-len(value) % 4)
    )


def create_access_token(user_id: int) -> str:
    settings = get_settings()

    header = _b64(
        json.dumps(
            {
                "alg": "HS256",
                "typ": "JWT",
            },
            separators=(",", ":"),
        ).encode()
    )

    expiration = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    )

    exp = int(expiration.timestamp())

    payload = _b64(
        json.dumps(
            {
                "sub": str(user_id),
                "exp": exp,
            },
            separators=(",", ":"),
        ).encode()
    )

    message = f"{header}.{payload}".encode()

    signature = _b64(
        hmac_new(
            settings.secret_key.encode(),
            message,
            hashlib.sha256,
        ).digest()
    )

    return f"{header}.{payload}.{signature}"


def _decode(token: str):
    try:
        header, payload, signature = token.split(".")

        expected = _b64(
            hmac_new(
                get_settings().secret_key.encode(),
                f"{header}.{payload}".encode(),
                hashlib.sha256,
            ).digest()
        )

        if not compare_digest(signature, expected):
            return None

        data = json.loads(_unb64(payload))

        if int(data["exp"]) < int(
            datetime.now(timezone.utc).timestamp()
        ):
            return None

        return int(data["sub"])

    except Exception:
        return None


def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
):
    token = token or request.cookies.get("access_token")

    user_id = _decode(token) if token else None

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    with get_db() as db:
        row = db.execute(
            """
            SELECT id, username, email, created_at
            FROM users
            WHERE id=?
            """,
            (user_id,),
        ).fetchone()

    if not row:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return dict(row)
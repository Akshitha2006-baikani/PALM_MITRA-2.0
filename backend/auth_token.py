from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt


SECRET_KEY = "palm-mitra-development-secret-key-change-before-deployment"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    """
    Create a JWT access token.
    """

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str):
    """
    Decode and verify a JWT access token.

    Returns the token payload if valid.
    Returns None if the token is invalid or expired.
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        return None
        
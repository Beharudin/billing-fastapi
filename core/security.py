from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------- PASSWORD ----------
def hash_password(password: str):
    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) > 72:
        print("Passsword: in if")
        truncated = pw_bytes[:72].decode("utf-8", "ignore")
        try:
            return pwd_context.hash(truncated)
        except ValueError:
            raise ValueError("Password too long after truncation; provide a shorter password (<=72 bytes UTF-8)")
    try:
        return pwd_context.hash(password)
    except ValueError:
        # re-raise with clearer message
        raise ValueError("Password cannot be longer than 72 bytes when encoded in UTF-8; truncate or use a shorter password")

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

# ---------- JWT ----------
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

def decode_token(token: str):
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM]
    )
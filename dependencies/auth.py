from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from core.security import decode_token
from core.database import get_db
from models.user import User

oauth2 = HTTPBearer()

def get_current_user(token=Depends(oauth2), db: Session = Depends(get_db)):

    try:
        payload = decode_token(token.credentials)

        user = db.query(User).filter(User.id == payload["sub"]).first()

        if not user:
            raise Exception()

        return user

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.response import format_response
from core.security import create_access_token

from schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RegisterResponse,
    LoginResponse,
    TokenResponse,
    UserResponse,
    AdminRegisterRequest
)

from services.auth_service import (
    register_user,
    authenticate_user,
    register_admin
)

from dependencies.auth import get_current_user
from dependencies.rbac import require_roles
from models.enums import RoleEnum

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if len(payload.password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password must be at most 72 bytes when encoded in UTF-8")

    user = register_user(
        db=db,
        email=payload.email,
        password=payload.password,
        is_active=payload.is_active
    )

    user_data = UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active
    )

    return format_response("User created", user_data)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    user = authenticate_user(db, payload.email, payload.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({"sub": str(user.id)})

    return format_response(
        "Login successful",
        TokenResponse(access_token=token)
    )


@router.post("/admin/register", response_model=RegisterResponse)
def admin_register(
    payload: AdminRegisterRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    require_roles(current_user, [RoleEnum.ADMIN])

    if len(payload.password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password must be at most 72 bytes when encoded in UTF-8")

    user = register_admin(
        db,
        payload.email,
        payload.password,
        payload.role,
        payload.is_active
    )

    user_data = UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active
    )

    return format_response("Admin created", user_data)
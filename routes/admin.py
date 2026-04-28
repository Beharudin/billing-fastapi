from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from dependencies.auth import get_current_user
from dependencies.rbac import require_roles
from models.plan import Plan
from models.user import User
from models.enums import RoleEnum
from schemas.admin import (
    RevenueResponse,
    PlanCreate,
    PlanResponse,
    UserRoleUpdate,
    UserResponse,
    PlanFullResponse
)
from core.response import format_response
from models.webhook_event import WebhookEvent
from core.stripe_client import create_price_for_product, create_product


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/revenue", response_model=RevenueResponse)
def get_revenue(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_roles(user, [RoleEnum.ADMIN.value])

    result = db.execute("""
        SELECT SUM(amount) FROM payments WHERE status='succeeded'
    """).scalar() or 0

    return {"total_revenue": float(result)}


@router.post("/plans", response_model=PlanFullResponse)
def create_plan(payload: PlanCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_roles(user, [RoleEnum.ADMIN.value])
    # Validate
    if payload.price is None or payload.price <= 0:
        raise HTTPException(status_code=400, detail="Price must be a positive number")

    # prevent duplicate plan names early
    existing = db.query(Plan).filter(Plan.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Plan with this name already exists")

    # Convert dollars -> cents (round to nearest cent)
    price_cents = int(round(payload.price * 100))

    # Create Stripe product + price (unit_amount in cents)
    try:
        product = create_product(payload.name)
        stripe_price = create_price_for_product(product.id, price_cents, payload.interval)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Stripe error: {exc}")

    # Store plan with Stripe price_id
    p = Plan(
        name=payload.name,
        price_cents=price_cents,
        interval=payload.interval,
        stripe_price_id=stripe_price.id,
    )
    db.add(p)
    db.commit()
    db.refresh(p)

    return format_response("Plan created", PlanResponse.from_orm(p))


@router.get("/plans")
def list_plans(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_roles(user, [RoleEnum.ADMIN.value])
    plans = db.query(Plan).all()
    return format_response("Plans", {"plans": [PlanResponse.from_orm(p) for p in plans]})


@router.put("/plans/{plan_id}")
def update_plan(plan_id: str, payload: PlanCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_roles(user, [RoleEnum.ADMIN.value])
    p = db.query(Plan).filter(Plan.id == plan_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Plan not found")
    p.name = payload.name
    p.price_cents = int(payload.price * 100)
    p.interval = payload.interval
    db.commit()
    db.refresh(p)
    return PlanResponse.from_orm(p)


@router.delete("/plans/{plan_id}")
def delete_plan(plan_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_roles(user, [RoleEnum.ADMIN.value])
    p = db.query(Plan).filter(Plan.id == plan_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(p)
    db.commit()
    return format_response("Deleted")


@router.get("/users")
def list_users(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_roles(user, [RoleEnum.ADMIN.value])
    users = db.query(User).all()
    return format_response("Users", {"users": [UserResponse.from_orm(u) for u in users]})


@router.post("/users/{user_id}/role")
def update_user_role(user_id: str, payload: UserRoleUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_roles(user, [RoleEnum.ADMIN.value])
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.role not in (RoleEnum.ADMIN.value, RoleEnum.MEMBER.value):
        raise HTTPException(status_code=400, detail="Invalid role")
    u.role = payload.role
    db.commit()
    db.refresh(u)
    return UserResponse.from_orm(u)


@router.get("/webhook-events")
def list_webhook_events(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_roles(user, [RoleEnum.ADMIN.value])
    events = db.query(WebhookEvent).order_by(WebhookEvent.created_at.desc()).limit(200).all()
    return format_response("Webhook events", {"events": [ {"id": e.id, "stripe_event_id": e.stripe_event_id, "event_type": e.event_type, "processed": e.processed, "created_at": e.created_at.isoformat(), "processed_at": e.processed_at.isoformat() if e.processed_at else None } for e in events ]})
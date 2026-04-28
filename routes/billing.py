from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.stripe_client import create_checkout_session
from dependencies.auth import get_current_user
from services.stripe_service import start_checkout
from schemas.billing import (
    CreateCheckoutRequest,
    CreateUsageRequest,
    SubscriptionResponse,
)
from core.response import format_response
from services.billing_service import ( 
    record_usage,
    list_subscriptions,
    cancel_subscription,
    get_usage,
)

from models.plan import Plan
from models.subscription import Subscription
from datetime import datetime

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/checkout")
def checkout(payload: CreateCheckoutRequest, user=Depends(get_current_user)):
    session = start_checkout(user, payload.price_id)
    return format_response("Checkout created", {"url": session.url})


@router.post("/subscribe")
def subscribe_to_plan(price_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Fetch the plan by price_id
    plan = db.query(Plan).filter(Plan.stripe_price_id == price_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Create Stripe checkout session
    checkout_session = create_checkout_session(user.stripe_customer_id, price_id)

    # Create a subscription record with status 'incomplete'
    subscription = Subscription(
        user_id=user.id,
        stripe_subscription_id=None,
        status="incomplete",
        plan=plan.name,
        current_period_end=datetime.utcnow()
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return {"subscription_id": subscription.id, "status": subscription.status, "checkout_url": checkout_session.url}


@router.get("/plans", response_model=dict)
def get_plans(db: Session = Depends(get_db)):
    plans = db.query(Plan).all()
    return {
        "message": "Plans",
        "status": "success",
        "data": {
            "plans": [
                {
                    "id": plan.id,
                    "name": plan.name,
                    "price_cents": plan.price_cents,
                    "interval": plan.interval,
                    "stripe_price_id": plan.stripe_price_id  # Include stripe_price_id
                }
                for plan in plans
            ]
        }
    }


@router.post("/usage")
def api_usage(payload: CreateUsageRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ue = record_usage(db, user, payload.feature, payload.quantity, payload.subscription_id)
    return format_response("Usage recorded", {"usage_id": ue.id})


@router.get("/usage")
def api_get_usage(db: Session = Depends(get_db), user=Depends(get_current_user)):
    usages = get_usage(db, user)
    return format_response("Usage events", {"usage": [ {"id": u.id, "feature": u.event_type, "quantity": u.quantity, "created_at": u.created_at.isoformat()} for u in usages ]})


@router.get("/subscriptions")
def api_list_subscriptions(db: Session = Depends(get_db), user=Depends(get_current_user)):
    subs = list_subscriptions(db, user)
    return format_response("Subscriptions", {"subscriptions": [SubscriptionResponse.from_orm(s) for s in subs]})


@router.post("/cancel-subscription")
def api_cancel_subscription(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    subscription_id = payload.get("subscription_id")
    if not subscription_id:
        raise HTTPException(status_code=400, detail="subscription_id required")
    sub = cancel_subscription(db, user, subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return format_response("Canceled", {"subscription": SubscriptionResponse.from_orm(sub)})
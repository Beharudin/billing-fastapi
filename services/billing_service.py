from models.subscription import Subscription
from models.payment import Payment
from models.user import User
from datetime import datetime
from models.usage import UsageEvent
from models.plan import Plan

# Simple plan pricing map (price_id -> cents)
PLAN_PRICING = {
    "starter": 1000,  # $10.00
    "pro": 2500,      # $25.00
}

USAGE_RATE_CENTS = 10  # 10 cents per unit

def upsert_subscription(db, data):
    sub = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == data["id"]
    ).first()

    if not sub:
        sub = Subscription(
            user_id=data["metadata"]["user_id"],
            stripe_subscription_id=data["id"],
            status=data["status"],
            plan=data["items"]["data"][0]["price"]["id"],
            current_period_end=datetime.fromtimestamp(data["current_period_end"])
        )
        db.add(sub)
    else:
        sub.status = data["status"]

    db.commit()
    db.refresh(sub)
    return sub


def log_payment(db, event):
    # event may be an invoice or a checkout.session etc. Normalize fields.
    metadata = event.get("metadata") or {}
    user_id = metadata.get("user_id")

    # If no user_id in metadata, try to resolve via Stripe customer id
    if not user_id:
        customer = event.get("customer")
        if customer:
            user = db.query(User).filter(User.stripe_customer_id == customer).first()
            if user:
                user_id = user.id

    # amount may be in cents (Stripe) — convert to dollars for DB
    amount_cents = event.get("amount_paid") or event.get("total") or event.get("amount") or 0
    try:
        amount = float(amount_cents) / 100.0
    except Exception:
        amount = 0.0

    payment_intent = event.get("payment_intent") or event.get("payment") or event.get("id")
    currency = event.get("currency") or "usd"
    status = event.get("status") or "succeeded"

    payment = Payment(
        user_id=user_id,
        stripe_payment_intent=payment_intent,
        amount=amount,
        currency=currency,
        status=status,
    )
    db.add(payment)
    db.commit()


def subscribe(db, user, plan_id: str):
    sub = Subscription(
        user_id=user.id,
        stripe_subscription_id=None,
        status="active",
        plan=plan_id,
        current_period_end=datetime.utcnow()
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    return sub


def record_usage(db, user, feature: str, quantity: int = 1, subscription_id: str | None = None):
    ue = UsageEvent(
        tenant_id=user.tenant_id,
        event_type=feature,
        quantity=quantity
    )
    db.add(ue)
    db.commit()
    db.refresh(ue)
    return ue


def get_all_plans(db):
    return db.query(Plan).all()


def get_usage(db, user):
    return db.query(UsageEvent).filter(UsageEvent.tenant_id == user.tenant_id).all()


def list_subscriptions(db, user):
    return db.query(Subscription).filter(Subscription.user_id == user.id).all()


def cancel_subscription(db, user, subscription_id: str):
    sub = db.query(Subscription).filter(Subscription.id == subscription_id, Subscription.user_id == user.id).first()
    if not sub:
        return None
    sub.status = "canceled"
    db.commit()
    db.refresh(sub)
    return sub
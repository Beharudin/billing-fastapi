from workers.celery_app import celery
from services.billing_service import upsert_subscription, log_payment, subscribe
from core.database import SessionLocal
from models.webhook_event import WebhookEvent
from models.user import User
from datetime import datetime
import json


@celery.task(bind=True, name="tasks.webhook_tasks.process_event", max_retries=5, default_retry_delay=30)
def process_event(self, event_id: str, event_type: str, data: dict):
    db = SessionLocal()

    try:
        # Idempotency: has this Stripe event been processed?
        we = db.query(WebhookEvent).filter(WebhookEvent.stripe_event_id == event_id).first()
        if we and we.processed:
            return "already_processed"

        if not we:
            we = WebhookEvent(
                stripe_event_id=event_id,
                event_type=event_type,
                payload=json.dumps(data),
                processed=False
            )
            db.add(we)
            db.commit()
            db.refresh(we)

        # Handle event types
        # 1) checkout.session.completed: attach customer to user if metadata contains user_id
        if event_type == "checkout.session.completed":
            metadata = data.get("metadata") or {}
            user_id = metadata.get("user_id")
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    # store stripe customer id on user
                    user.stripe_customer_id = data.get("customer")
                    db.commit()

        # 2) invoice.payment_succeeded / invoice.paid
        elif event_type in ("invoice.payment_succeeded", "invoice.paid"):
            # record payment and activate user
            try:
                log_payment(db, data)
            except Exception:
                # logging failure should be retried
                raise

            customer = data.get("customer")
            if customer:
                user = db.query(User).filter(User.stripe_customer_id == customer).first()
                if user:
                    user.is_active = True
                    db.commit()

        # 3) invoice.payment_failed
        elif event_type == "invoice.payment_failed":
            customer = data.get("customer")
            if customer:
                user = db.query(User).filter(User.stripe_customer_id == customer).first()
                if user:
                    user.is_active = False
                    db.commit()

        # 4) customer.subscription.deleted or customer.subscription.updated
        elif event_type.startswith("customer.subscription"):
            upsert_subscription(db, data)

        # mark processed
        we.processed = True
        we.processed_at = datetime.utcnow()
        db.commit()
        return "processed"

    except Exception as exc:
        db.rollback()
        try:
            # let Celery retry for transient errors
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            raise
    finally:
        db.close()


from workers.celery_app import celery
from services.billing_service import upsert_subscription, log_payment
from core.database import SessionLocal


@celery.task(name="webhook.process")
def process_webhook(event_type: str, data: dict):

    db = SessionLocal()

    try:
        if event_type.startswith("customer.subscription"):
            upsert_subscription(db, data)

        elif event_type == "invoice.payment_succeeded":
            log_payment(db, data)

    finally:
        db.close()
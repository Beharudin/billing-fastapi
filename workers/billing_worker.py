from workers.celery_app import celery
import stripe
from core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


@celery.task(name="billing.sync_usage", autoretry_for=(Exception,), retry_backoff=True)
def sync_usage(subscription_item_id: str, quantity: int):

    stripe.SubscriptionItem.create_usage_record(
        subscription_item_id,
        quantity=quantity,
        timestamp="now",
        action="increment"
    )
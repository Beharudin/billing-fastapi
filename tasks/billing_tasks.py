from workers.celery_app import celery
import stripe

@celery.task
def sync_usage_to_stripe(stripe_subscription_item_id: str, quantity: int):

    stripe.SubscriptionItem.create_usage_record(
        stripe_subscription_item_id,
        quantity=quantity,
        timestamp="now",
        action="increment"
    )
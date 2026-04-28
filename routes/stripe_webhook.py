from fastapi import APIRouter, Request, HTTPException
from core.config import settings
import stripe
from tasks.webhook_tasks import process_event

router = APIRouter(prefix="/stripe", tags=["Stripe Webhook"])


@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook")

    # quickly enqueue the event for background processing
    event_id = event.get("id")
    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    # push to worker with id for idempotency
    process_event.delay(event_id, event_type, data)

    return {"status": "queued"}
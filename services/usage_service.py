from models.usage import UsageEvent

def record_usage(db, tenant_id: str, event_type: str, quantity: int = 1):
    event = UsageEvent(
        tenant_id=tenant_id,
        event_type=event_type,
        quantity=quantity
    )
    db.add(event)
    db.commit()
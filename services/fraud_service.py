def detect_fraud(db, user_id: str):

    recent_payments = db.execute("""
        SELECT COUNT(*) FROM payments
        WHERE user_id = :user_id
        AND created_at > NOW() - INTERVAL '10 minutes'
    """, {"user_id": user_id}).scalar()

    if recent_payments > 5:
        return True  # suspicious
    return False
from core.stripe_client import create_customer, create_checkout_session

def get_or_create_customer(user):
    if user.stripe_customer_id:
        return user.stripe_customer_id

    customer = create_customer(user.email)
    return customer.id

def start_checkout(user, price_id: str):
    customer_id = get_or_create_customer(user)
    return create_checkout_session(customer_id, price_id)

def change_subscription_plan(subscription_id: str, new_price_id: str):

    return stripe.Subscription.modify(
        subscription_id,
        proration_behavior="create_prorations",
        items=[{
            "price": new_price_id
        }]
    )
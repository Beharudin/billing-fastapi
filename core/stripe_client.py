import stripe
from core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_customer(email: str):
    return stripe.Customer.create(email=email)

def create_checkout_session(customer_id: str, price_id: str):
    return stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url="https://your-production-url.com/success",
        cancel_url="https://your-production-url.com/cancel",
    )

def create_price(name: str, price_cents: int, interval: str):
    # create price for an existing product name/product id
    product = stripe.Product.create(name=name)
    return stripe.Price.create(
        unit_amount=price_cents,
        currency="usd",
        recurring={"interval": interval},
        product=product.id
    )

def create_product(name: str):
    return stripe.Product.create(name=name)

def create_price_for_product(product_id: str, price_cents: int, interval: str):
    return stripe.Price.create(
        unit_amount=price_cents,
        currency="usd",
        recurring={"interval": interval},
        product=product_id,
    )
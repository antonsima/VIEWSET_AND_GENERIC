import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY

def create_stripe_product(name, description=None):
    try:
        product = stripe.Product.create(
            name=name,
            description=description or "",
        )
        return product
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe error while creating product: {str(e)}")

def create_stripe_price(product_id, unit_amount, currency="rub"):
    try:
        price = stripe.Price.create(
            product=product_id,
            unit_amount=int(unit_amount * 100),
            currency=currency,
        )
        return price
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe error while creating price: {str(e)}")

def create_stripe_checkout_session(price_id, success_url, cancel_url):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe error while creating checkout session: {str(e)}")

def retrieve_stripe_session(session_id):
    try:
        return stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe error while retrieving session: {str(e)}")
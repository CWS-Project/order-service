import stripe
import os
from datetime import datetime

stripe.api_key = os.getenv("STRIPE_API_KEY")


def create_payment_id(
        amount: float, 
        currency: str, 
        description: str, 
        user_id: str, 
    ) -> str:
    print(f"Creating payment intent for {amount} {currency} for user {user_id}")
    intent = stripe.PaymentIntent.create(
        amount=int(amount*100),
        currency=currency.lower(),
        description=description,
        automatic_payment_methods={"enabled": True}
    )

    stripe.PaymentIntent.modify(
        intent["id"], 
        metadata={
            "user_id": user_id,
        }
    )

    return intent['id']


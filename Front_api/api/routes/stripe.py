import json
import stripe
from fastapi import FastAPI ,APIRouter ,Request, Header, HTTPException
from typing import Optional
from dotenv import load_dotenv
from core.stripe import core_update_stripe_subscription
import os
load_dotenv()
WEBHOOK_SECRET=os.getenv("STRIPE_WEBHOOK")
STRIPE_SECRET_KEY=os.getenv("STRIPE_SECRET_KEY")
print("WEBHOOK_SECRET:", WEBHOOK_SECRET)
router = APIRouter()

@router.post("/webhooks/stripe/subscription")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
):
    """
    Webhook Stripe : reçoit les événements (ex: checkout.session.completed).
    On vérifie la signature, puis on agit selon event.type.
    """
    if not stripe_signature:
        print("signature manquante")
        raise HTTPException(status_code=400, detail="Signature manquante")

    payload = await request.body()
    payload_data = json.loads(payload)
    print("payload_data -->", payload_data)
    
    # Data tu update stripe,in db
    userId = payload_data["data"]["object"].get("client_reference_id", None) # user id syntetica not stripe
    customerId = payload_data["data"]["object"].get("customer", None) # user id syntetica not stripe
    subscriptionId = payload_data["data"]["object"].get("subscription", None) # user id syntetica not stripe
    # price = payload_data["data"]["object"].get("amount_subtotal", str(-1)) # user id syntetica not stripe
    print("userId -->", userId)
    subscription =None
     # 1) Vérifier la signature (IMPORTANT)
    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=stripe_signature, secret=WEBHOOK_SECRET
        )


        
        if subscriptionId:
        # Récupérer l'abonnement + items/price/product si tu veux mapper le plan
            subscription = stripe.Subscription.retrieve(
                subscriptionId,
                api_key=STRIPE_SECRET_KEY,
                
            )
            print("subscription -->", subscription)
        currentPeriodEnd = subscription["items"]["data"]["current_period_end"]
        interval = subscription["items"]["data"]["plan"]["interval"]
      
        # Mise à jour de la souscription stripe dans la base de données
        core_update_stripe_subscription(userId=userId, stripeSubscriptionId=subscriptionId,  stripeCustomerId=customerId , 
        stripePriceId=interval,currentPeriodEnd=currentPeriodEnd, status="active", suscriptionType="Pro")
        



    except Exception as e:
        print("signature invalide 2", e)
        raise HTTPException(status_code=400, detail=f"Signature invalide: {e}")

    # 2) Router par type d'événement
    event_type = event["type"]

    if event_type == "checkout.session.completed":
        # Paiement réussi pour Checkout (y compris Payment Link no-code)
        session = event["data"]["object"]
        # Ce que tu peux récupérer :
        # - session["client_reference_id"] (si tu as ajouté ?client_reference_id=USER_ID au Payment Link)
        # - session["metadata"] (si tu as créé la session via API et mis des metadata)
        # - session["amount_total"], session["payment_intent"], etc.

        order_id = None

        # Option A : tu passais l'order_id dans metadata (Checkout via API)
        md = session.get("metadata") or {}
        order_id = md.get("order_id")
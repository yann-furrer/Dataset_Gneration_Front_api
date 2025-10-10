import json
from fastapi.responses import JSONResponse
import stripe
import httpx
from fastapi import FastAPI, APIRouter, Request, Header, HTTPException
from typing import Optional
from dotenv import load_dotenv
from core.stripe import core_update_stripe_subscription
import os

sub_info = json.load(open("./subSysteminfo.json"))

load_dotenv()
DEV_SERVICE_URL = os.getenv("DEV_SERVICE_URL")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_PRD")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
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

    # Data tu update stripe,in db
    userId = payload_data["data"]["object"].get(
        "client_reference_id", None
    )  # user id syntetica not stripe
  
    subscriptionId = payload_data["data"]["object"].get(
        "subscription", None
    )  # user id syntetica not stripe
    subscription = None

    # 1) Vérifier la signature (IMPORTANT)
    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=stripe_signature, secret=WEBHOOK_SECRET
        )
        # print(event)
    except Exception as e:
        print("signature invalide 2", e)
        raise HTTPException(status_code=400, detail=f"Signature invalide: {e}")

    # 2) Router par type d'événement
    event = event["data"]["object"]
    payment_link = event["payment_link"]
    if payment_link == "plink_1SGFE5RqxJWcutRZAXLVY6Sv":  # cas d'ajout de credit
        # print("payment_link -->", payment_link)
        httpx.post(f"{DEV_SERVICE_URL}/add_credit")
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{DEV_SERVICE_URL}/add_credit",
                content=payload,  # ⚠️ le même corps BRUT
                headers={
                    "Stripe-Signature": stripe_signature,  # ⚠️ le même header
                    "Content-Type": "application/json",
                },
                timeout=10,
            )
            print(
                "forward status:",
                resp.status_code,
                "location:",
                resp.headers.get("location"),
            )

            return JSONResponse({"forwarded": True, "status": resp.status_code})

    if subscriptionId:
        # Récupérer l'abonnement + items/price/product si tu veux mapper le plan
        subscription = stripe.Subscription.retrieve(
            subscriptionId,
            api_key=STRIPE_SECRET_KEY,
        )

        # Choisi en fonction du forfait le nombre de lignes max
        nb_row_max_suscribed = 10000
        suscription_type = "Free"

        if sub_info["Basic"]["id_m"] == payment_link:
            nb_row_max_suscribed = sub_info["Basic"]["maxRows"]
            suscription_type = "Basic"
        elif sub_info["Basic"]["id_y"] == payment_link:
            nb_row_max_suscribed = sub_info["Basic"]["maxRows"]
            suscription_type = "Basic"
        elif sub_info["Pro"]["id_m"] == payment_link:
            nb_row_max_suscribed = sub_info["Pro"]["maxRows"]
            suscription_type = "Pro"
        elif sub_info["Pro"]["id_y"] == payment_link:
            nb_row_max_suscribed = sub_info["Pro"]["maxRows"]
            suscription_type = "Pro"

        currentPeriodEnd = subscription["items"]["data"][0]["current_period_end"]
        interval = subscription["items"]["data"][0]["plan"]["interval"]
        stripe_customer_id = event["customer"]
      
        core_update_stripe_subscription(
            userId=userId,
            stripeSubscriptionId=subscriptionId,
            stripeCustomerId=stripe_customer_id,
            stripePriceId=interval,
            currentPeriodEnd=currentPeriodEnd,
            status="active",
            suscriptionType=suscription_type,
            nbRowMaxSuscribed=nb_row_max_suscribed,
        )

        return JSONResponse({"updated": True})
    return JSONResponse({"error": "no subscriptionId"}, status_code=400)

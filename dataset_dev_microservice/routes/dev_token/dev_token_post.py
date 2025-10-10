import json
import os
import sys
import stripe
from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from fastapi.security import HTTPBearer
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from core.checking import (
    check_dev_token_validity,
    get_session_token,
    get_token_by_user_id,
)

from core.dev_token.dev_token_update import core_add_api_credit_on_user

from core.dev_token.dev_token_insert import generate_token, core_insert_api_token



load_dotenv()
PRICE_FOR_HUNDRED_ROWS = 0.02  # 1$ for 100 rows
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_PRD")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
print("WEBHOOK_SECRET:", WEBHOOK_SECRET)
router = APIRouter()
security = HTTPBearer()



#Appelé uniquement par la route stripe dans le front 
# si un crédit doit être ajouté  lors d'un paiement réussi via webhook
@router.post("/add_credit")
async def add_credit(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
):
    payload = await request.body()

    # 1) Vérifier la signature (IMPORTANT)
    try:
        event =stripe.Webhook.construct_event(
            payload=payload, sig_header=stripe_signature, secret=WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Signature invalide Credit can not be added: {e}")
    
    event = event["data"]["object"]
    amount_total: float = float(event.get("amount_subtotal", 0) / 100)  # in cents
    nb_rows_credited: int = (amount_total) / PRICE_FOR_HUNDRED_ROWS * 100  # 100 rows
    user_id: str = event.get("client_reference_id", "")  # user id syntetica not stripe

    result = core_add_api_credit_on_user(user_id, nb_rows_credited)
    if result is False:
        raise HTTPException(status_code=400, detail="Error while updating quota used")



# route utiliser par le front pour mettre à jour le quota utilisé
@router.post("/update_token_quota/{token}")
async def update_token_used(
    token: str,
    new_quota_used_to_sum: int,
    user_id: str = Depends(get_session_token),
    _=Depends(check_dev_token_validity),
):
    token = get_token_by_user_id(token)
    response: bool = core_add_api_credit_on_user(token, new_quota_used_to_sum)
    if response is False:
        HTTPException(status_code=400, detail="Error while updating quota used")
    return {"message": "Dev token updated!"}



# Vérifie si le token est valide
@router.post(
    "/dev/generate_token",
    summary="Génère un token développeur",
    description="Cette route permet de générer un token développeur pour accéder à l'API",
)
async def dev_token(
    user_id: str = Depends(get_session_token),
):
    token = generate_token()
    limit = -1
    response: bool = core_insert_api_token(user_id, limit)

    if response is False:
        HTTPException(status_code=409, detail="A developer token already exists")
    else:
        return {"message": "Dev token granted!", "token": token, "limit": limit}

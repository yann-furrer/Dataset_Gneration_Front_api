import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from fastapi import HTTPException


from database.queries.stripe import update_stripe_subscription


def core_update_stripe_subscription(
    userId: str,
    stripeSubscriptionId: str,
    stripeCustomerId: str,
    stripePriceId: str,
    status: str,
    currentPeriodEnd: str,
    suscriptionType: str,
    nbRowMaxSuscribed: int,
) -> bool:
    """
    Update stripe subscription
    """
    result_request = update_stripe_subscription(
        userId,
        stripeSubscriptionId,
        stripeCustomerId,
        stripePriceId,
        status,
        datetime.datetime.fromtimestamp(currentPeriodEnd),
        suscriptionType,
        nbRowMaxSuscribed,
    )

    if result_request:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while updating stripe subscription",
            headers={"WWW-Authenticate": "Bearer"},
        )

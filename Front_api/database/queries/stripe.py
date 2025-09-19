
import os , sys, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config import session, text


UPDATE_STRIPE_SUBSCRIPTION = """
UPDATE public."StripeSubscription" SET "userId" = :userId, "stripeSubscriptionId" = :stripeSubscriptionId, 
"stripeCustomerId" = :stripeCustomerId, "stripePriceId" = :stripePriceId, 
"status" = :status, "currentPeriodEnd" = :currentPeriodEnd, "updatedAt" = :updatedAt, 
"suscriptionType" = :suscritpionType, nbRowMaxSuscribed = :nbRowMaxSuscribed, nbRowsUsed = 0
WHERE "userId" = :userId;
"""

def update_stripe_subscription(userId: str, stripeSubscriptionId: str, stripeCustomerId: str, stripePriceId: str, stripeProductId: str,
    status: str, currentPeriodEnd: str, suscriptionType: str, nbRowMaxSuscribed: int
                               ) -> bool:
    """
    Update stripe subscription
    """
    try:
        session.execute(
            text(UPDATE_STRIPE_SUBSCRIPTION),
            {
                "stripeSubscriptionId": stripeSubscriptionId,
                "stripeCustomerId": stripeCustomerId,
                "stripePriceId": stripePriceId,
                "stripeProductId": stripeProductId,
                "userId": userId,
                "status": status,
                "currentPeriodEnd": currentPeriodEnd,
                "suscriptionType": suscriptionType,
                "nbRowMaxSuscribed": nbRowMaxSuscribed,
            },
        )
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print("Error while updating stripe subscription", e)
        return False


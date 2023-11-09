# Create your views here.
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from estate_plans.models import EstateTransaction
from estate_utilities.models import UtilityTransaction
from estate_utilities.utils import update_utility_transaction
from estate_webhooks.models import Webhook
from estates.utils import verify_flutterwave_reference, verify_paystack_reference


def utility_transaction_helper(utility_transaction, amount):
    # Check if the transaction is Flutterwave
    if utility_transaction.payment_type == "FLUTTERWAVE":
        # update and verify the transaction
        if verify_flutterwave_reference(utility_transaction.transaction_reference):
            update_utility_transaction(
                utility_transaction=utility_transaction,
                success=True, amount=amount)
    elif utility_transaction.payment_type == "PAYSTACK":
        # If the payment type is paystack then we have to verify for paystack
        if verify_paystack_reference(utility_transaction.transaction_reference):
            update_utility_transaction(
                utility_transaction=utility_transaction,
                success=True, amount=amount)
    else:
        # Just set the transaction to failed
        update_utility_transaction(
            utility_transaction=utility_transaction,
            success=False, amount=amount)


def estate_transaction_helper(estate_transaction):
    # Check if the transaction was mad with flutterwave
    if estate_transaction.payment_type == "FLUTTERWAVE":
        if verify_flutterwave_reference(estate_transaction.transaction_reference):
            estate_transaction.status = "SUCCESS"
            estate_transaction.save()
            # Update the estate subscription also
            estate_transaction.update_estate_subscription()
    elif estate_transaction.payment_type == "PAYSTACK":
        if verify_paystack_reference(estate_transaction.transaction_reference):
            estate_transaction.status = "SUCCESS"
            estate_transaction.save()
            # Update the estate subscription also
            estate_transaction.update_estate_subscription()
    else:
        estate_transaction.status = "FAILED"
        estate_transaction.save()


def webhook_amount_and_tx_ref(data):
    """
    this checks and return if the data is being sent by flutterwave or paystack
    :param data:
    :return:
    """
    # if the transaction is from flutterwave
    if data.get("flw_ref"):
        return {
            "amount": data.get("amount"),
            "tx_ref": data.get("tx_ref"),
        }
    return None


class WebhookAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Get or Create the webhook response sent from flutterwave or paystack
        webhook, created = Webhook.objects.get_or_create(
            data=self.request.data
        )
        # Get the transaction reference
        data = self.request.data.get("data")
        # this returns a json in this format {"amount":12,"tx_ref":EstateIQ-utility-1673},
        amount_and_tx_ref = webhook_amount_and_tx_ref(data=data)
        if not amount_and_tx_ref:
            # Check if it returns none
            return Response(status=200)
        transaction_reference = data.get("tx_ref")
        amount = data.get("amount")
        # Get the type of transaction reference  EstateIQ-utility-16737979956 :  EstateIQ-plan-16737979956
        transaction_type = transaction_reference.split("-")[1]
        # If the transaction is for utility
        if transaction_type == "utility":
            utility_transaction = UtilityTransaction.objects.filter(
                transaction_reference=transaction_reference
            ).first()
            if utility_transaction:
                # modify the transaction
                utility_transaction_helper(utility_transaction=utility_transaction, amount=float(amount))
        # If the transaction is for plan
        elif transaction_type == "plan":
            estate_transaction = EstateTransaction.objects.filter(
                transaction_reference=transaction_reference
            ).first()
            if estate_transaction:
                # Check if the plan being paid for transaction amount is up to the plan
                # I added 10 naira to the price just for little issues that may occur
                if estate_transaction.plan.price > amount + 10:
                    return Response(status=200)
                # modify and update estate subscription
                estate_transaction_helper(estate_transaction=estate_transaction)
        return Response(status=200)

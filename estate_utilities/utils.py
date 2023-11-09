from datetime import timedelta

from django.utils import timezone


def convert_payment_frequency_to_date(frequency):
    if frequency == "MONTHLY":
        due_date = timedelta(days=30) + timezone.now()
        return due_date
    elif frequency == "QUARTERLY":
        due_date = timedelta(days=30 * 3) + timezone.now()
        return due_date

    elif frequency == "HALF_YEARLY":
        due_date = timedelta(days=30 * 6) + timezone.now()
        return due_date

    elif frequency == "YEARLY":
        due_date = timedelta(days=365) + timezone.now()
        return due_date


def update_utility_transaction(utility_transaction, success: bool, amount: float):
    """
    This function is used to verify and update a utility transaction on flutterwave
    :param amount: The amount the user paid
    :param success: True or False
    :param utility_transaction:
    :return:
    """
    # This returns a boolean if the transaction is valid
    if success:
        # Only update if the transaction has not been successful
        if utility_transaction.status != "SUCCESS":
            utility_transaction.status = "SUCCESS"
            utility_transaction.amount = amount
            utility_transaction.paid_date = timezone.now()
            # Get the due date by converting the words for example MONTHLY to a month from now
            due_date = convert_payment_frequency_to_date(
                utility_transaction.estate_utility.payment_frequency)
            # To prevent error but the due date must be returned
            if due_date:
                utility_transaction.due_date = due_date
            utility_transaction.save()
            print("Reach here")
            return True
    else:
        # If not valid then the transaction fails
        utility_transaction.status = "FAILED"
        utility_transaction.amount = amount
        utility_transaction.save()
        return False

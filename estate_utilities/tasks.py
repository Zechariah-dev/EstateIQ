from datetime import timedelta

from celery import shared_task


def penalise_users_on_estate_utilities():
    """
    this custom function is used to filter all the estate penalty created and
    penalise users who haven't paid for that estate penalty
    :return:
    """
    from estate_utilities.models import EstateUtilityPenalty
    estate_penalties = EstateUtilityPenalty.objects.all()
    for penalty in estate_penalties:
        # Get the due date converted to days in django timedelta
        week_days = 7
        month_days = 30
        year_days = 365
        due_date = penalty.timestamp
        if penalty.unpaid_period == "WEEK":
            due_date += timedelta(days=week_days * penalty.unpaid_in)
        elif penalty.unpaid_period == "MONTH":
            due_date += timedelta(days=month_days * penalty.unpaid_in)
        elif penalty.unpaid_period == "YEAR":
            due_date += timedelta(days=year_days * penalty.unpaid_in)

        # After getting the due date now i need to get the estate user
        # from the penalty that are due
        estate = penalty.estate
        # fixme: for now i am excluding the admin
        for estate_user in estate.estateuser_set.all().exclude(user_type="ADMIN"):
            # if the user haven't paid then he doesn't have the grace
            # period  but if he has then he has the grace period
            print()
            estate_user_utility_transaction = estate_user.utilitytransaction_set.filter(
                estate_utility=penalty.estate_utility).first()
            if estate_user_utility_transaction:
                # check if the user due date is less than the due date
                if not estate_user_utility_transaction.due_date < due_date:
                    return True
            # start revoking the user permission
            for revoke in penalty.revoke_list:
                if revoke == "ON_TO_ONE_MESSAGE":
                    estate_user.on_to_one_message = False
                elif revoke == "UTILITY_PORTAL":
                    estate_user.utility_portal = False
                elif revoke == "EMERGENCY_SERVICE":
                    estate_user.emergency_service = False
                elif revoke == "GATE_PASS":
                    estate_user.gate_pass = False
                estate_user.save()
    return True


@shared_task
def remove_penalty_not_existing_on_utility_penalty():
    """
    this is used to remove penalty that does not exist on the estate utility penalty
    :return:
    """
    from estate_users.models import EstateUser
    estate_users = EstateUser.objects.all().exclude(user_type="ADMIN")
    for estate_user in estate_users:
        # Get on to one message if it blocked for that estate user
        estate_penalty_exist = estate_user.estate.estateutilitypenalty_set.filter(
            revoke__icontains="ON_TO_ONE_MESSAGE").exists()
        if not estate_penalty_exist:
            # estate_users.update(on)
            estate_user.on_to_one_message = True
            estate_user.save()

        # Get on utility_portal if it blocked for that estate user
        estate_penalty_exist = estate_user.estate.estateutilitypenalty_set.filter(
            revoke__icontains="UTILITY_PORTAL").exists()
        if not estate_penalty_exist:
            estate_user.utility_portal = True
            estate_user.save()

        # Get on emergency_service if it blocked for that estate user
        estate_penalty_exist = estate_user.estate.estateutilitypenalty_set.filter(
            revoke__icontains="EMERGENCY_SERVICE").exists()
        if not estate_penalty_exist:
            estate_user.emergency_service = True
            estate_user.save()

        # Get on gate_pass if it blocked for that estate user
        estate_penalty_exist = estate_user.estate.estateutilitypenalty_set.filter(
            revoke__icontains="GATE_PASS").exists()
        if not estate_penalty_exist:
            estate_user.gate_pass = True
            estate_user.save()

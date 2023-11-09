from celery import shared_task


@shared_task
def create_notification_for_reminder(message):
    from estate_user_notifications.models import EstateUserNotification, EstateUser

    # loop through all the estate users
    for estate_user in EstateUser.objects.all():
        estate_user_profile, created = EstateUserNotification.objects.get_or_create(
            estate_user=estate_user,
            message=message,
            notification_type="REMINDER",
            redirect_url=f"https://estateiq.ng/{estate_user.user_type}/tasks/{estate_user.estate.estate_id}"
        )


@shared_task
def create_notification_for_advert(message):
    from estate_user_notifications.models import EstateUser
    from estate_user_notifications.models import EstateUserNotification

    # loop through all the estate users
    for estate_user in EstateUser.objects.all():
        estate_user_profile, created = EstateUserNotification.objects.get_or_create(
            estate_user=estate_user,
            message=message,
            notification_type="ADVERT",
            redirect_url=f"https://estateiq.ng/{estate_user.user_type}/tasks/{estate_user.estate.estate_id}"
        )


@shared_task
def create_notification_for_announcement(message):
    from estate_user_notifications.models import EstateUser
    from estate_user_notifications.models import EstateUserNotification

    # loop through all the estate users
    for estate_user in EstateUser.objects.all():
        estate_user_profile, created = EstateUserNotification.objects.get_or_create(
            estate_user=estate_user,
            message=message,
            notification_type="ANNOUNCEMENT",
            redirect_url=f"https://estateiq.ng/{estate_user.user_type}/tasks/{estate_user.estate.estate_id}"
        )

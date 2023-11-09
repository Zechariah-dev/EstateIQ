import random
import string
import time

from celery import shared_task
from decouple import config
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

EstateIQ_INFO_MAIL = config("EstateIQ_INFO_MAIL")
EstateIQ_CUSTOMER_SUPPORT_MAIL = config("EstateIQ_CUSTOMER_SUPPORT_MAIL")


@shared_task
def send_created_estate_user(
        estate_name,
        user_category,
        first_name,
        last_name,
        email,
        mobile,
        user_type,
        inverter_user_type,
        password,
        inviter_first_name,
        inviter_last_name):
    # Create the correct word to be used on the message
    if inverter_user_type == "ADMIN":
        correct_word = "an"
    elif inverter_user_type == "RESIDENT":
        correct_word = "a"
    else:
        correct_word = "a"

    html_message = f"""

    Hello {first_name} {last_name}, <br/><br/>
    {inviter_first_name} {inviter_last_name} has invited you to join this estate - {estate_name} on EstateIQ <br/>
    Kindly use the link below to <a href='https://estateiq.ng/login'>Login</a>
    <br/><br/>

<ul>
    <li> Firstname: {first_name}</li>
    <li> Lastname: {last_name}</li>
    <li> Email: {email}</li>
    <li> Mobile: {mobile}</li>
    <li> Password: {password}</li>

</ul>


<br/><br/>

Regards, <br/>
EstateIQ Team <br/> <br/>
This email has been sent to persons who have requested to create accounts
on the EstateIQ platform.<br/><br/>
If you didn't register, please click
<a href='https://estateiq.ng/unsubscribe/'>Unsubscribe</a>

                """
    html_message = render_to_string(
        'email_template.html',
        {
            'message': html_message
        })
    send_mail(
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        subject="Invitation Message",
        message="",
        html_message=html_message
    )


@shared_task
def send_user_account_activated(
        estate_name,
        first_name,
        email):
    # Create the correct word to be used on the message

    html_message = f"""
               Hello {first_name}, <br/><br/>
               Your request to join this estate - {estate_name} on EstateIQ has been approved by the Estate Admin. <br/><br/>
               Kindly use the link below to login into the EstateIQ account to start using.  <br/><br/>
               <a href='https://estateiq.ng/login'>Login</a> <br/><br/>
                Regards, <br/>
                EstateIQ Team <br/><br/>
                This email has been sent to people who have requested to create accounts on the EstateIQ platform .<br/><br/>  
                If you didn’t request to join, please click <a href='https://estateiq.ng/unsubscribe/'>Unsubscribe</a>
                """
    html_message = render_to_string(
        'email_template.html',
        {
            'message': html_message
        })
    send_mail(
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        subject="Approved to Join Estate Message",
        message="",
        html_message=html_message
    )


@shared_task
def estate_user_bulk_upload(data, estate_id, estate_user_id):
    """
    this is used to make estate bulk upload
    :param data:  the data
    :param estate_id:  estate id  uuid
    :param estate_user_id: estate user id  uuid
    :return:

    """
    from estates.models import Estate
    from estate_users.models import EstateUser

    estate = Estate.objects.filter(id=estate_id).first()
    if not estate:
        return
    estate_user = EstateUser.objects.filter(id=estate_user_id).first()
    if not estate_user:
        return
        # loop through the data
    for item in data:
        # Generate random strings in ten letters
        password = ''.join(random.choices(string.ascii_lowercase +
                                          string.digits, k=10))
        # Create the Django User
        from estate_users.utils import create_user
        new_user = create_user(first_name=item.get("first_name"),
                               last_name=item.get("last_name"), email=item.get("email"),
                               mobile=item.get("mobile"), password=password)
        # after creating the new user add an estate user
        if not new_user:
            continue
        time.sleep(5)
        # Create the estate user under the estate
        from estate_users.utils import create_estate_user

        new_estate_user = create_estate_user(
            estate=estate,
            created_by_user=estate_user,
            user=new_user,
            user_category="OTHERS",
            user_type="RESIDENT",
            address=item.get("address"),
            status="ACTIVE",
            relationship=None,
            designation=None
        )
        if not new_estate_user:
            continue
        # Send the user a message on the account created
        send_created_estate_user.delay(
            estate_name=estate.name,
            user_category="user_category",
            first_name=item.get("first_name"),
            last_name=item.get("last_name"),
            email=item.get("email"),
            mobile=item.get("mobile"),
            password=password,
            user_type=new_estate_user.user_type,
            inverter_user_type=estate_user.user_type,
            inviter_first_name=estate_user.user.first_name,
            inviter_last_name=estate_user.user.last_name
        )

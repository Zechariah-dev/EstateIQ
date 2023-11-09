from celery import shared_task
from decouple import config
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

EstateIQ_INFO_MAIL = config("EstateIQ_INFO_MAIL")
EstateIQ_CUSTOMER_SUPPORT_MAIL = config("EstateIQ_CUSTOMER_SUPPORT_MAIL")


@shared_task
def send_verify_email_task(email, first_name, last_name, user_id):
    """
    This sends an email to the logged-in user for verification
    """
    html_message = f"""
       Hello {first_name},<br/><br/>
       Kindly confirm your email by clicking 
       <a href='https://estateiq.ng/verify_user?user_id={user_id}'>"Confirm"</a>
       <br/><br/>
        Regards, <br/>
        EstateIQ Team <br/> <br/>
        
       This email has been sent to persons who have requested to create accounts 
        on the EstateIQ platform.<br/><br/>  If you didn't register, please click
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
        subject="EstateIQ Verify Account",
        message="",
        html_message=html_message,
        fail_silently=False
    )


@shared_task
def send_welcome_message(email, first_name, user_type, estate_id):
    """
    this is used to send welcome message to the user signing up
    :param email:
    :param first_name:
    :return:
    """
    html_message = f"""
    Hello {first_name},<br/><br/>
    We are glad to have you on board!!! Here's how to get you started <br/>
    Click  <a href='https://estateiq.ng/{user_type}/settings/'>My Profile</a> <br/><br/>
    Regards,<br/>
    EstateIQ Team <br/><br/>
    This email has been sent to persons who have requested to create accounts 
    on the EstateIQ platform.<br/> If you didn't register, please click
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
        subject="Welcome Message",
        message=html_message,
        html_message=html_message,
        fail_silently=False
    )


@shared_task
def send_request_to_join_estate(admin_email, first_name, last_name, admin_first_name, estate_name, estate_id):
    """
    this is used to send a message to the owner of the estate
    :param email:
    :param first_name:
    :return:
    """
    admin_first_name = admin_first_name.title()
    html_message = f"""
    Hello {admin_first_name},<br/><br/>
    {first_name} {last_name} wants to join your estate - {estate_name} on EstateIQ <br/>
    Kindly use this <a href='https://estateiq.ng/{estate_id}/activate-users/'>link</a> to approve or reject this request 
      <br/><br/>
    
    Regards,<br/>
    EstateIQ Team <br/><br/>
    This email has been sent to persons who have requested to create accounts 
    on the EstateIQ platform.<br/>  <br/>
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
        recipient_list=[admin_email],
        subject="Request to Join Estate Message",
        message=html_message,
        html_message=html_message,
        fail_silently=False
    )


@shared_task
def send_user_to_wait_till_active(estate_name, email, first_name):
    """
    this is used to send a message to the owner of the estate
    :param estate_name:
    :param email:
    :param first_name:
    :return:
    """
    html_message = f"""
    Hello {first_name},<br/><br/>
    Your request to join estate - {estate_name} on EstateIQ is pending approval.<br/><br/>
    You will be notified as soon as your request is approved.<br/><br/>
    
    Thank You,<br/><br/>
    Regards<br/>
    EstateIQ Team <br/><br/>
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
        subject="Approval",
        message=html_message,
        html_message=html_message,
        fail_silently=False
    )


@shared_task
def send_otp_to_email_task(otp, email, first_name, last_name):
    """
    This sends an email to the logged-in user for verification
    """
    html_message = f"""
    Hello {first_name} {last_name}, <br/>
    
Please use this OTP to complete your request:{otp}.</br>
<span style="display:block; height:10px;"></span> 
If you haven't performed and action that requires an OTP please contact us. <br/><br/>

Regards,<br/>
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
        subject="OTP Requested",
        message=html_message,
        html_message=html_message,
        fail_silently=False
    )
    return True


@shared_task
def send_super_admin_activate_estate(estate_id, estate_name):
    """
    This sends an email to the logged-in user for verification
    """
    html_message = f"""
 Hello Admin,<br/> <br/>
    
A new estate activation request has been received: <br/>

<ul>
<li><strong>Estate ID:</strong> {estate_id}</li>
<li><strong>Estate Name:</strong> {estate_name}</li>
</ul>

Please review the details and take appropriate action to activate the estate. <br/> <br/>

 Regards,<br/>
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
    info_email = config("EstateIQ_INFO_MAIL")
    send_mail(
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[info_email],
        subject="Estate Activation Request",
        message=html_message,
        html_message=html_message,
        fail_silently=False
    )
    return True

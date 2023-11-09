from celery import shared_task
from decouple import config
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task
def send_waitlist_added_task(email):
    """
    This sends an email to the waitlist
    """
    html_message = f"""
Hello, <br/>

We're thrilled to inform you that you've been added to the EstateIQ wait-list! You're now part of an exclusive group that will be the first to know about our upcoming service. <br/>

Stay tuned for updates and announcements. We'll keep you posted on our progress and let you know as soon as we're ready to launch. <br/>

If you have any questions or need assistance, feel free to reach out to our support team at support@estateiq.ng. <br/>

Thank you for your interest and support! <br/> <br/>

 Regards,<br/>
 EstateIQ Team <br/> <br/>
This email has been sent to persons who was added to  EstateIQ wait-list platform.<br/><br/>  
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
        subject="Welcome to the EstateIQ Waitlist!",
        message=html_message,
        html_message=html_message,
        fail_silently=False
    )
    return True


@shared_task
def send_super_admin_waitlist_added_task(wait_list_email):
    """
    This sends an email to the waitlist
    """
    html_message = f"""
Hello ,<br/>

We wanted to inform you that a new user with the following email address has joined the EstateIQ wait-list: <br/>

Email: {wait_list_email} <br/>

They will be among the first to hear about our upcoming service and updates. Please extend a warm welcome to them!<br/>

If you have any questions or need further information, feel free to reach out. <br/> <br/>


 Regards,<br/>
 EstateIQ Team <br/> <br/>
This email has been sent to persons who was added to  EstateIQ wait-list platform.<br/><br/>  
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
        subject="New User Joined the EstateIQ Wait list",
        message=html_message,
        html_message=html_message,
        fail_silently=False
    )
    return True

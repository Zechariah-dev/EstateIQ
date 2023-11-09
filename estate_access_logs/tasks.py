from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task
def send_access_code_task(email, first_name, last_name, status, guest_first_name, guest_last_name):
    """
    This sends an email to the logged-in user for verification
    """
    html_message = f"""
 Hello {first_name} {last_name},  <br/><br/>

Your guest ({guest_first_name} {guest_last_name}) has been {status} access.<br/> <br/>

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
        subject="Access Notification",
        message=html_message,
        html_message=html_message,
        fail_silently=False
    )
    return True

# granted/denied

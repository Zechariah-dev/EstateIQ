from celery import shared_task
from decouple import config
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task
def send_new_complaint_to_super_admin_task(
    case_id,
    estate_name,
    estate_id,
    complaint_title,
    senders_name,
    complaint_reason,
    complaint_message,
    complaint_status,
):
    # Create the correct word to be used on the message

    html_message = f"""
<p>Hello ,</p>

<p>A new complaint has been lodged on the EstateIQ platform. Below are the details of the complaint:</p>

<ul>
<li><strong>Complaint ID:</strong> {case_id}</li>
<li><strong>Estate:</strong> {estate_name}</li>
<li><strong>Estate ID:</strong> {estate_id}</li>
<li><strong>Title:</strong> {complaint_title}</li>
<li><strong>Sender:</strong> {senders_name}</li>
<li><strong>Priority:</strong> {complaint_reason}</li>
<li><strong>Message:</strong> {complaint_message}</li>
<li><strong>Status:</strong> {complaint_status}</li>
</ul>

<p>Please take appropriate action and respond to the complaint as needed.</p>

<p>Thank you for your attention.</p>
Regards, <br/>
EstateIQ Team <br/><br/>
This email has been sent to people who have requested to create accounts on the EstateIQ platform .<br/><br/>  
If you didn’t request to join, please click <a href='https://estateiq.ng/unsubscribe/'>Unsubscribe</a>
                """
    html_message = render_to_string("email_template.html", {"message": html_message})
    info_email = config("EstateIQ_INFO_MAIL")
    send_mail(
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[info_email],
        subject="New Complaint Received On EstateIQ",
        message="",
        html_message=html_message,
    )


@shared_task
def send_new_complaint_to_receiver_task(
    email,
    first_name,
    last_name,
    case_id,
    estate_name,
    estate_id,
    complaint_title,
    senders_name,
    complaint_reason,
    complaint_message,
    complaint_status,
):
    # Create the correct word to be used on the message
    html_message = f"""
<p>Hello {first_name} - {last_name},</p>

<p>A new complaint has been lodged on {estate_name} on the EstateIQ platform. Below are the details of the complaint:</p>

<ul>
<li><strong>Complaint ID:</strong> {case_id}</li>
<li><strong>Estate ID:</strong> {estate_id}</li>
<li><strong>Title:</strong> {complaint_title}</li>
<li><strong>Sender:</strong> {senders_name}</li>
<li><strong>Priority:</strong> {complaint_reason}</li>
<li><strong>Message:</strong> {complaint_message}</li>
<li><strong>Status:</strong> {complaint_status}</li>
</ul>

<p>Please take appropriate action and respond to the complaint as needed.</p>

<p>Thank you for your attention.</p>
Regards, <br/>
EstateIQ Team <br/><br/>
This email has been sent to people who have requested to create accounts on the EstateIQ platform .<br/><br/>  
If you didn’t request to join, please click <a href='https://estateiq.ng/unsubscribe/'>Unsubscribe</a>
                """
    html_message = render_to_string("email_template.html", {"message": html_message})
    send_mail(
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        subject="New Complaint Received On EstateIQ",
        message="",
        html_message=html_message,
    )

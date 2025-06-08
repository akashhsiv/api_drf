import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

# Set up logging
logger = logging.getLogger(__name__)
def send_otp_email(email, otp_code):
    """
    Send an OTP code to the user's email
    
    Args:
        email (str): Recipient's email address
        otp_code (str): The OTP code to send
    """
    subject = 'Your One-Time Password (OTP)'
    
    try:
        # Render HTML content
        html_content = render_to_string('emails/otp_email.html', {
            'otp_code': otp_code,
        })
        
        # Create text version (for non-HTML email clients)
        text_content = strip_tags(html_content)
        
        # Create email
        email_message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        
        # Attach HTML content
        email_message.attach_alternative(html_content, "text/html")
        
        # Send email
        email_message.send()
        logger.info(f"OTP email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending OTP email to {email}: {str(e)}")
        # For debugging purposes, print the OTP to console in development
        if settings.DEBUG:
            print(f"DEBUG - OTP for {email}: {otp_code}")
        return False
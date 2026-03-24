from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_otp_email(user_email, otp):
    """
    Sends OTP to user email. Returns True if sent, False if failed.
    """
    subject = "Your Feedora Verification Code"
    
    # Sender ka naam acha dikhane ke liye
    from_email = f"Feedora Team <{settings.EMAIL_HOST_USER}>"
    
    # 1. HTML Template Load karo
    # Make sure 'emails/otp_email.html' templates folder me ho
    html_content = render_to_string('email_template.html', {'otp': otp})
    
    # 2. Text Version (Un logo ke liye jinka HTML off hai)
    text_content = strip_tags(html_content)

    try:
        # 3. Email Object Setup
        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            [user_email]
        )
        
        # 4. HTML Attach karo
        email.attach_alternative(html_content, "text/html")
        
        # 5. Send
        email.send()
        print(f"✅ OTP Email sent to {user_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False
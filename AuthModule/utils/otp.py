import secrets
import hashlib
from datetime import timedelta
from django.utils import timezone

def generate_otp(length=6):
    """
    Generate secure numeric OTP
    """
    digits = "0123456789"
    return "".join(secrets.choice(digits) for _ in range(length))




def hash_otp(otp):
    """
    Hash OTP before saving in DB
    """
    return hashlib.sha256(otp.encode()).hexdigest()



def otp_expiry(minutes=5):
    return timezone.now() + timedelta(minutes=minutes)

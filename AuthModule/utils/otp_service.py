from AuthModule.models import EmailOTP
from .otp import generate_otp, hash_otp, otp_expiry


def create_and_store_otp(user, purpose="register"):
    """
    Generate OTP, hash it, store in DB
    Returns plain OTP (for email sending)
    """

    # generate OTP
    otp = generate_otp()

    # hash OTP
    hashed = hash_otp(otp)

    # save in DB
    EmailOTP.objects.create(
        user=user,
        otp_hash=hashed,
        purpose=purpose,
        expires_at=otp_expiry(),
    )

    return otp

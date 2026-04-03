from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model ,login , authenticate , logout 
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings
from AuthModule.utils.otp_service import create_and_store_otp
from AuthModule.utils.email_service import send_otp_email
from django.utils import timezone
from AuthModule.models import EmailOTP
from AuthModule.utils.otp import hash_otp
from UserModule.models import UserProfile
User = get_user_model()


def register_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")

        # create inactive user
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password
        )
        user.is_active = False
        user.save()

        # OTP create
        otp = create_and_store_otp(user)
        send_otp_email(user.email, otp)

        # ⭐ SESSION STORE
        
        request.session["email"] = email
        request.session.modified = True   # important
        request.session.save()            # force save

        print("SESSION SET:", request.session.get("verify_email"))

        return redirect("verify-otp")

    return render(request, "register.html")




def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")

        # authenticate user
        user = authenticate(request, email=email, password=password)

        if user is None:
            return render(request, "login.html", {
                "error": "Invalid email or password"
            })

        # block inactive users
        if not user.is_active:
            return render(request, "login.html", {
                "error": "Account not verified"
            })

        # login session
        login(request, user)

        return redirect("Dashboard")

    return render(request, "login.html")


def logout_view(request):
    logout(request )
    return redirect("login")

def send_test_email(request):
    send_mail(
        subject="Feedora Test Email",
        message="Email working successfully!",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.EMAIL_HOST_USER],
        fail_silently=False,
    )
    return HttpResponse("Email sent!")




User = get_user_model()


def verify_otp_view(request):

    # SESSION SE EMAIL LO
    email = request.session.get("email")

    print("SESSION EMAIL:", email)  # debug

    # session missing
    if not email:
        return HttpResponse("Session expired. Please register again.")

    if request.method == "POST":
        otp_input = request.POST.get("otp")

        if not otp_input:
            return render(request, "otp_verfiy.html", {
                "error": "Enter OTP"
            })

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "otp_verfiy.html", {
                "error": "User not found"
            })

        try:
            otp_record = EmailOTP.objects.filter(
                user=user,
                purpose="register",
                is_used=False
            ).latest("created_at")

        except EmailOTP.DoesNotExist:
            return render(request, "otp_verfiy.html", {
                "error": "OTP not found"
            })

        # expiry check
        if otp_record.expires_at < timezone.now():
            return render(request, "otp_verfiy.html", {
                "error": "OTP expired"
            })

       

        # success
        otp_record.is_used = True
        otp_record.save()

        user.is_active = True
        user.save()
        
        # ⭐ CREATE PROFILE AFTER VERIFY
        UserProfile.objects.get_or_create(user=user)
        login(request, user)

        # session cleanup (good practice)
        del request.session["email"]

        

    return render(request, "otp_verfiy.html")


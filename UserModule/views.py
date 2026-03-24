from django.shortcuts import render
from AuthModule.models import User
from . models import UserProfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# Create your views here.


def view_profile(request, username):

    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=user)

    return render(request, "view_profile.html", {
        "profile": profile
    })

@login_required
def update_profile(request, username):

    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=user)

    # security: user apna hi profile edit kare
    if request.user != user:
        return redirect("Dashboard")

    if request.method == "POST":

        profile.full_name = request.POST.get("full_name")
        profile.phone_number = request.POST.get("phone_number")
        profile.bio = request.POST.get("bio")
        profile.location = request.POST.get("location")
        profile.website = request.POST.get("website")
        profile.twitter = request.POST.get("twitter")
        profile.linkedin = request.POST.get("linkedin")
        profile.github = request.POST.get("github")

        # image upload handle
        if request.FILES.get("profile_photo"):
            profile.profile_photo = request.FILES.get("profile_photo")

        profile.save()

        return redirect("Profile", username=username)

    return render(request, "edit_profile.html", {"profile": profile})
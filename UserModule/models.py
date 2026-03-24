from django.db import models
from AuthModule.models import User
from PIL import Image
from io import BytesIO
from django.core.files import File


class UserProfile(models.Model):

    ROLE_CHOICES = (
        ("reader", "Reader"),
        ("writer", "Content Writer"),
        ("blogger", "Blogger"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=255)
    profile_photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    bio = models.TextField(blank=True)

    phone_number = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="reader")
    is_verified_creator = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def save(self, *args, **kwargs):

        # image compression logic
        if self.profile_photo:
            img = Image.open(self.profile_photo)

            # resize (max 300x300)
            img.thumbnail((300, 300))

            # convert to RGB if PNG
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            output = BytesIO()
            img.save(output, format="JPEG", quality=70)  # compression
            output.seek(0)

            self.profile_photo = File(output, name=self.profile_photo.name)

        super().save(*args, **kwargs)
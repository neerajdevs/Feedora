from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    # list page columns
    list_display = (
        "id",
        "user",
        "full_name",
        "role",
        "is_verified_creator",
        "created_at",
    )

    # sidebar filters
    list_filter = (
        "role",
        "is_verified_creator",
        "created_at",
    )

    # search box
    search_fields = (
        "user__email",
        "full_name",
        "phone_number",
        "location",
    )

    # editable fields directly in list view
    list_editable = (
        "role",
        "is_verified_creator",
    )

    # ordering
    ordering = ("-created_at",)

    # pagination
    list_per_page = 20

    # form layout
    fieldsets = (
        ("User Info", {
            "fields": ("user", "full_name", "profile_photo", "bio")
        }),

        ("Contact Info", {
            "fields": ("phone_number", "location", "website")
        }),

        ("Social Links", {
            "fields": ("twitter", "linkedin", "github")
        }),

        ("Permissions", {
            "fields": ("role", "is_verified_creator")
        }),

        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    # readonly fields
    readonly_fields = ("created_at", "updated_at")


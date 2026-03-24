from django.contrib import admin
from .models import User , EmailOTP
# Register your models here.

@admin.register(User)
class AdminAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "created_at")
    search_fields = ("username",)
    
admin.site.register(EmailOTP)
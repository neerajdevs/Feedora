from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True , null= True , blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    is_active = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    

class EmailOTP(models.Model):
    PURPOSE_CHOICES = (
        ('register', 'Register'),
        ('delete_blog', 'Delete Blog'),
        ('change_email', 'Change Email'),
        ('account_recovery', 'Account Recovery'),
        ('account_deletion', 'Account Deletion'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_hash = models.CharField(max_length=128)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.purpose}"

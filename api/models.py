from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)

import random
import string
from django.utils import timezone
from datetime import timedelta

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    otp_reset_code = models.CharField(max_length=6, null=True, blank=True)
    otp_reset_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.email

    def generate_otp(self):
        """Generate a new 6-digit OTP"""
        self.otp_reset_code = ''.join(random.choices(string.digits, k=6))
        self.otp_reset_expires_at = timezone.now() + timedelta(minutes=15)
        self.save()
        return self.otp_reset_code

    def is_otp_valid(self, otp):
        """Check if provided OTP is valid and hasn't expired"""
        if not self.otp_reset_code:
            return False
        if self.otp_reset_code != otp:
            return False
        if self.otp_reset_expires_at < timezone.now():
            return False
        return True

    def clear_otp(self):
        """Clear the OTP after successful password reset"""
        self.otp_reset_code = None
        self.otp_reset_expires_at = None
        self.save()

import logging
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
import random
import string
from django.utils import timezone
from datetime import timedelta
from django.core.validators import MinLengthValidator

# Set up logging
logger = logging.getLogger(__name__)

class UserRole(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
    ]
    
    # Role hierarchy - who can create which roles
    ROLE_HIERARCHY = {
        'superuser': ['admin'],
        'admin': ['manager'],
        'manager': ['cashier'],
        'cashier': []
    }
    
    # Permissions for each role
    ROLE_PERMISSIONS = {
        'admin': ['add_manager', 'view_manager', 'change_manager', 'delete_manager',
                 'add_cashier', 'view_cashier', 'change_cashier', 'delete_cashier'],
        'manager': ['add_cashier', 'view_cashier', 'change_cashier'],
        'cashier': ['view_cashier']
    }
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=dict)  # Store permissions as JSON
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
    
    def __str__(self):
        return self.get_role_display()
        
    @classmethod
    def get_creatable_roles(cls, user_role):
        """Get list of roles that can be created by the given role"""
        return cls.ROLE_HIERARCHY.get(user_role, [])

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a user with the given email and password.
        For customers, no special permissions are needed.
        """
        if not email:
            raise ValueError('The Email field must be set')
            
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('user_type', 'customer')
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_staff_user(self, email, password=None, **extra_fields):
        """
        Create and save a staff user with the given email and password.
        Requires role and created_by fields for staff users.
        """
        if not email:
            raise ValueError('The Email field must be set')
            
        role = extra_fields.get('role')
        created_by = extra_fields.get('created_by')
        
        if not role:
            raise ValueError('Staff users must have a role')
            
        # Only superusers can create the first admin
        if role.role == 'admin' and not created_by and not self.filter(role__role='admin').exists():
            if not (hasattr(created_by, 'is_superuser') and created_by.is_superuser):
                raise ValueError('Only superusers can create the first admin')
                
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('user_type', 'staff')
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'staff')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        # Create a default admin role if it doesn't exist
        from .models import UserRole
        admin_role, _ = UserRole.objects.get_or_create(
            role='admin',
            defaults={'description': 'Administrator with full access'}
        )
        
        extra_fields['role'] = admin_role
        return self.create_staff_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('staff', 'Staff'),
    ]
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Staff users only
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    
    # Staff-specific fields
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_users')
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_staff')
    
    # Customer-specific fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    otp_reset_code = models.CharField(max_length=6, null=True, blank=True)
    otp_reset_expires_at = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    @property
    def is_admin(self):
        return self.role and self.role.role == 'admin'
    
    @property
    def is_manager(self):
        return self.role and self.role.role == 'manager'
    
    @property
    def is_cashier(self):
        return self.role and self.role.role == 'cashier'
    
    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True
        if not self.role:
            return False
        return perm in self.role.permissions
    
    def has_module_perms(self, app_label):
        return self.is_staff or self.is_superuser
    
    def generate_otp(self):
        # Generate a 6-digit OTP
        self.otp_reset_code = ''.join(random.choices(string.digits, k=6))
        self.otp_reset_expires_at = timezone.now() + timedelta(minutes=15)  # 15 minutes expiry
        
        # Save the OTP to the database
        self.save(update_fields=['otp_reset_code', 'otp_reset_expires_at'])
        
        # Send the OTP via email
        from .utils import send_otp_email
        send_otp_email(self.email, self.otp_reset_code)
        
        return self.otp_reset_code
    
    def is_otp_valid(self, otp):
        if not self.otp_reset_code or not self.otp_reset_expires_at:
            return False
        return self.otp_reset_code == otp and timezone.now() < self.otp_reset_expires_at
    
    def clear_otp(self):
        self.otp_reset_code = None
        self.otp_reset_expires_at = None
        self.save()

class CustomerManager(CustomUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(user_type='customer')
        
    def create_customer(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('user_type', 'customer')
        return self.create_user(email, password, name=name, **extra_fields)

class Customer(User):
    objects = CustomerManager()
    
    class Meta:
        proxy = True
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
    def save(self, *args, **kwargs):
        self.user_type = 'customer'
        super().save(*args, **kwargs)

class StaffManager(CustomUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(user_type='staff')
        
    def create_staff(self, email, name, role=None, password=None, **extra_fields):
        extra_fields.setdefault('user_type', 'staff')
        if role:
            extra_fields['role'] = role
        return self.create_user(email, password, name=name, **extra_fields)

class Staff(User):
    objects = StaffManager()
    
    class Meta:
        proxy = True
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'
    
    def save(self, *args, **kwargs):
        # Prevent recursion
        generating_otp = kwargs.pop('generating_otp', False)
        
        # Only set user_type if it's not already set
        if not self.pk or self.user_type != 'staff':
            self.user_type = 'staff'
        
        # Call the parent's save method
        super().save(*args, **kwargs)
        
        # Only generate OTP if explicitly requested (e.g., during password reset)
        if generating_otp:
            self.otp_reset_code = ''.join(random.choices(string.digits, k=6))
            self.otp_reset_expires_at = timezone.now() + timedelta(minutes=15)
            
            logger.info(f"Generated OTP for user {self.email}")
            logger.info(f"Expires at: {self.otp_reset_expires_at}")
            
            # Save only the OTP fields to the database
            super().save(update_fields=['otp_reset_code', 'otp_reset_expires_at'])
            return self.otp_reset_code

    def is_otp_valid(self, otp):
        """Check if provided OTP is valid and hasn't expired"""
        if not self.otp_reset_code or not self.otp_reset_expires_at:
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
        self.save(update_fields=['otp_reset_code', 'otp_reset_expires_at'])

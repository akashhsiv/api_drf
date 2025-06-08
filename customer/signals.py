from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserRole

User = get_user_model()

@receiver(post_save, sender=User)
def set_default_user_role(sender, instance, created, **kwargs):
    """
    Signal to set default role for staff users if not set during creation
    """
    if created and instance.is_staff and not instance.role:
        # Assign cashier role by default to new staff members
        cashier_role, _ = UserRole.objects.get_or_create(
            role='cashier',
            defaults={
                'description': 'Cashier role with basic permissions',
                'permissions': {}
            }
        )
        instance.role = cashier_role
        instance.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create user profile after user creation
    """
    if created:
        # Create user profile or perform other post-creation tasks
        pass

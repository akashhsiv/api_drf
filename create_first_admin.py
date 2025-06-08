import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_drf.settings')
django.setup()

from customer.models import User, UserRole

def create_first_admin():
    # Create admin role if it doesn't exist
    admin_role, created = UserRole.objects.get_or_create(
        role='admin',
        defaults={
            'description': 'Administrator with full access',
            'permissions': {}
        }
    )
    
    # Create the first superuser
    admin = User.objects.create(
        email='admin@example.com',
        name='Admin User',
        is_staff=True,
        is_superuser=True,
        user_type='staff',
        role=admin_role
    )
    admin.set_password('admin123')
    admin.save()
    
    print("Superuser created successfully!")
    print(f"Email: admin@example.com")
    print(f"Password: admin123")

if __name__ == "__main__":
    create_first_admin()

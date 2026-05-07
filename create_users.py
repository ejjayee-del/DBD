import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dbd_config.settings')
django.setup()

from accounts.models import CustomUser

# Create superuser if it doesn't exist
if not CustomUser.objects.filter(username='admin').exists():
    user = CustomUser.objects.create_superuser(
        username='admin',
        email='admin@barangay.local',
        password='admin123',
        first_name='System',
        last_name='Administrator',
        role='admin'
    )
    user.can_view_history = True
    user.can_print_certificates = True
    user.can_edit_records = True
    user.can_delete_records = True
    user.save()
    print("✓ Superuser 'admin' created successfully!")
    print("  Username: admin")
    print("  Password: admin123")
else:
    print("✓ Superuser 'admin' already exists!")

# Create some sample users  
if not CustomUser.objects.filter(username='secretary1').exists():
    user = CustomUser.objects.create_user(
        username='secretary1',
        email='secretary@barangay.local',
        password='secretary123',
        first_name='Ejjayee',
        last_name='Quino',
        role='secretary'
    )
    user.can_view_history = True
    user.can_print_certificates = True
    user.save()
    print("✓ Secretary user created!")

if not CustomUser.objects.filter(username='officer1').exists():
    user = CustomUser.objects.create_user(
        username='officer1',
        email='officer@barangay.local',
        password='officer123',
        first_name='Dwight',
        last_name='Geralde',
        role='officer'
    )
    user.can_view_history = True
    user.can_print_certificates = True
    user.can_edit_records = True
    user.save()
    print("✓ Officer user created!")

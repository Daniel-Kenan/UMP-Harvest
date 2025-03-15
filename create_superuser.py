import os
import django
from django.contrib.auth import get_user_model

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
django.setup()

# Get the User model
User = get_user_model()

# Automatically create a superuser if it does not exist
def create_superuser():
    username = os.getenv("DJANGO_ADMIN_USERNAME", "admin")
    email = os.getenv("DJANGO_ADMIN_EMAIL", "admin@example.com")
    password = os.getenv("DJANGO_ADMIN_PASSWORD", "adminpassword")

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"Superuser '{username}' created successfully!")
    else:
        print(f"Superuser '{username}' already exists.")

# Ensure this script only runs when explicitly executed, not on every Django command
if __name__ == "__main__":
    create_superuser()

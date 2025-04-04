# debug.py
import os
import django

# Set the default settings module for the 'django' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VirtualLCS.settings')

# Setup Django
django.setup()

# Now you can import your models
from Discussion.models import Session  # Adjust the import based on your app structure

def main():
    # Your debugging logic here
    sessions = Session.objects.all()
    for session in sessions:
        print(session)

if __name__ == "__main__":
    main()
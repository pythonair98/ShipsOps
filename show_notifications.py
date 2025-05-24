import os
import django
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShipsManagment.settings')
django.setup()

# Import models
from ShipOps.models import Notification

def show_sample_notifications(count=5):
    """
    Show a sample of notifications from the database
    """
    total = Notification.objects.count()
    print(f"Total notifications in database: {total}")
    
    # Get random sample
    if total > 0:
        sample_size = min(count, total)
        # Get random IDs
        all_ids = list(Notification.objects.values_list('id', flat=True))
        sample_ids = random.sample(all_ids, sample_size)
        
        # Fetch the notifications
        sample_notifications = Notification.objects.filter(id__in=sample_ids)
        
        print(f"\nShowing {sample_size} random notifications:\n")
        
        for i, notification in enumerate(sample_notifications, 1):
            print(f"{i}. [{notification.notification_type}] {notification.title}")
            print(f"   Message: {notification.message}")
            print(f"   Status: {'Read' if notification.is_read else 'Unread'}")
            print(f"   Created: {notification.created_at}")
            print(f"   Related to: {notification.related_object_type or 'None'} "
                  f"(ID: {notification.related_object_id or 'None'})")
            print("")
    else:
        print("No notifications found in the database.")

if __name__ == "__main__":
    show_sample_notifications(10) 
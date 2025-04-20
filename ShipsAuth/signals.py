from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, UserRole


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a UserProfile whenever a User is created.
    """
    if created:
        # Find or create default viewer role
        default_role, _ = UserRole.objects.get_or_create(
            name='viewer',
            defaults={
                'description': 'Read-only access to the system'
            }
        )
        
        # Create the user profile
        UserProfile.objects.create(
            user=instance,
            role=default_role,
            department='Default',
            can_view_contracts=True,
            can_edit_contracts=False,
            can_view_invoices=True,
            can_edit_invoices=False
        ) 
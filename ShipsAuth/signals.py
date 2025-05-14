from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, UserRole, UserPermissions


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
            department='Default'
        )

@receiver(post_save, sender=User)
def create_user_permissions(sender, instance, created, **kwargs):
    """Create UserPermissions when a new user is created"""
    if created:
        # Create permissions object
        user_permissions = UserPermissions.objects.create(user=instance)
        
        # If user has a role, set default permissions for that role
        if hasattr(instance, 'ops_profile') and instance.ops_profile.role:
            instance.ops_profile.role.set_default_permissions(user_permissions)
            user_permissions.save()

@receiver(post_save, sender=User)
def save_user_permissions(sender, instance, **kwargs):
    """Save UserPermissions when user is saved"""
    if hasattr(instance, 'permissions'):
        instance.permissions.save() 
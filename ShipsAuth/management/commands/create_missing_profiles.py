from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ShipsAuth.models import UserProfile, UserRole


class Command(BaseCommand):
    help = 'Create missing user profiles for users'

    def handle(self, *args, **options):
        # Find default role (or create one if none exists)
        default_role, created = UserRole.objects.get_or_create(
            name='viewer',
            defaults={
                'description': 'Read-only access to the system'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created default "viewer" role'))

        # Find users without ops_profile
        users_without_profile = []
        for user in User.objects.all():
            try:
                # This will raise the exception if profile doesn't exist
                user.ops_profile
            except User.ops_profile.RelatedObjectDoesNotExist:
                users_without_profile.append(user)

        # Create profiles
        count = 0
        for user in users_without_profile:
            UserProfile.objects.create(
                user=user,
                role=default_role,
                department='Default',
                can_view_contracts=True,
                can_edit_contracts=False,
                can_view_invoices=True,
                can_edit_invoices=False
            )
            count += 1

        if count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {count} missing user profiles')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('All users already have profiles')
            ) 
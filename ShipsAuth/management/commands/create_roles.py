from django.core.management.base import BaseCommand
from ShipsAuth.models import UserRole

class Command(BaseCommand):
    help = 'Create predefined roles in the system'

    def handle(self, *args, **options):
        roles = [
            {
                'name': 'system_admin',
                'description': 'Full system access and control. Can manage all aspects of the system including users, roles, and settings.'
            },
            {
                'name': 'operations_manager',
                'description': 'Manages shipping operations, contracts, vessels, and crew. Has extensive permissions for operational tasks.'
            },
            {
                'name': 'finance_officer',
                'description': 'Handles financial aspects including invoices, billing, and financial reports. Focused on financial operations.'
            },
            {
                'name': 'operations_staff',
                'description': 'Handles day-to-day operations. Can view and create basic shipping documents and maintenance records.'
            },
            {
                'name': 'viewer',
                'description': 'Read-only access to contracts, invoices, and other system data. Suitable for auditors and stakeholders.'
            },
            {
                'name': 'support_staff',
                'description': 'Provides support to users. Has access to view system data and upload documents.'
            }
        ]

        created_count = 0
        updated_count = 0

        for role_data in roles:
            role, created = UserRole.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created role: {role.get_name_display()}')
                )
            else:
                # Update description if role exists
                role.description = role_data['description']
                role.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Updated role: {role.get_name_display()}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed roles. Created: {created_count}, Updated: {updated_count}'
            )
        ) 
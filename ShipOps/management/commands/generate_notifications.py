import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from ShipOps.models import Contract, Invoice, Vessel, VesselMaintenance, VesselDocument
from ShipOps.utils import (
    create_notification,
    create_notification_for_users,
    create_notification_for_group
)


class Command(BaseCommand):
    help = 'Generates dummy notifications for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of notifications to generate per user'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=14,
            help='Maximum age of notifications in days'
        )

    def handle(self, *args, **options):
        count = options['count']
        max_days = options['days']
        
        # Get all users
        users = User.objects.all()
        if not users.exists():
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return
        
        # Get some objects to reference in notifications
        contracts = list(Contract.objects.all())
        invoices = list(Invoice.objects.all())
        vessels = list(Vessel.objects.all())
        maintenances = list(VesselMaintenance.objects.all())
        documents = list(VesselDocument.objects.all())
        
        # Check if we have enough data
        if not contracts:
            self.stdout.write(self.style.WARNING('No contracts found. Some notification types will be skipped.'))
        if not invoices:
            self.stdout.write(self.style.WARNING('No invoices found. Some notification types will be skipped.'))
        if not vessels:
            self.stdout.write(self.style.WARNING('No vessels found. Some notification types will be skipped.'))
        
        # Notification types
        notification_types = ['contract', 'invoice', 'vessel', 'maintenance', 'document', 'deadline', 'system', 'alert']
        
        # Sample notification templates
        templates = {
            'contract': [
                {
                    'title': 'Contract {id} created',
                    'message': 'A new contract for vessel {vessel} has been created by {user}.'
                },
                {
                    'title': 'Contract {id} updated',
                    'message': 'Contract for vessel {vessel} has been updated with new terms.'
                },
                {
                    'title': 'Contract {id} needs approval',
                    'message': 'Contract #{id} for vessel {vessel} is awaiting your approval.'
                },
                {
                    'title': 'Contract {id} expiring soon',
                    'message': 'Contract #{id} for vessel {vessel} will expire in {days} days.'
                }
            ],
            'invoice': [
                {
                    'title': 'New invoice #{id} created',
                    'message': 'A new invoice has been created for contract #{contract_id}.'
                },
                {
                    'title': 'Invoice #{id} due soon',
                    'message': 'Invoice #{id} for ${amount} is due in {days} days.'
                },
                {
                    'title': 'Invoice #{id} payment overdue',
                    'message': 'Payment for Invoice #{id} is overdue by {days} days.'
                },
                {
                    'title': 'Invoice #{id} has been paid',
                    'message': 'Payment for Invoice #{id} in the amount of ${amount} has been received.'
                }
            ],
            'vessel': [
                {
                    'title': 'Vessel {name} status update',
                    'message': 'Vessel {name} is now {status}.'
                },
                {
                    'title': 'Vessel {name} location updated',
                    'message': 'Vessel {name} has arrived at {port}.'
                },
                {
                    'title': 'Vessel {name} scheduled for maintenance',
                    'message': 'Vessel {name} is scheduled for {type} maintenance on {date}.'
                }
            ],
            'maintenance': [
                {
                    'title': 'Maintenance scheduled for {vessel}',
                    'message': '{type} maintenance has been scheduled for vessel {vessel} on {date}.'
                },
                {
                    'title': 'Maintenance completed for {vessel}',
                    'message': '{type} maintenance for vessel {vessel} has been completed.'
                },
                {
                    'title': 'Upcoming maintenance reminder',
                    'message': 'Reminder: {type} maintenance for vessel {vessel} is scheduled for {date}.'
                }
            ],
            'document': [
                {
                    'title': 'Document {title} expiring soon',
                    'message': 'Document {title} for vessel {vessel} will expire in {days} days.'
                },
                {
                    'title': 'New document uploaded',
                    'message': 'A new {doc_type} document has been uploaded for vessel {vessel}.'
                },
                {
                    'title': 'Document {title} has expired',
                    'message': 'Document {title} for vessel {vessel} has expired. Please renew immediately.'
                }
            ],
            'deadline': [
                {
                    'title': 'Approaching deadline: {title}',
                    'message': '{title} deadline is approaching in {days} days.'
                },
                {
                    'title': 'Deadline reminder: {title}',
                    'message': 'Reminder: {title} is due on {date}.'
                }
            ],
            'system': [
                {
                    'title': 'System maintenance scheduled',
                    'message': 'The system will be unavailable for maintenance on {date} from {start} to {end}.'
                },
                {
                    'title': 'New feature available',
                    'message': 'A new feature has been added to the system: {feature}.'
                },
                {
                    'title': 'Password expiration notice',
                    'message': 'Your password will expire in {days} days. Please change it soon.'
                }
            ],
            'alert': [
                {
                    'title': 'Critical alert: {title}',
                    'message': '{message}'
                },
                {
                    'title': 'Security alert',
                    'message': 'Unusual login activity detected from {location}.'
                },
                {
                    'title': 'Important announcement',
                    'message': '{message}'
                }
            ]
        }
        
        # Random data to fill in templates
        ports = ['Dubai Port', 'Port of Jebel Ali', 'Abu Dhabi Port', 'Sharjah Port', 'Fujairah Port', 'Khalifa Port', 'Port Rashid']
        maintenance_types = ['Routine', 'Emergency', 'Scheduled', 'Annual', 'Quarterly', 'Engine', 'Hull', 'Navigation System']
        document_types = ['Registration', 'Insurance', 'Classification', 'Safety', 'Inspection', 'Crew List', 'Port Authority', 'Customs']
        deadlines = ['Regulatory Compliance', 'Tax Filing', 'Insurance Renewal', 'Certification Renewal', 'Staff Training', 'Audit Preparation']
        features = ['Advanced Analytics Dashboard', 'Vessel Tracking Map', 'Document OCR Processing', 'Mobile App Access', 'API Integration', 'Custom Reports']
        locations = ['Dubai, UAE', 'New York, USA', 'London, UK', 'Singapore', 'Hong Kong', 'Mumbai, India', 'Unknown Location']
        alert_titles = ['System Error', 'Database Issue', 'Connection Problems', 'Data Synchronization Failure', 'Server Overload']
        alert_messages = [
            'Authentication service is experiencing issues. Some users may be unable to log in.',
            'Database performance issues detected. Operations may be slower than usual.',
            'Network connectivity issues detected. Some features may be unavailable.',
            'Critical system update required. Please contact IT department.',
            'Unusual system activity detected. Security team has been notified.'
        ]
        
        # Track how many notifications we've created
        created_count = 0
        
        # Create notifications for each user
        for user in users:
            self.stdout.write(f"Creating notifications for user: {user.username}")
            
            for _ in range(count):
                # Randomly select notification type
                notification_type = random.choice(notification_types)
                
                # Randomly select if notification is read
                is_read = random.choice([True, False, False])  # 2/3 chance of being unread
                
                # Random creation date in the past
                days_ago = random.randint(0, max_days)
                created_at = timezone.now() - timedelta(days=days_ago)
                
                # Is email sent?
                is_email_sent = random.choice([True, False])
                
                # Pick a template for this type
                if notification_type in templates and templates[notification_type]:
                    template = random.choice(templates[notification_type])
                    title_template = template['title']
                    message_template = template['message']
                    
                    # Data to fill the templates
                    data = {}
                    related_object_type = None
                    related_object_id = None
                    
                    # Contract notifications
                    if notification_type == 'contract' and contracts:
                        contract = random.choice(contracts)
                        data = {
                            'id': contract.id,
                            'vessel': contract.vessel,
                            'user': user.username,
                            'days': random.randint(1, 30)
                        }
                        related_object_type = 'contract'
                        related_object_id = contract.id
                    
                    # Invoice notifications
                    elif notification_type == 'invoice' and invoices:
                        invoice = random.choice(invoices)
                        data = {
                            'id': invoice.id,
                            'contract_id': invoice.contract.id if invoice.contract else 'Unknown',
                            'amount': round(invoice.price_usd, 2) if invoice.price_usd else 'Unknown',
                            'days': random.randint(1, 30)
                        }
                        related_object_type = 'invoice'
                        related_object_id = invoice.id
                    
                    # Vessel notifications
                    elif notification_type == 'vessel' and vessels:
                        vessel = random.choice(vessels)
                        data = {
                            'name': vessel.name,
                            'status': vessel.status,
                            'port': random.choice(ports),
                            'type': random.choice(maintenance_types),
                            'date': (timezone.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
                        }
                        related_object_type = 'vessel'
                        related_object_id = vessel.id
                    
                    # Maintenance notifications
                    elif notification_type == 'maintenance' and maintenances and vessels:
                        if maintenances:
                            maintenance = random.choice(maintenances)
                            vessel_name = maintenance.vessel.name
                            maintenance_type = maintenance.maintenance_type
                            vessel_id = maintenance.vessel.id
                        else:
                            vessel = random.choice(vessels)
                            vessel_name = vessel.name
                            maintenance_type = random.choice(maintenance_types)
                            vessel_id = vessel.id
                            
                        data = {
                            'vessel': vessel_name,
                            'type': maintenance_type,
                            'date': (timezone.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
                        }
                        related_object_type = 'vessel'
                        related_object_id = vessel_id
                    
                    # Document notifications
                    elif notification_type == 'document' and vessels:
                        if documents:
                            document = random.choice(documents)
                            title = document.title
                            vessel_name = document.vessel.name
                            vessel_id = document.vessel.id
                            doc_type = document.document_type
                        else:
                            vessel = random.choice(vessels)
                            title = f"{random.choice(document_types)} Certificate"
                            vessel_name = vessel.name
                            vessel_id = vessel.id
                            doc_type = random.choice(document_types)
                            
                        data = {
                            'title': title,
                            'vessel': vessel_name,
                            'days': random.randint(1, 30),
                            'doc_type': doc_type
                        }
                        related_object_type = 'vessel'
                        related_object_id = vessel_id
                    
                    # Deadline notifications
                    elif notification_type == 'deadline':
                        deadline = random.choice(deadlines)
                        data = {
                            'title': deadline,
                            'days': random.randint(1, 30),
                            'date': (timezone.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
                        }
                        
                        # Maybe relate to a contract or vessel
                        if random.choice([True, False]) and contracts:
                            contract = random.choice(contracts)
                            related_object_type = 'contract'
                            related_object_id = contract.id
                        elif vessels:
                            vessel = random.choice(vessels)
                            related_object_type = 'vessel'
                            related_object_id = vessel.id
                    
                    # System notifications
                    elif notification_type == 'system':
                        feature = random.choice(features)
                        maint_date = (timezone.now() + timedelta(days=random.randint(1, 14))).strftime('%Y-%m-%d')
                        start_time = f"{random.randint(0, 23):02d}:00"
                        end_time = f"{random.randint(0, 23):02d}:00"
                        
                        data = {
                            'date': maint_date,
                            'start': start_time,
                            'end': end_time,
                            'feature': feature,
                            'days': random.randint(1, 30)
                        }
                    
                    # Alert notifications
                    elif notification_type == 'alert':
                        alert_title = random.choice(alert_titles)
                        alert_message = random.choice(alert_messages)
                        location = random.choice(locations)
                        
                        data = {
                            'title': alert_title,
                            'message': alert_message,
                            'location': location
                        }
                    
                    # Format the title and message with the data
                    try:
                        title = title_template.format(**data)
                        message = message_template.format(**data)
                        
                        # Create the notification
                        notification = create_notification(
                            user=user,
                            title=title,
                            message=message,
                            notification_type=notification_type,
                            related_object_type=related_object_type,
                            related_object_id=related_object_id,
                            send_email=False  # Don't actually send emails for dummy data
                        )
                        
                        # Manually set created_at and is_read
                        notification.created_at = created_at
                        notification.is_read = is_read
                        notification.is_email_sent = is_email_sent
                        notification.save()
                        
                        created_count += 1
                    except KeyError as e:
                        self.stdout.write(self.style.WARNING(f"Error formatting notification: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} dummy notifications')) 
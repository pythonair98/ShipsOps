from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Q
from django.utils import timezone

from datetime import timedelta
from .models import Notification, Contract, Invoice, Vessel, VesselMaintenance, VesselDocument, User


def create_notification(user, title, message, notification_type, related_object_type=None, related_object_id=None, send_email=False):
    """
    Create a notification for a user
    
    Args:
        user: User object or user ID
        title: Notification title
        message: Notification message
        notification_type: Type of notification
        related_object_type: Type of related object (optional)
        related_object_id: ID of related object (optional)
        send_email: Whether to send an email notification
    
    Returns:
        Notification object
    """
    # Handle user as ID or object
    if isinstance(user, int):
        user = User.objects.get(id=user)
    
    # Create notification
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        related_object_type=related_object_type,
        related_object_id=related_object_id
    )
    
    # Send email if requested
    if send_email and user.email:
        try:
            subject = f"ShipsOps Notification: {title}"
            html_message = render_to_string('emails/notification_email.html', {
                'user': user,
                'notification': notification,
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else '/',
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=True
            )
            
            # Mark email as sent
            notification.is_email_sent = True
            notification.save(update_fields=['is_email_sent'])
        except Exception as e:
            print(f"Failed to send email notification: {e}")
    
    return notification


def create_notification_for_users(users, title, message, notification_type, related_object_type=None, related_object_id=None, send_email=False):
    """Create the same notification for multiple users"""
    notifications = []
    for user in users:
        notifications.append(
            create_notification(
                user, title, message, notification_type, 
                related_object_type, related_object_id, send_email
            )
        )
    return notifications


def create_notification_for_group(group_name, title, message, notification_type, related_object_type=None, related_object_id=None, send_email=False):
    """Create notifications for all users in a group"""
    from django.contrib.auth.models import Group
    
    try:
        group = Group.objects.get(name=group_name)
        users = group.user_set.all()
        return create_notification_for_users(
            users, title, message, notification_type, 
            related_object_type, related_object_id, send_email
        )
    except Group.DoesNotExist:
        return []


def check_approaching_deadlines(days_threshold=7):
    """
    Check for approaching deadlines and create notifications
    
    This function checks for:
    - Contracts about to expire
    - Documents about to expire
    - Upcoming maintenance tasks
    - Invoices near due date
    """
    today = timezone.now().date()
    threshold_date = today + timedelta(days=days_threshold)
    
    # Contracts approaching end date
    expiring_contracts = Contract.objects.filter(
        contract_end__date__range=[today, threshold_date],
        state__in=[0, 1]  # Only active contracts (pending or finance)
    ).select_related('created_by')
    
    for contract in expiring_contracts:
        days_left = (contract.contract_end.date() - today).days
        
        # Create notification for contract creator
        if contract.created_by:
            create_notification(
                contract.created_by,
                f"Contract ending soon: {contract.vessel}",
                f"Contract #{contract.id} for vessel {contract.vessel} will end in {days_left} days.",
                'deadline',
                'contract',
                contract.id,
                send_email=True
            )
            
        # Create notification for finance team if contract is in finance state
        if contract.state == 1:
            create_notification_for_group(
                'Finance',
                f"Contract ending soon: {contract.vessel}",
                f"Contract #{contract.id} for vessel {contract.vessel} will end in {days_left} days.",
                'deadline',
                'contract',
                contract.id,
                send_email=True
            )
    
    # Documents about to expire
    expiring_documents = VesselDocument.objects.filter(
        expiry_date__range=[today, threshold_date]
    ).select_related('vessel')
    
    for document in expiring_documents:
        days_left = (document.expiry_date - today).days
        
        # Create notification for admins
        create_notification_for_group(
            'Admins',
            f"Document expiring: {document.title}",
            f"Document {document.title} for vessel {document.vessel.name} will expire in {days_left} days.",
            'document',
            'vessel',
            document.vessel.id,
            send_email=True
        )
    
    # Upcoming maintenance
    upcoming_maintenance = VesselMaintenance.objects.filter(
        scheduled_date__range=[today, threshold_date],
        status__in=['scheduled', 'in_progress']
    ).select_related('vessel')
    
    for maintenance in upcoming_maintenance:
        days_left = (maintenance.scheduled_date - today).days
        
        # Create notification for maintenance team
        create_notification_for_group(
            'Maintenance',
            f"Upcoming maintenance: {maintenance.vessel.name}",
            f"Maintenance task '{maintenance.maintenance_type}' for vessel {maintenance.vessel.name} is scheduled in {days_left} days.",
            'maintenance',
            'vessel',
            maintenance.vessel.id,
            send_email=True
        )
    
    # Invoices near due date
    approaching_invoices = Invoice.objects.filter(
        due_date__range=[today, threshold_date],
        status=0  # Pending
    ).select_related('contract')
    
    for invoice in approaching_invoices:
        days_left = (invoice.due_date - today).days
        
        # Create notification for finance team
        create_notification_for_group(
            'Finance',
            f"Invoice payment due soon: #{invoice.id}",
            f"Invoice #{invoice.id} for contract #{invoice.contract.id} is due in {days_left} days.",
            'invoice',
            'invoice',
            invoice.id,
            send_email=True
        )

    return {
        'contracts': expiring_contracts.count(),
        'documents': expiring_documents.count(),
        'maintenance': upcoming_maintenance.count(),
        'invoices': approaching_invoices.count()
    }


def get_user_notifications(user, unread_only=False, limit=None):
    """Get notifications for a user"""
    query = Q(user=user)
    if unread_only:
        query &= Q(is_read=False)
    
    notifications = Notification.objects.filter(query).order_by('-created_at')
    
    if limit:
        notifications = notifications[:limit]
    
    return notifications


def mark_all_as_read(user):
    """Mark all notifications as read for a user"""
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)
    return Notification.objects.filter(user=user, is_read=False).count() == 0 
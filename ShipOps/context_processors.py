from .models import Notification

def notifications(request):
    """Context processor that adds notification data to all templates."""
    context = {
        'unread_notifications': False,
    }
    
    # Only add notification data for authenticated users
    if request.user.is_authenticated:
        # Check if there are any unread notifications
        has_unread = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).exists()
        
        context['unread_notifications'] = has_unread
        
    return context 
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps

def role_required(power_level):
    """
    Decorator to require a minimum occupation power level to access a view.
    
    Args:
        power_level (int): The minimum power level required to access the view.
        
    Usage:
        @role_required(5)
        def my_view(request):
            # View code here
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Try to get user's profile
            try:
                # First check for auth_profile (from ShipsAuth)
                if hasattr(request.user, 'auth_profile') and request.user.auth_profile.occupation:
                    user_power = request.user.auth_profile.occupation.power
                    if user_power <= power_level:
                        return view_func(request, *args, **kwargs)
                # If no access, show message and redirect
                messages.warning(request, "You don't have permission to access this page")
                return redirect('login')  # Or another appropriate page
            except Exception as e:
                # Handle any errors (e.g., if profile doesn't exist)
                messages.error(request, f"Error checking permissions: {str(e)}")
                return redirect('login')
        return _wrapped_view
    return decorator 
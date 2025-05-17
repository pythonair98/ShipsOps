from django.utils.deprecation import MiddlewareMixin
from .models import UserAction
from django.urls import resolve

class UserActionMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Only track actions for authenticated users
        if not request.user.is_authenticated:
            return response

        # Skip tracking for certain paths
        path = request.path
        if any(skip_path in path for skip_path in ['/static/', '/media/', '/admin/jsi18n/']):
            return response

        # Get the view function name
        try:
            view_func = resolve(path).func
            view_name = view_func.__name__
        except:
            view_name = 'unknown'

        # Map HTTP methods to action types
        method_to_action = {
            'GET': 'view',
            'POST': 'create' if 'new' in view_name or 'create' in view_name else 'update',
            'PUT': 'update',
            'DELETE': 'delete',
        }

        # Get action type from HTTP method
        action_type = method_to_action.get(request.method, 'other')

        # Get model name from URL path
        model_name = path.split('/')[1].capitalize() if len(path.split('/')) > 1 else 'Unknown'

        # Get object ID if available
        object_id = None
        if len(path.split('/')) > 2:
            try:
                object_id = int(path.split('/')[2])
            except ValueError:
                pass

        # Create action details
        details = f"{request.method} request to {path}"

        # Create the user action record
        UserAction.objects.create(
            user=request.user,
            action_type=action_type,
            model_name=model_name,
            object_id=object_id,
            details=details,
            ip_address=self.get_client_ip(request)
        )

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 
from django.utils.deprecation import MiddlewareMixin
from ShipOps.models import UserAction
from django.urls import resolve

class UserActivityMiddleware(MiddlewareMixin):
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

        # Exclude 'view' actions from logging
        if action_type == 'view':
            return response

        # Get model name from URL path
        model_name = path.split('/')[1].capitalize() if len(path.split('/')) > 1 else 'Unknown'

        # Get object ID if available
        object_id = None
        if len(path.split('/')) > 2:
            try:
                object_id = str(path.split('/')[2])  # Convert to string since model field is CharField
            except (ValueError, IndexError):
                pass

        # Create action details with more meaningful info
        action_details = {
            'view_name': view_name,
            'path': path,
            'method': request.method,
            'details': f"{action_type.title()} action by {request.user.username} on {model_name} (ID: {object_id}) via {request.method} at {path}"
        }

        # For POST/PUT, include form data (excluding sensitive fields)
        if request.method in ['POST', 'PUT']:
            action_details['form_data'] = {
                k: v for k, v in request.POST.items()
                if k not in ['csrfmiddlewaretoken', 'password']
            }

        # Create the user action record
        UserAction.objects.create(
            user=request.user,
            action_type=action_type,
            model_name=model_name,
            object_id=object_id,
            action_details=action_details,
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
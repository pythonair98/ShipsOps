from django.shortcuts import render, get_object_or_404, redirect
from .forms import LoginForm, RegisterForm
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from ShipsAuth.models import UserProfile, UserRole, UserPermissions
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
import json
# Create your views here.
def login_view(request):
    """
    View to handle user login.
    
    Handles both GET and POST requests. If the request method is POST, it authenticates the user.
    If authentication is successful, the user is logged in and redirected to the contract list page.
    If authentication fails, an error message is displayed.
    
    :param request: The HTTP request object.
    :return: Rendered 'login.html' template with login form.
    """
    # Check if user is already authenticated, redirect to contract list
    if request.user.is_authenticated:
        return redirect('contract_list')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                return redirect('contract_list')
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid form submission")
    else:
        form = LoginForm()
        
    return render(request, 'ShipsAuth/login.html', {'form': form})

def register_view(request):
    """
    View to handle user registration.
    
    Handles both GET and POST requests. If the request method is POST, it validates and saves the form.
    If successful, a new user is created with the hashed password, a success message is displayed,
    and the user is redirected to the login page.
    If the form is invalid, an error message is displayed.
    
    :param request: The HTTP request object.
    :return: Rendered 'register.html' template with registration form.
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "User registered successfully")
            return redirect('login')
        else:
            messages.error(request, "Invalid form submission")
    else:
        form = RegisterForm()
    return render(request, 'ShipsAuth/signup.html', {'form': form})


def logout_view(request):
    """
    View to handle user logout.
    
    Logs the user out and redirects to the login page.
    
    :param request: The HTTP request object.
    :return: Redirect to the login page.
    """
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect('login')

@login_required
def edit_user_view(request, user_id):
    """
    View to handle editing user information.
    
    Allows administrators to edit user details. If the request method is POST,
    it validates and saves the form. If successful, the user information is updated
    and a success message is displayed.
    
    :param request: The HTTP request object.
    :param user_id: The ID of the user to edit.
    :return: Rendered 'edit_user.html' template with the user form.
    """
    user = get_object_or_404(User, id=user_id)
    user_profile = get_object_or_404(UserProfile, user=user)
    
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # Save the user first
            user = form.save()
            
            # Update the user profile
            user_profile.role_id = request.POST.get('role')
            user_profile.department = request.POST.get('department')
            user_profile.save()
            
            messages.success(request, "User updated successfully")
            return redirect('ShipsAuth:user_list_auth')
        else:
            messages.error(request, "Invalid form submission")
            messages.error(request, form.errors.as_text())
    else:
        form = RegisterForm(instance=user)
    
    # Get unique departments for the dropdown
    departments = UserProfile.objects.values_list('department', flat=True).distinct()
    
    # Get all roles for the dropdown
    roles = UserRole.objects.all()
    
    return render(request, 'ShipsAuth/edit_user.html', {
        'form': form,
        'user_id': user_id,
        'departments': departments,
        'roles': roles,
        'user': user,
        'user_profile': user_profile
    })


@login_required
def delete_user_view(request, user_id):
    """
    View to handle user deletion.
    
    Allows administrators to delete users. If the request method is POST,
    it deletes the user and displays a success message.
    
    :param request: The HTTP request object.
    :param user_id: The ID of the user to delete.
    :return: Redirect to the user list page.
    """
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, "User deleted successfully")
        return redirect('/users/')  # Use absolute URL path
    
    return render(request, 'ShipsAuth/confirm_delete_user.html', {'user': user})


@login_required
def activate_user_view(request, user_id):
    """
    View to activate a user account.
    
    Allows administrators to activate a deactivated user account.
    
    :param request: The HTTP request object.
    :param user_id: The ID of the user to activate.
    :return: Redirect to the user list page.
    """
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    
    messages.success(request, f"User {user.username} has been activated successfully")
    return redirect('/users/')  # Use absolute URL path


@login_required
def deactivate_user_view(request, user_id):
    """
    View to deactivate a user account.
    
    Allows administrators to deactivate an active user account.
    
    :param request: The HTTP request object.
    :param user_id: The ID of the user to deactivate.
    :return: Redirect to the user list page.
    """
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    
    messages.success(request, f"User {user.username} has been deactivated successfully")
    return redirect('/users/')  # Use absolute URL path

@login_required
def reset_user_password_view(request, user_id):
    """
    View to reset a user's password.
    
    Allows administrators to reset a user's password to a new value.
    
    :param request: The HTTP request object.
    :param user_id: The ID of the user whose password will be reset.
    :return: Redirect to the user list page or render the reset password form.
    """
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            messages.success(request, f"Password for {user.username} has been reset successfully")
            return redirect('/users/')  # Use absolute URL path
        else:
            messages.error(request, "Passwords do not match")
    
    return render(request, 'ShipsAuth/reset_user_password.html', {'user': user})

@login_required
def user_list_view(request):
    """
    View to display a list of all users.
    
    Retrieves all User objects from the database and passes them to the 'users.html' template.
    
    :param request: The HTTP request object.
    :return: Rendered 'users.html' template with user data.
    """
    # Get all users
    users = User.objects.all().order_by('-date_joined')
    
    # Prepare context dictionary for template rendering
    context = {
        'users': users,
        'page_title': 'User Management'
    }
    
    return render(request, 'ShipsAuth/users.html', context)

@login_required
def user_list(request):
    """
    View for displaying all users with their information and permissions.
    Includes filtering capabilities and pagination.
    """
    # Get all users with their profiles and roles
    user_profiles = UserProfile.objects.select_related('user', 'role').all().order_by('user__first_name')
    
    # Get all roles for filter dropdown
    roles = UserRole.objects.all()
    
    # Get unique departments for filter dropdown
    departments = UserProfile.objects.values_list('department', flat=True).distinct()
    
    # Filter users if filters are applied
    name_filter = request.GET.get('name', '')
    role_filter = request.GET.get('role', '')
    department_filter = request.GET.get('department', '')
    permission_filter = request.GET.get('permission', '')
    
    if name_filter:
        user_profiles = user_profiles.filter(
            user__first_name__icontains=name_filter
        ) | user_profiles.filter(
            user__last_name__icontains=name_filter
        ) | user_profiles.filter(
            user__username__icontains=name_filter
        )
    
    if role_filter:
        user_profiles = user_profiles.filter(role_id=role_filter)
    
    if department_filter:
        user_profiles = user_profiles.filter(department=department_filter)
    
    if permission_filter:
        if permission_filter == 'contracts_view':
            user_profiles = user_profiles.filter(can_view_contracts=True)
        elif permission_filter == 'contracts_edit':
            user_profiles = user_profiles.filter(can_edit_contracts=True)
        elif permission_filter == 'invoices_view':
            user_profiles = user_profiles.filter(can_view_invoices=True)
        elif permission_filter == 'invoices_edit':
            user_profiles = user_profiles.filter(can_edit_invoices=True)
    
    # Paginate users
    paginator = Paginator(user_profiles, 15)  # Show 15 users per page
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    # Mock activity logs (in a real app, you would retrieve actual logs)
    activity_logs = [
        {
            'user': user.user,
            'action': 'Logged in',
            'details': 'User logged in from 192.168.1.1',
            'timestamp': user.user.last_login,
        }
        for user in user_profiles[:5] if user.user.last_login
    ]
    
    context = {
        'users': users,
        'roles': roles,
        'departments': departments,
        'activity_logs': activity_logs,
        # Preserve filters for pagination
        'name_filter': name_filter,
        'role_filter': role_filter,
        'department_filter': department_filter,
        'permission_filter': permission_filter,
    }
    
    return render(request, 'ShipsAuth/user_list.html', context)

@login_required
@require_http_methods(["GET"])
def get_user_permissions(request, user_id):
    """Get permissions for a specific user"""
    try:
        # Check if the requesting user has permission to view user permissions
        # Superusers can always view permissions
        if not (request.user.is_superuser or (hasattr(request.user, 'permissions') and request.user.permissions.can_view_users)):
            raise PermissionDenied("You don't have permission to view user permissions")
        
        # Get the target user's permissions
        user_permissions = UserPermissions.objects.get(user_id=user_id)
        
        # Convert permissions to dictionary
        permissions_dict = {
            field.name: getattr(user_permissions, field.name)
            for field in UserPermissions._meta.fields
            if field.name != 'user' and field.name != 'id'
        }
        
        return JsonResponse({
            'success': True,
            'permissions': permissions_dict
        })
    except UserPermissions.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User permissions not found'
        }, status=404)
    except PermissionDenied as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=403)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def update_user_permissions(request, user_id):
    """Update permissions for a specific user"""
    try:
        # Check if the requesting user has permission to edit user permissions
        # Superusers can always edit permissions
        if not (request.user.is_superuser or (hasattr(request.user, 'permissions') and request.user.permissions.can_edit_users)):
            raise PermissionDenied("You don't have permission to edit user permissions")
        
        # Parse the request body
        data = json.loads(request.body)
        
        # Get or create the target user's permissions
        user_permissions, created = UserPermissions.objects.get_or_create(user_id=user_id)
        
        # Update each permission
        for field in UserPermissions._meta.fields:
            if field.name in data and field.name != 'user' and field.name != 'id':
                setattr(user_permissions, field.name, data[field.name])
        
        # Save the changes
        user_permissions.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Permissions updated successfully'
        })
    except PermissionDenied as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=403)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_permission_groups(request):
    """Get all available permission groups"""
    try:
        # First check if the user has a permissions object
        if not hasattr(request.user, 'permissions'):
            # Create permissions object if it doesn't exist
            UserPermissions.objects.create(user=request.user)
            request.user.refresh_from_db()
        
        # Get permission groups regardless of user's permissions
        # This allows viewing the structure even if they can't edit
        permission_groups = UserPermissions.get_permission_groups()
        
        # Superusers can always edit permissions
        can_edit = request.user.is_superuser or (hasattr(request.user, 'permissions') and request.user.permissions.can_edit_users)
        
        return JsonResponse({
            'success': True,
            'permission_groups': permission_groups,
            'can_edit': can_edit
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def role_list(request):
    """View for displaying all roles and their permissions"""
    roles = UserRole.objects.all()
    return render(request, 'ShipsAuth/role_list.html', {'roles': roles})

@login_required
@require_http_methods(["GET"])
def get_role_permissions(request, role_id):
    """Get permissions for a specific role"""
    try:
        # Check if the requesting user has permission to view role permissions
        if not (request.user.is_superuser or (hasattr(request.user, 'permissions') and request.user.permissions.can_edit_users)):
            raise PermissionDenied("You don't have permission to view role permissions")
        
        role = UserRole.objects.get(id=role_id)
        
        # Create a temporary UserPermissions object to get default permissions
        temp_permissions = UserPermissions()
        role.set_default_permissions(temp_permissions)
        
        # Convert permissions to dictionary
        permissions_dict = {
            field.name: getattr(temp_permissions, field.name)
            for field in UserPermissions._meta.fields
            if field.name not in ['user', 'id']
        }
        
        return JsonResponse({
            'success': True,
            'role_name': role.get_name_display(),
            'permissions': permissions_dict
        })
    except UserRole.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Role not found'
        }, status=404)
    except PermissionDenied as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=403)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def update_role_permissions(request, role_id):
    """Update permissions for a specific role"""
    try:
        # Check if the requesting user has permission to edit role permissions
        if not (request.user.is_superuser or (hasattr(request.user, 'permissions') and request.user.permissions.can_edit_users)):
            raise PermissionDenied("You don't have permission to edit role permissions")
        
        # Parse the request body
        data = json.loads(request.body)
        
        # Get the role
        role = UserRole.objects.get(id=role_id)
        
        # Update the set_default_permissions method with new permissions
        def update_role_permissions_method(self, user_permissions):
            for field in UserPermissions._meta.fields:
                if field.name in data and field.name not in ['user', 'id']:
                    setattr(user_permissions, field.name, data[field.name])
            return user_permissions
        
        # Replace the set_default_permissions method
        role.set_default_permissions = update_role_permissions_method.__get__(role, UserRole)
        
        # Update all users with this role
        for profile in UserProfile.objects.filter(role=role):
            if hasattr(profile.user, 'permissions'):
                role.set_default_permissions(profile.user.permissions)
                profile.user.permissions.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Role permissions updated successfully'
        })
    except UserRole.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Role not found'
        }, status=404)
    except PermissionDenied as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=403)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

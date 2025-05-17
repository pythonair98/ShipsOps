from django.urls import path
from .views import (
    login_view, register_view, logout_view, edit_user_view, delete_user_view, user_list,
    activate_user_view, deactivate_user_view, reset_user_password_view,
    get_permission_groups, get_user_permissions, update_user_permissions,
    role_list, get_role_permissions, update_role_permissions, role_users_view, edit_role_view,
    delete_role_view
)
from ShipOps.views import user_analytics

app_name = 'ShipsAuth'

urlpatterns = [
    # Main app URLs
    path('users/', user_list, name='user_list_auth'),
    path('users/<int:user_id>/edit/', edit_user_view, name='edit_user'),
    path('users/<int:user_id>/delete/', delete_user_view, name='delete_user'),
    path('users/<int:user_id>/reset-password/', reset_user_password_view, name='reset_user_password'),
    path('users/<int:user_id>/deactivate/', deactivate_user_view, name='deactivate_user'),
    path('users/<int:user_id>/activate/', activate_user_view, name='activate_user'),
    
    # Role management URLs
    path('roles/', role_list, name='role_list'),
    path('roles/<int:role_id>/users/', role_users_view, name='role_users'),
    path('roles/<int:role_id>/edit/', edit_role_view, name='edit_role'),
    path('roles/<int:role_id>/delete/', delete_role_view, name='delete_role'),
    path('roles/<int:role_id>/permissions/', get_role_permissions, name='get_role_permissions'),
    path('roles/<int:role_id>/permissions/update/', update_role_permissions, name='update_role_permissions'),
    
    # API endpoints
    path('permission-groups/', get_permission_groups, name='get_permission_groups'),
    path('permissions/<int:user_id>/', get_user_permissions, name='get_user_permissions'),
    path('permissions/<int:user_id>/update/', update_user_permissions, name='update_user_permissions'),
    path('analytics/', user_analytics, name='user_analytics'),
]
# User management URLs


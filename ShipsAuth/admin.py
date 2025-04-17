from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Occupation,
    SystemPages,
    Permission,
    Profile,
)
from ShipsAuth.models import UserProfile, UserRole

# =============================================================================
# Occupation Admin
# =============================================================================
@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Occupation model.
    Displays basic details along with a computed member count.
    """
    list_display = ('id', 'en_name', 'ar_name', 'power')
    search_fields = ('en_name', 'ar_name', 'power')
    list_filter = ('power',)
    ordering = ('power',)


# =============================================================================
# SystemPages Admin
# =============================================================================
@admin.register(SystemPages)
class SystemPagesAdmin(admin.ModelAdmin):
    """
    Admin configuration for the SystemPages model.
    Allows filtering by navigation flags and parent page.
    """
    list_display = ('id', 'endpoint', 'rendered_name', 'has_submenu', 'parent', 'is_nav_item')
    search_fields = ('endpoint', 'rendered_name')
    list_filter = ('has_submenu', 'is_nav_item', 'parent')
    ordering = ('id',)


# =============================================================================
# Permission Admin
# =============================================================================
@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Permission model.
    Provides quick lookup by page and occupation.
    """
    list_display = ('id', 'page', 'occupation')
    search_fields = (
        'page__rendered_name',  # allow searching by SystemPages rendered name
        'occupation__en_name',  # allow searching by occupation's English name
        'occupation__ar_name',  # allow searching by occupation's Arabic name
    )
    list_filter = ('page', 'occupation')
    ordering = ('id',)




# =============================================================================
# Profile Admin
# =============================================================================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Profile model.
    Uses a raw ID widget for the user_obj field and allows filtering by occupation.
    """
    list_display = ('id', 'user_obj', 'occupation', 'token', 'profile_image')
    search_fields = (
        'user_obj__username',
        'user_obj__first_name',
        'user_obj__last_name',
        'occupation__en_name',
        'occupation__ar_name',
    )
    list_filter = ('occupation',)
    ordering = ('id',)
    raw_id_fields = ('user_obj',)  # improves performance for foreign keys if there are many users





# =============================================================================
# User Role Admin
# =============================================================================
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserRole model.
    Displays role name and allows searching by name.
    """
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('id',)


# =============================================================================
# User Profile Admin
# =============================================================================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserProfile model.
    Displays user information and permissions.
    """
    list_display = ('id', 'user', 'role', 'department', 'can_view_contracts', 'can_edit_contracts')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department')
    list_filter = ('role', 'can_view_contracts', 'can_edit_contracts', 'can_view_invoices', 'can_edit_invoices')
    ordering = ('id',)
    raw_id_fields = ('user',)

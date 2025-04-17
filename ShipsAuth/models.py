from django.contrib.auth.models import User
from django.db import models

# =============================================================================
# SystemPages Model
# =============================================================================
class SystemPages(models.Model):
    """
    Represents a system page used for navigation and permissions.

    Fields:
        endpoint: The URL endpoint for the page.
        rendered_name: The display name for the page.
        has_submenu: Indicates if this page has submenu items.
        parent: Self-referential link to a parent page.
        is_nav_item: Indicates if this page should appear in the navigation menu.
    """
    endpoint = models.CharField(max_length=255)
    rendered_name = models.CharField(max_length=255)
    has_submenu = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='submenus'
    )
    is_nav_item = models.BooleanField(default=False)

    def get_submenu(self):
        """
        Returns all submenu pages that have this page as their parent.
        """
        return self.submenus.all()

    @staticmethod
    def has_permission(occupation_id, page_id):
        """
        Checks if a given occupation has permission to access the page.
        """
        return Permission.objects.filter(page_id=page_id, occupation_id=occupation_id).exists()

    def __str__(self):
        return self.rendered_name

# =============================================================================
# Occupation Model
# =============================================================================
class Occupation(models.Model):
    """
    Represents a user occupation or role within the system.

    Fields:
        ar_name: Arabic name of the occupation.
        en_name: English name of the occupation.
        power: An integer that represents the role's level or authority (must be unique).
    """
    ar_name = models.CharField(max_length=250, unique=True)
    en_name = models.CharField(max_length=250, unique=True)
    power = models.IntegerField(unique=True)

    def __str__(self):
        return self.en_name

# =============================================================================
# Permission Model
# =============================================================================
class Permission(models.Model):
    """
    Represents the permission linking an Occupation to a SystemPage.

    Fields:
        page: The system page to which permission applies.
        occupation: The occupation (role) that is granted permission.
    """
    page = models.ForeignKey(SystemPages, on_delete=models.CASCADE)
    occupation = models.ForeignKey(Occupation, on_delete=models.CASCADE)

    def get_page_object(self):
        """
        Returns the SystemPages object associated with this permission.
        """
        return self.page

    def get_occupation_object(self):
        """
        Returns the Occupation object associated with this permission.
        """
        return self.occupation

    def __str__(self):
        return f"Permission: {self.occupation.en_name} -> {self.page.rendered_name}"

# =============================================================================
# Profile Model
# =============================================================================
class Profile(models.Model):
    """
    Extends the Django User model with additional profile information.

    Fields:
        user_obj: One-to-one relation to Django's User model.
        occupation: Foreign key linking to the Occupation model.
        token: A token string for authentication or other purposes.
        profile_image: Path to the user's profile image.
    """
    user_obj = models.OneToOneField(User, on_delete=models.CASCADE, related_name='auth_profile')
    occupation = models.ForeignKey(
        Occupation,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    token = models.CharField(max_length=255, null=True, blank=True)
    profile_image = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user_obj.get_full_name()



# =============================================================================
# User Role Model
# =============================================================================
class UserRole(models.Model):
    """
    Represents user roles within the system to manage workflow permissions.
    
    Fields:
        name: The name of the role (e.g., 'Finance Department', 'Head Manager').
        description: A description of the role's responsibilities.
        created_at: Timestamp when the role was created.
        updated_at: Timestamp when the role was last updated.
    """
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('finance', 'Finance Department'),
        ('manager', 'Head Manager'),
        ('operations', 'Operations Staff'),
        ('viewer', 'Read-only User'),
    )
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.get_name_display()


# =============================================================================
# User Profile Model
# =============================================================================
class UserProfile(models.Model):
    """
    Extends the built-in User model with additional fields for role-based permissions.
    
    Fields:
        user: One-to-one relation with Django's User model.
        role: The role assigned to this user.
        department: The department this user belongs to.
        can_view_contracts: Whether the user can view contracts.
        can_edit_contracts: Whether the user can edit contracts.
        can_view_invoices: Whether the user can view invoices.
        can_edit_invoices: Whether the user can edit invoices.
    """
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='ops_profile')
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    can_view_contracts = models.BooleanField(default=True)
    can_edit_contracts = models.BooleanField(default=False)
    can_view_invoices = models.BooleanField(default=True)
    can_edit_invoices = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    @property
    def is_finance(self):
        """Check if user has finance department role"""
        return self.role and self.role.name == 'finance'
    
    @property
    def is_management(self):
        """Check if user has management role (admin or manager)"""
        return self.role and self.role.name in ['admin', 'manager']
    
    @property
    def is_operations(self):
        """Check if user has operations staff role"""
        return self.role and self.role.name == 'operations'


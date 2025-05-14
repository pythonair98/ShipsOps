from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

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
        name: The name of the role (e.g., 'System Administrator', 'Operations Manager').
        description: A description of the role's responsibilities.
        created_at: Timestamp when the role was created.
        updated_at: Timestamp when the role was last updated.
    """
    ROLE_CHOICES = (
        ('system_admin', 'System Administrator'),
        ('operations_manager', 'Operations Manager'),
        ('finance_officer', 'Finance Officer'),
        ('operations_staff', 'Operations Staff'),
        ('viewer', 'Viewer'),
        ('support_staff', 'Support Staff'),
    )
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.get_name_display()
    
    def set_default_permissions(self, user_permissions):
        """Set default permissions based on role"""
        if self.name == 'system_admin':
            # System Administrator has all permissions
            for field in UserPermissions._meta.fields:
                if field.name not in ['user', 'id']:
                    setattr(user_permissions, field.name, True)
        
        elif self.name == 'operations_manager':
            # Operations Manager permissions
            user_permissions.can_view_contracts = True
            user_permissions.can_create_contracts = True
            user_permissions.can_edit_contracts = True
            user_permissions.can_approve_contracts = True
            user_permissions.can_view_invoices = True
            user_permissions.can_view_vessels = True
            user_permissions.can_edit_vessels = True
            user_permissions.can_view_ports = True
            user_permissions.can_edit_ports = True
            user_permissions.can_view_crew = True
            user_permissions.can_edit_crew = True
            user_permissions.can_view_cargo = True
            user_permissions.can_edit_cargo = True
            user_permissions.can_view_reports = True
            user_permissions.can_generate_reports = True
            user_permissions.can_export_reports = True
            user_permissions.can_view_users = True
            user_permissions.can_edit_users = True
            user_permissions.can_view_settings = True
            user_permissions.can_view_audit_logs = True
            user_permissions.can_view_documents = True
            user_permissions.can_upload_documents = True
            user_permissions.can_view_maintenance = True
            user_permissions.can_edit_maintenance = True
            user_permissions.can_view_billing = True
            user_permissions.can_view_compliance = True
            user_permissions.can_edit_compliance = True
            user_permissions.can_view_risks = True
            user_permissions.can_edit_risks = True
        
        elif self.name == 'finance_officer':
            # Finance Officer permissions
            user_permissions.can_view_contracts = True
            user_permissions.can_view_invoices = True
            user_permissions.can_create_invoices = True
            user_permissions.can_edit_invoices = True
            user_permissions.can_approve_invoices = True
            user_permissions.can_view_reports = True
            user_permissions.can_generate_reports = True
            user_permissions.can_export_reports = True
            user_permissions.can_view_billing = True
            user_permissions.can_create_billing = True
            user_permissions.can_edit_billing = True
            user_permissions.can_view_documents = True
            user_permissions.can_upload_documents = True
        
        elif self.name == 'operations_staff':
            # Operations Staff permissions
            user_permissions.can_view_contracts = True
            user_permissions.can_create_contracts = True
            user_permissions.can_view_invoices = True
            user_permissions.can_view_vessels = True
            user_permissions.can_view_ports = True
            user_permissions.can_view_crew = True
            user_permissions.can_view_cargo = True
            user_permissions.can_view_documents = True
            user_permissions.can_upload_documents = True
            user_permissions.can_view_maintenance = True
            user_permissions.can_create_maintenance = True
        
        elif self.name == 'viewer':
            # Viewer permissions (read-only)
            user_permissions.can_view_contracts = True
            user_permissions.can_view_invoices = True
            user_permissions.can_view_vessels = True
            user_permissions.can_view_ports = True
            user_permissions.can_view_crew = True
            user_permissions.can_view_cargo = True
            user_permissions.can_view_reports = True
            user_permissions.can_view_documents = True
        
        elif self.name == 'support_staff':
            # Support Staff permissions
            user_permissions.can_view_contracts = True
            user_permissions.can_view_invoices = True
            user_permissions.can_view_vessels = True
            user_permissions.can_view_ports = True
            user_permissions.can_view_crew = True
            user_permissions.can_view_cargo = True
            user_permissions.can_view_documents = True
            user_permissions.can_upload_documents = True
            user_permissions.can_view_maintenance = True
            user_permissions.can_view_billing = True
            user_permissions.can_view_compliance = True
            user_permissions.can_view_risks = True
        
        return user_permissions


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

class UserPermissions(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='permissions')
    
    # Contract Management
    can_view_contracts = models.BooleanField(default=False, verbose_name=_('View Contracts'))
    can_create_contracts = models.BooleanField(default=False, verbose_name=_('Create Contracts'))
    can_edit_contracts = models.BooleanField(default=False, verbose_name=_('Edit Contracts'))
    can_delete_contracts = models.BooleanField(default=False, verbose_name=_('Delete Contracts'))
    can_approve_contracts = models.BooleanField(default=False, verbose_name=_('Approve Contracts'))
    
    # Invoice Management
    can_view_invoices = models.BooleanField(default=False, verbose_name=_('View Invoices'))
    can_create_invoices = models.BooleanField(default=False, verbose_name=_('Create Invoices'))
    can_edit_invoices = models.BooleanField(default=False, verbose_name=_('Edit Invoices'))
    can_delete_invoices = models.BooleanField(default=False, verbose_name=_('Delete Invoices'))
    can_approve_invoices = models.BooleanField(default=False, verbose_name=_('Approve Invoices'))
    
    # Vessel Management
    can_view_vessels = models.BooleanField(default=False, verbose_name=_('View Vessels'))
    can_create_vessels = models.BooleanField(default=False, verbose_name=_('Create Vessels'))
    can_edit_vessels = models.BooleanField(default=False, verbose_name=_('Edit Vessels'))
    can_delete_vessels = models.BooleanField(default=False, verbose_name=_('Delete Vessels'))
    
    # Port Management
    can_view_ports = models.BooleanField(default=False, verbose_name=_('View Ports'))
    can_create_ports = models.BooleanField(default=False, verbose_name=_('Create Ports'))
    can_edit_ports = models.BooleanField(default=False, verbose_name=_('Edit Ports'))
    can_delete_ports = models.BooleanField(default=False, verbose_name=_('Delete Ports'))
    
    # Crew Management
    can_view_crew = models.BooleanField(default=False, verbose_name=_('View Crew'))
    can_create_crew = models.BooleanField(default=False, verbose_name=_('Create Crew'))
    can_edit_crew = models.BooleanField(default=False, verbose_name=_('Edit Crew'))
    can_delete_crew = models.BooleanField(default=False, verbose_name=_('Delete Crew'))
    
    # Cargo Management
    can_view_cargo = models.BooleanField(default=False, verbose_name=_('View Cargo'))
    can_create_cargo = models.BooleanField(default=False, verbose_name=_('Create Cargo'))
    can_edit_cargo = models.BooleanField(default=False, verbose_name=_('Edit Cargo'))
    can_delete_cargo = models.BooleanField(default=False, verbose_name=_('Delete Cargo'))
    
    # Reports
    can_view_reports = models.BooleanField(default=False, verbose_name=_('View Reports'))
    can_generate_reports = models.BooleanField(default=False, verbose_name=_('Generate Reports'))
    can_export_reports = models.BooleanField(default=False, verbose_name=_('Export Reports'))
    
    # User Management
    can_view_users = models.BooleanField(default=False, verbose_name=_('View Users'))
    can_create_users = models.BooleanField(default=False, verbose_name=_('Create Users'))
    can_edit_users = models.BooleanField(default=False, verbose_name=_('Edit Users'))
    can_delete_users = models.BooleanField(default=False, verbose_name=_('Delete Users'))
    
    # System Settings
    can_view_settings = models.BooleanField(default=False, verbose_name=_('View Settings'))
    can_edit_settings = models.BooleanField(default=False, verbose_name=_('Edit Settings'))
    
    # Audit Logs
    can_view_audit_logs = models.BooleanField(default=False, verbose_name=_('View Audit Logs'))
    
    # Document Management
    can_view_documents = models.BooleanField(default=False, verbose_name=_('View Documents'))
    can_upload_documents = models.BooleanField(default=False, verbose_name=_('Upload Documents'))
    can_delete_documents = models.BooleanField(default=False, verbose_name=_('Delete Documents'))
    
    # Maintenance
    can_view_maintenance = models.BooleanField(default=False, verbose_name=_('View Maintenance'))
    can_create_maintenance = models.BooleanField(default=False, verbose_name=_('Create Maintenance'))
    can_edit_maintenance = models.BooleanField(default=False, verbose_name=_('Edit Maintenance'))
    can_delete_maintenance = models.BooleanField(default=False, verbose_name=_('Delete Maintenance'))
    
    # Billing
    can_view_billing = models.BooleanField(default=False, verbose_name=_('View Billing'))
    can_create_billing = models.BooleanField(default=False, verbose_name=_('Create Billing'))
    can_edit_billing = models.BooleanField(default=False, verbose_name=_('Edit Billing'))
    can_delete_billing = models.BooleanField(default=False, verbose_name=_('Delete Billing'))
    
    # Compliance
    can_view_compliance = models.BooleanField(default=False, verbose_name=_('View Compliance'))
    can_edit_compliance = models.BooleanField(default=False, verbose_name=_('Edit Compliance'))
    
    # Risk Management
    can_view_risks = models.BooleanField(default=False, verbose_name=_('View Risks'))
    can_create_risks = models.BooleanField(default=False, verbose_name=_('Create Risks'))
    can_edit_risks = models.BooleanField(default=False, verbose_name=_('Edit Risks'))
    can_delete_risks = models.BooleanField(default=False, verbose_name=_('Delete Risks'))
    
    class Meta:
        verbose_name = _('User Permissions')
        verbose_name_plural = _('User Permissions')
    
    def __str__(self):
        return f"Permissions for {self.user.get_full_name()}"
    
    @classmethod
    def get_permission_groups(cls):
        """Returns a dictionary of permission groups for the frontend"""
        return {
            'contract_management': {
                'name': _('Contract Management'),
                'permissions': [
                    'can_view_contracts',
                    'can_create_contracts',
                    'can_edit_contracts',
                    'can_delete_contracts',
                    'can_approve_contracts',
                ]
            },
            'invoice_management': {
                'name': _('Invoice Management'),
                'permissions': [
                    'can_view_invoices',
                    'can_create_invoices',
                    'can_edit_invoices',
                    'can_delete_invoices',
                    'can_approve_invoices',
                ]
            },
            'vessel_management': {
                'name': _('Vessel Management'),
                'permissions': [
                    'can_view_vessels',
                    'can_create_vessels',
                    'can_edit_vessels',
                    'can_delete_vessels',
                ]
            },
            'port_management': {
                'name': _('Port Management'),
                'permissions': [
                    'can_view_ports',
                    'can_create_ports',
                    'can_edit_ports',
                    'can_delete_ports',
                ]
            },
            'crew_management': {
                'name': _('Crew Management'),
                'permissions': [
                    'can_view_crew',
                    'can_create_crew',
                    'can_edit_crew',
                    'can_delete_crew',
                ]
            },
            'cargo_management': {
                'name': _('Cargo Management'),
                'permissions': [
                    'can_view_cargo',
                    'can_create_cargo',
                    'can_edit_cargo',
                    'can_delete_cargo',
                ]
            },
            'reports': {
                'name': _('Reports'),
                'permissions': [
                    'can_view_reports',
                    'can_generate_reports',
                    'can_export_reports',
                ]
            },
            'user_management': {
                'name': _('User Management'),
                'permissions': [
                    'can_view_users',
                    'can_create_users',
                    'can_edit_users',
                    'can_delete_users',
                ]
            },
            'system_settings': {
                'name': _('System Settings'),
                'permissions': [
                    'can_view_settings',
                    'can_edit_settings',
                ]
            },
            'audit_logs': {
                'name': _('Audit Logs'),
                'permissions': [
                    'can_view_audit_logs',
                ]
            },
            'document_management': {
                'name': _('Document Management'),
                'permissions': [
                    'can_view_documents',
                    'can_upload_documents',
                    'can_delete_documents',
                ]
            },
            'maintenance': {
                'name': _('Maintenance'),
                'permissions': [
                    'can_view_maintenance',
                    'can_create_maintenance',
                    'can_edit_maintenance',
                    'can_delete_maintenance',
                ]
            },
            'billing': {
                'name': _('Billing'),
                'permissions': [
                    'can_view_billing',
                    'can_create_billing',
                    'can_edit_billing',
                    'can_delete_billing',
                ]
            },
            'compliance': {
                'name': _('Compliance'),
                'permissions': [
                    'can_view_compliance',
                    'can_edit_compliance',
                ]
            },
            'risk_management': {
                'name': _('Risk Management'),
                'permissions': [
                    'can_view_risks',
                    'can_create_risks',
                    'can_edit_risks',
                    'can_delete_risks',
                ]
            },
        }


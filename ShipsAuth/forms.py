from django import forms
from .models import Occupation, SystemPages, Permission,  Profile

class OccupationForm(forms.ModelForm):
    """
    Form for creating or updating an Occupation.

    Fields:
      - ar_name: Arabic name of the occupation.
      - en_name: English name of the occupation.
      - power: Integer representing the role's authority.
    """

    class Meta:
        model = Occupation
        fields = ['ar_name', 'en_name', 'power']


class SystemPagesForm(forms.ModelForm):
    """
    Form for creating or updating a System Page.

    Fields:
      - endpoint: The URL endpoint for the page.
      - rendered_name: The display name for the page.
      - has_submenu: Boolean indicating if the page has submenu items.
      - parent: Self-referential ForeignKey to set a parent page.
      - is_nav_item: Boolean to show/hide this page in the navigation.
    """

    class Meta:
        model = SystemPages
        fields = ['endpoint', 'rendered_name', 'has_submenu', 'parent', 'is_nav_item']


class PermissionForm(forms.ModelForm):
    """
    Form for creating or updating a Permission.

    Fields:
      - page: ForeignKey linking to the SystemPages model.
      - occupation: ForeignKey linking to the Occupation model.
    """

    class Meta:
        model = Permission
        fields = ['page', 'occupation']


class ProfileForm(forms.ModelForm):
    """
    Form for creating or updating a Profile.

    Fields:
      - user_obj: One-to-one relation to Django's built-in User model.
      - occupation: ForeignKey linking to the Occupation model.
      - token: Token string for authentication or other purposes.
      - profile_image: Path to the user's profile image.

    Note:
      Adjust the widget or validation for 'user_obj' as necessary if you want to manage user creation separately.
    """

    class Meta:
        model = Profile
        fields = ['user_obj', 'occupation', 'token', 'profile_image']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)
    profile_image = forms.ImageField(required=False)
    phone_number = forms.CharField(max_length=100, required=False)
    
    class Meta:
        from django.contrib.auth.models import User
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Get current instance (for editing)
        instance = getattr(self, 'instance', None)
        
        # Check if username exists but exclude current instance if editing
        if instance and instance.pk:
            users = self.Meta.model.objects.filter(username=username).exclude(pk=instance.pk)
            if users.exists():
                raise forms.ValidationError("This username is already taken. Please choose another one.")
        else:
            # For new users
            if self.Meta.model.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken. Please choose another one.")
        
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        # If this is a new user or password is being changed
        if not self.instance.pk or password:
            if not password:
                raise forms.ValidationError("Password is required for new users")
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Only set password if it's provided (for editing users)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            
            # Create or update profile
            try:
                profile = Profile.objects.get(user_obj=user)
            except Profile.DoesNotExist:
                profile = Profile(user_obj=user)
                
            if self.cleaned_data.get('profile_image'):
                profile.profile_image = self.cleaned_data['profile_image']
            
            profile.save()
        
        return user

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
    


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=100)
    profile_image = forms.ImageField(required=False)
    
    def clean_username(self):
        from django.contrib.auth.models import User
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another one.")
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data
    
    def save(self, commit=True):
        from django.contrib.auth.models import User
        
        user = User(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        
        if commit:
            user.set_password(self.cleaned_data['password'])
            user.save()
            
            # Create profile for the user
            profile = Profile(
                user_obj=user,
                profile_image=self.cleaned_data.get('profile_image', None)
            )
            profile.save()
        
        return user

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Profile, StudentDetail


class UserRegistrationForm(UserCreationForm):
    """Form for new STUDENT registration only (public portal)."""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email',
        })
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'First name',
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Last name',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Choose a username',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Create a password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm your password',
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT  # Force student role
        if commit:
            user.save()
        return user


class AdminCreateUserForm(UserCreationForm):
    """Form for admin to create any type of user (student/teacher)."""

    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'role-radio'}),
        initial='student',
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter email',
        })
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'First name',
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Last name',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Choose a username',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Create a password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm password',
        })


class AdminEditUserForm(forms.ModelForm):
    """Form for admin to edit user info (name, email, role, active status)."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'is_active', 'is_email_verified']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'First name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Last name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Email address',
            }),
            'role': forms.Select(attrs={'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_email_verified': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class UserLoginForm(AuthenticationForm):
    """Custom login form with styled widgets."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username or Email',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password',
        })
    )


class ProfileUpdateForm(forms.ModelForm):
    """Form to update user profile."""

    class Meta:
        model = Profile
        fields = ['bio', 'phone', 'date_of_birth', 'address', 'profile_picture', 'avatar_ratio', 'avatar_position']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Tell us about yourself...',
                'rows': 4,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Phone number',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Your address',
                'rows': 3,
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-input file-input',
                'accept': 'image/*',
            }),
            'avatar_ratio': forms.Select(attrs={
                'class': 'form-input',
            }),
            'avatar_position': forms.Select(attrs={
                'class': 'form-input',
            }),
        }


class UserUpdateForm(forms.ModelForm):
    """Form to update basic user info."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'First name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Last name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Email address',
            }),
        }


class StudentDetailForm(forms.ModelForm):
    """Form for student academic details."""

    class Meta:
        model = StudentDetail
        fields = ['roll_number', 'department', 'year', 'semester',
                  'admission_date', 'guardian_name', 'guardian_phone']
        widgets = {
            'roll_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Roll number',
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Department',
            }),
            'year': forms.Select(attrs={'class': 'form-input'}),
            'semester': forms.Select(attrs={'class': 'form-input'}),
            'admission_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'guardian_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Guardian name',
            }),
            'guardian_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Guardian phone',
            }),
        }

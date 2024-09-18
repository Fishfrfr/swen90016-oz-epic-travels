from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email

from .models import CustomUser


class UserRegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Create a strong password'}),
        help_text='At least 8 characters with uppercase, lowercase, and digits.'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter your password'}),
        help_text='Enter your password again for verification.'
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'full_name', 'age', 'email', 'address', 'contact_number',
            'business_registration_number', 'registration_document'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a unique username'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'age': forms.NumberInput(attrs={'min': 18, 'max':80, 'placeholder': 'Your age'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your email address'}),
            'address': forms.TextInput(attrs={'placeholder': 'Your full address'}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'Your contact number'}),
            'business_registration_number': forms.TextInput(attrs={'placeholder': 'Business registration number'}),
            'registration_document': forms.FileInput(attrs={'class': 'w-full'}),
        }
        help_texts = {
            'username': 'Choose a unique username for your account.',
            'full_name': 'Enter your full name as it appears on official documents.',
            'age': 'Must be at least 18 years old to register.',
            'email': 'We\'ll use this for account verification and important updates.',
            'address': 'Provide your current residential address.',
            'contact_number': 'Enter a valid phone number.',
            'business_registration_number': 'Enter your registration number.',
            'registration_document': 'Upload a copy of your business registration document (PDF, JPG, JPEG, or PNG, max 5MB).',
        }
        error_messages = {
            field: {'required': f'{field.replace("_", " ").title()} is required.'}
            for field in fields
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        validate_email(email)
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use. Please use a different email.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not any(c.isupper() for c in password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in password):
            raise forms.ValidationError("Password must contain at least one digit.")
        return password

    def clean_registration_document(self):
        document = self.cleaned_data.get('registration_document')
        if document:
            if document.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 5 MB.")
            if document.name.split('.')[-1].lower() not in ['pdf', 'jpg', 'jpeg', 'png']:
                raise forms.ValidationError("Only PDF, JPG, JPEG, and PNG files are allowed.")
        return document

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and age < 18:
            raise forms.ValidationError("You must be at least 18 years old to register.")
        return age


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )

    error_messages = {
        'invalid_login': "Please enter a correct username and password.",
        'inactive': "This account is inactive.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Username"
        self.fields['password'].label = "Password"
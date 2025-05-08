from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Books, User


class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ['name', 'author', 'price']


class ProfileForm(forms.ModelForm):
    # Adding password fields for updating password
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="Confirm New Password"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role',
                  'new_password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        # Password validation
        if new_password or confirm_password:
            if new_password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match.")
            elif len(new_password) < 8:
                self.add_error(
                    'new_password', "Password must be at least 8 characters long.")
        return cleaned_data


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=[
        ('user', 'Regular User'),
        ('admin', 'Administrator')
    ], initial='user')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

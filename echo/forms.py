from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Books, User


class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ['name', 'author', 'price']


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

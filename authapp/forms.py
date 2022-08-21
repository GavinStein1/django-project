from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class NewUserForm(UserCreationForm):
    email = forms.EmailField(max_length=200)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    # username = forms.CharField(label='Username', max_length=18)
    # password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    # password_again = forms.CharField(widget=forms.PasswordInput(), label="Re-enter password")
    # email = forms.CharField(label='Email', max_length=100)
    # first_name = forms.CharField(label='First name', max_length=100)
    # last_name = forms.CharField(label='Last name', max_length=100)

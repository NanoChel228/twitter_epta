from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    username = forms.CharField(label='Никнейм', required=True, widget=forms.TextInput(attrs = {'class': 'forms-control mb-20'}))
    email = forms.EmailField(label='E-mail', required=True, widget=forms.TextInput(attrs = {'class': 'forms-control mb-20'}))
    password1 = forms.CharField(label='Пароль', required=True, widget=forms.PasswordInput(attrs = {'class': 'forms-control mb-20'})) 
    password2 = forms.CharField(label='Повторите пароль', required=True, widget=forms.PasswordInput(attrs = {'class': 'forms-control mb-20'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['last_name']
        if commit:
            user.save()
            return user

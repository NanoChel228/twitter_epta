from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    username = forms.CharField(label='Никнейм', required=True)
    email = forms.EmailField(label='E-mail', required=True)
    password1 = forms.CharField(label='Пароль', required=True)
    password2 = forms.CharField(label='Повторите пароль', required=True)
    first_name = forms.CharField(label='Имя', required=True)
    last_name = forms.CharField(label='Фамилия', required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['last_name']
        if commit:
            user.save()
            return user

from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Post, Tag, Profile, Message


class RegisterForm(UserCreationForm):
    username = forms.CharField(label='Никнейм', required=True, widget=forms.TextInput())
    email = forms.EmailField(label='E-mail', required=True, widget=forms.EmailInput())
    password1 = forms.CharField(label='Пароль', required=True, widget=forms.PasswordInput())
    password2 = forms.CharField(label='Повторите пароль', required=True, widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
    
class PostForm(forms.ModelForm):
    new_tag = forms.CharField(max_length=15, required=False, label="Новый тег")

    class Meta:
        model = Post
        fields = ['content', 'image', 'tag', 'new_tag']  # 'tag' для выбора существующих тегов

    def save(self, commit=True):
        post = super().save(commit=False)
        new_tag_name = self.cleaned_data.get('new_tag')

        if new_tag_name:
            # Создаем новый тег, если его нет
            tag, created = Tag.objects.get_or_create(name=new_tag_name, slug=new_tag_name.lower())
            post.tag = tag

        if commit:
            post.save()
        return post


class SearchForm(forms.Form):
    query = forms.CharField(label='Поиск', max_length=100, required=False)
    
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['content', 'image', 'image_header']
        
        
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
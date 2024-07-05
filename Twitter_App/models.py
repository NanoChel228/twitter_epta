from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import reverse

# Create your models here.
class Post(models.Model):
    title = models.CharField('Название поста', max_length=255)
    text = models.TextField('Описание поста')
    tag = models.ForeignKey('Тег', on_delete=models.CASCADE, null=True)
    profile = models.ForeignKey('UserProfile', verbose_name='Пользователь', on_delete=models.CASCADE)
    created_at = models.DateTimeField('Дата создания поста', default=timezone.now)


class Tag(models.Model):
    title = models.CharField('Название категории', max_length=20)
    slug = models.SlugField('Ссылка', unique=True)


class Favourites(models.Model):
    user = models.ForeignKey('UserProfile', verbose_name='Пользователь', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, unique=False)


class UserProfile(models.Model) :
    user = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    name = models.CharField('Никнейм', max_length=30)
    image = models.ImageField('Аватарка')
    favourites = models.ForeignKey(Favourites, verbose_name='избранное')

    def get_favorites(self):
        if self.user:
            return self.user.favorite_set.all()


class Chat(models.Model):
    profile = models.ForeignKey(UserProfile, verbose_name='Профиль')
    message = models.ForeignKey('Message')


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE) 
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    date = models.DateTimeField(default = timezone.now)
    text = models.TextField()


class Message(models.Model):
    sender = models.ForeignKey(UserProfile)
    recipient = models.ForeignKey(UserProfile)
    text = models.TextField('Сообщение')
    created_ta = models.DateTimeField('Дата создания сообщения', default=timezone.now)
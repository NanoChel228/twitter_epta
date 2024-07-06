from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


# Create your models here.
class Post(models.Model):
    title = models.CharField('Название поста', max_length=255)
    content = models.TextField('Описание поста')
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey('Profile', verbose_name='Автор', on_delete=models.CASCADE)
    created_at = models.DateTimeField('Дата создания поста', default=timezone.now)
    
    def get_link(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
           
class Tag(models.Model):
    name = models.CharField('Название категории', max_length=20)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

class Favorites(models.Model):
    user = models.ForeignKey('Profile' , verbose_name='Пользователь', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Пост')
    
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class Profile(models.Model) :
    user = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    content = models.TextField('Описание')
    image = models.ImageField('Аватарка', upload_to='profile_images/', blank=True, null=True)
    favourites = models.ManyToManyField(Favorites, verbose_name='Избранные' ,related_name='favorited_by', blank=True)

    def get_favorites(self):
        return self.user.favorites_set.all()
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE) 
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateTimeField(default = timezone.now)
    text = models.TextField()
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    
class Chat(models.Model):
    profiles = models.ManyToManyField(Profile)
    messages = models.ManyToManyField('Message')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'


class Message(models.Model):
    sender = models.ForeignKey(Profile, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(Profile, related_name='received_messages', on_delete=models.CASCADE)
    text = models.TextField('Сообщение')
    created_at = models.DateTimeField('Дата создания сообщения', default=timezone.now)
    
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
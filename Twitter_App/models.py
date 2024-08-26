from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from slugify import slugify
from django.db.models import Sum


# Create your models here.
class Post(models.Model):
    content = models.TextField('Описание поста', max_length=280)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey('Profile', verbose_name='Автор', on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField('Дата создания поста', default=timezone.now)
    slug = models.SlugField('Ссылка', unique=True)
    image = models.ImageField('Картинка', upload_to='post_img/', blank=True, null=True)
    likes = models.ManyToManyField('Profile', related_name='liked_posts', blank=True)
    views = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        max_length = 10
        if len(self.content) > max_length:
            return f"{self.content[:max_length]}..."
        return self.content

    def get_link(self):
        return reverse('post_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug and self.content:  # Генерация слага только если его нет и контент присутствует
            base_slug = slugify(self.content[:50])  # Используйте slugify для обработки текста
            unique_slug = base_slug
            num = 1
            while Post.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

           
class Tag(models.Model):
    name = models.CharField('Название категории', max_length=20)
    slug = models.SlugField('Ссылка', unique=True, default='default-slug')

    def __str__(self):
        return self.name

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
    user = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE, max_length=10)
    content = models.TextField('Описание')
    image = models.ImageField('Аватарка', upload_to='profile_images/', blank=True, null=True, default='profile_images/default.webp')
    image_header = models.ImageField('Хедер', upload_to='profile_image/', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания профиля', default=timezone.now)
    subscriptions = models.ManyToManyField('self', symmetrical=False, related_name='subscribers')    
    
    def __str__(self):
        return f"{self.user.username}"
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        
    def total_post_views(self):
        return self.posts.aggregate(total_views=Sum('views'))['total_views'] or 0


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE) 
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateTimeField(default = timezone.now)
    text = models.TextField()
    created_at = models.DateTimeField('Дата создания профиля', default=timezone.now)

    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        
    def __str__(self):
        return f'Comment by {self.author} on {self.post}'

    

class Chat(models.Model):
    profiles = models.ManyToManyField(Profile, related_name='chats')
    messages = models.ManyToManyField('Message', related_name='chats', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    def __str__(self):
        return f"Chat created at {self.created_at}"


class Message(models.Model):
    sender = models.ForeignKey(Profile, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(Profile, related_name='received_messages', on_delete=models.CASCADE)
    text = models.TextField('Сообщение')
    created_at = models.DateTimeField('Дата создания сообщения', default=timezone.now)
    
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f"Message from {self.sender.user.username} to {self.recipient.user.username}"
    
    

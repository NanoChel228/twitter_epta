from django.shortcuts import render, redirect, reverse, get_object_or_404
from .forms import RegisterForm, PostForm, SearchForm, ProfileForm, MessageForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Post, Comment, Profile, Tag, Favorites, Chat, Message
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q, Sum, F
from django.http import JsonResponse

# Create your views here.

def home(request):
    if not request.user.is_authenticated:
        return redirect('register')

    if request.method == 'POST':
        if 'favorite' in request.POST:
            post_slug = request.POST.get('post_slug')
            post = get_object_or_404(Post, slug=post_slug)
            
            profile, created = Profile.objects.get_or_create(user=request.user)
            
            favorite, created = Favorites.objects.get_or_create(user=profile, post=post)
            
            if not created:
                favorite.delete()
            
            return redirect('home')

        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            profile, created = Profile.objects.get_or_create(user=request.user)
            post.author = profile

            new_tag_name = request.POST.get('new_tag')
            if new_tag_name:
                tag, created = Tag.objects.get_or_create(name=new_tag_name, slug=new_tag_name.lower())
                post.tag = tag
            elif request.POST.get('tag'):
                post.tag = Tag.objects.get(id=request.POST.get('tag'))

            post.save()
            return redirect('home')
        else:
            print(form.errors)
    else:
        form = PostForm()

    posts = Post.objects.all()
    tags = Tag.objects.all()

    favorite_posts = []
    if request.user.is_authenticated:
        profile, created = Profile.objects.get_or_create(user=request.user)
        favorite_posts = Favorites.objects.filter(user=profile).values_list('post', flat=True)

    # Get top 5 profiles by total post views
    popular_profiles = Profile.objects.annotate(
        total_views=Sum('posts__views')
    ).order_by('-total_views')[:5]

    context = {
        'form': form,
        'posts': posts,
        'tags': tags,
        'favorite_posts': favorite_posts,
        'author': profile,
        'popular_profiles': popular_profiles,
    }
    return render(request, 'home.html', context)


def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect(reverse('post_detail', kwargs={'slug': slug}))
    else:
        form = PostForm(instance=post)
    
    return render(request, 'edit_post.html', {'form': form, 'post': post})

    
    
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'confirm_delete.html', {'post': post})


def register(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                Profile.objects.get_or_create(user=user)  # Создание профиля для нового пользователя
                login(request, user)
                return redirect('home')
        else:
            form = RegisterForm()
        return render(request, 'register.html', {'form': form})
    return redirect('home')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    message = None

    if request.method == 'POST':
        login_data = request.POST.get('username_or_email')
        password = request.POST.get('password')

        # Попробуем определить, что ввел пользователь
        if login_data:
            try:
                # Попытка аутентифицировать пользователя по email
                user = User.objects.get(email=login_data)
                username = user.username
            except ObjectDoesNotExist:
                # Попытка аутентифицировать пользователя по username
                username = login_data

            # Попытка аутентификации пользователя
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                message = 'Извините, неверный логин или пароль.'
        else:
            message = 'Извините, вы не ввели логин или email.'

    return render(request, 'login.html', {'message': message})


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('register')


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = get_or_create_user_profile(profile_user)
    image_profile = profile.image
    image_header_profile = profile.image_header
    posts = Post.objects.filter(author=profile)
    context = {
        'profile_user': profile_user,
        'image_profile': image_profile,
        'image_header_profile': image_header_profile,
        'posts': posts,
        'author': profile,
    }

    return render(request, 'profile.html', context)


def get_or_create_user_profile(user):
    profile, created = Profile.objects.get_or_create(user=user)
    return profile


@login_required
def comment(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(Post, slug=slug)
        text = request.POST.get('comment')
        profile = get_or_create_user_profile(request.user)
        comment = Comment(post=post, author=profile, text=text)
        comment.save()
        post.comments_count += 1
        post.save()
        return redirect(reverse('post_detail', kwargs={'slug': slug}))
    return redirect(reverse('post_detail', kwargs={'slug': slug}))


@login_required
def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    profile = request.user.profile

    if profile in post.likes.all():
        post.likes.remove(profile)  # Удаляем лайк
    else:
        post.likes.add(profile)  # Добавляем лайк

    return JsonResponse({
        'likes_count': post.likes.count(),
        'liked': profile in post.likes.all()
    })
    

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    # Использование F-экспрессии для увеличения счётчика просмотров
    post.views = F('views') + 1
    post.save(update_fields=['views'])
    post.refresh_from_db()
    
    # Получение автора поста
    author_profile = post.author
    
    # Получение комментариев
    comments = post.comments.all()
    
    context = {
        'post': post,
        'comments': comments,
        'likes_count': post.likes.count(),
        'comments_count': post.comments_count,
        'views_count': post.views,
        'author': author_profile,  # передача автора
    }
    
    return render(request, 'post_detail.html', context)


def explore(request):
    profile = get_or_create_user_profile(request.user)
    form = SearchForm(request.GET)
    posts = Post.objects.none()  # Начинаем с пустого QuerySet
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            posts = Post.objects.filter(
                Q(content__icontains=query.lower()) | Q(tag__name__icontains=query.lower()) | Q(content__icontains=query.upper()) | Q(tag__name__icontains=query.upper())
            )

    context = {
        'form': form,
        'posts': posts,
        'query': query,
        'author': profile,
    }
    return render(request, 'explore.html', context)


@login_required
def favorite_posts(request):
    profile = get_or_create_user_profile(request.user)
    favorites = Favorites.objects.filter(user=request.user.profile)
    return render(request, 'favorites.html', {'favorites': favorites, 'author': profile})


def communities(request):
    profile = get_or_create_user_profile(request.user)
    # Получаем все теги
    tags = Tag.objects.all()
    
    # Получаем выбранный тег из параметров запроса
    selected_tag_slug = request.GET.get('tag')
    
    if selected_tag_slug:
        # Найти тег по slug
        selected_tag = get_object_or_404(Tag, slug=selected_tag_slug)
        # Фильтруем посты по выбранному тегу
        posts = Post.objects.filter(tag=selected_tag)
    else:
        # Если тег не выбран, показываем все посты
        posts = Post.objects.all()
    
    return render(request, 'communities.html', {'tags': tags, 'posts': posts, 'selected_tag': selected_tag_slug, 'author': profile})


@login_required
def update_profile(request):
    if request.method == 'POST':
        profile = request.user.profile
        user = profile.user
        print()
        user.username = request.POST.get('username')
        user.save()
        
        profile.content = request.POST.get('bio')
        profile.birthday = request.POST.get('birthday')
        
        if 'image' in request.FILES:
            profile.image = request.FILES['image']
        
        if 'image_header' in request.FILES:
            profile.image_header = request.FILES['image_header']
        
        profile.save()
        return redirect(reverse('profile_url', args=[user.username]))

    return redirect('profile')


# тут пиздец босс качалки


def chat_list(request, chat_id=None):
    # Получаем все чаты текущего пользователя
    profile = get_or_create_user_profile(request.user)
    chats = Chat.objects.filter(profiles=request.user.profile)
    
    # Если указан chat_id, получаем выбранный чат
    selected_chat = None
    messages = []
    other_profile_username = ''

    if chat_id:
        selected_chat = get_object_or_404(Chat, id=chat_id, profiles=request.user.profile)
        messages = selected_chat.messages.all()
        other_profile = selected_chat.profiles.exclude(id=request.user.profile.id).first()
        if other_profile:
            other_profile_username = other_profile.user.username

    # Передаем все чаты и сообщения выбранного чата в контексте
    context = {
        'chats': chats,
        'selected_chat': selected_chat,
        'messages': messages,
        'other_profile_username': other_profile_username,
        'author': profile
    }
    return render(request, 'chat.html', context)


@login_required
def create_chat(request):
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient_username')
        try:
            recipient_profile = Profile.objects.get(user__username=recipient_username)
        except Profile.DoesNotExist:
            # Если пользователь не найден, можно вернуть ошибку или сообщение
            return redirect('chat_list')

        # Проверяем, существует ли уже чат с этим пользователем
        chat = Chat.objects.filter(profiles=request.user.profile).filter(profiles=recipient_profile).first()

        if not chat:
            # Если такого чата нет, создаем новый чат
            chat = Chat.objects.create()
            chat.profiles.add(request.user.profile, recipient_profile)

        # Перенаправляем на этот чат
        return redirect('chat_list_with_id', chat_id=chat.id)

@login_required
def send_message(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, profiles=request.user.profile)
    
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            recipient = chat.profiles.exclude(id=request.user.profile.id).first()
            message = Message.objects.create(
                sender=request.user.profile,
                recipient=recipient,
                text=text
            )
            chat.messages.add(message)

    return redirect('chat_list_with_id', chat_id=chat.id)


@login_required
def subscribe(request, username):
    profile_to_subscribe = get_object_or_404(Profile, user__username=username)
    
    if profile_to_subscribe != request.user.profile:
        request.user.profile.subscriptions.add(profile_to_subscribe)
        messages.success(request, f'Вы подписались на {profile_to_subscribe.user.username}')
    
    # Вернуть пользователя на страницу, с которой он пришел
    return redirect(request.META.get('HTTP_REFERER', 'profile_url'))


@login_required
def unsubscribe(request, username):
    profile_to_unsubscribe = get_object_or_404(Profile, user__username=username)
    
    if profile_to_unsubscribe != request.user.profile:
        request.user.profile.subscriptions.remove(profile_to_unsubscribe)
        messages.success(request, f'Вы отписались от {profile_to_unsubscribe.user.username}')
        
    return redirect(request.META.get('HTTP_REFERER', 'profile_url'))
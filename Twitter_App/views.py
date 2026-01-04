from django.shortcuts import render, redirect, reverse, get_object_or_404
from .forms import RegisterForm, PostForm, SearchForm, ProfileForm, MessageForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Post, Comment, Profile, Tag, Favorites, Chat, Message, PostRequest
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

    # Основные данные
    posts = Post.objects.all()
    tags = Tag.objects.all()
    trending_posts = get_trending_posts()
    search_query = request.GET.get('q', '')
    searched_profiles = search_profiles(search_query)
    
    if search_query:
        searched_profiles = search_profiles(search_query)
    else:
        searched_profiles = []

    if request.GET.get('profile_id'):
        profile_id = request.GET.get('profile_id')
        return redirect('profile', username=Profile.objects.get(id=profile_id).user.username)

    # Получаем избранные посты текущего пользователя
    favorite_posts = []
    follow_profiles = []
    if request.user.is_authenticated:
        profile, created = Profile.objects.get_or_create(user=request.user)
        favorite_posts = Favorites.objects.filter(user=profile).values_list('post', flat=True)
        # Получаем профили, на которые подписан текущий пользователь
        follow_profiles = profile.subscriptions.all()


    context = {
        'form': form,
        'posts': posts,
        'tags': tags,
        'favorite_posts': favorite_posts,
        'author': profile,
        'trending_posts': trending_posts,
        'searched_profiles': searched_profiles,
        'search_query': search_query,
        'follow_profiles': follow_profiles,  # Добавлено
    }
    return render(request, 'home.html', context)



def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    tags = Tag.objects.all()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect(reverse('post_detail', kwargs={'slug': slug}))
    else:
        form = PostForm(instance=post)
    
    return render(request, 'edit_post.html', {'form': form, 'post': post, 'tags': tags})

    
    
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
    profile = get_or_create_user_profile(profile_user)  # Профиль текущего пользователя
    image_profile = profile.image
    image_header_profile = profile.image_header
    is_subscribed = profile in request.user.profile.subscriptions.all() if request.user.is_authenticated else False
    posts = Post.objects.filter(author=profile)
    requested_posts = PostRequest.objects.filter(requester=profile_user)
    trending_posts = get_trending_posts()
    follower_count = profile.follower_count
    following_count = profile.following_count
    follow_profiles = profile.subscriptions.all()

    context = {
        'profile_user': profile_user,  # Сам User
        'image_profile': image_profile,
        'image_header_profile': image_header_profile,
        'posts': posts,
        'author': profile,  # Профиль, а не User
        'requested_posts': requested_posts,
        'trending_posts': trending_posts,
        'follower_count': follower_count,
        'following_count': following_count,
        'follow_profiles': follow_profiles,
        'is_subscribed': is_subscribed,
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
    profile = get_or_create_user_profile(request.user)
    
    # Использование F-экспрессии для увеличения счётчика просмотров
    post.views = F('views') + 1
    post.save(update_fields=['views'])
    post.refresh_from_db()
    
    # Получение комментариев
    comments = post.comments.all()
    follow_profiles = []
    trending_posts = get_trending_posts()
    follow_profiles = profile.subscriptions.all()
    
    context = {
        'post': post,
        'comments': comments,
        'likes_count': post.likes.count(),
        'comments_count': post.comments_count,
        'views_count': post.views,
        'author': profile,  # передача автора
        'trending_posts': trending_posts,
        'follow_profiles': follow_profiles,
    }
    
    return render(request, 'post_detail.html', context)


def explore(request):
    profile = get_or_create_user_profile(request.user)
    form = SearchForm(request.GET)
    posts = Post.objects.none()  # Начинаем с пустого QuerySet
    explored_profiles = Profile.objects.none()  # Инициализируем пустой QuerySet для профилей
    query = ''
    follow_profiles = []
    
    if request.user.is_authenticated:
        # Получаем профили, на которые подписан текущий пользователь
        follow_profiles = profile.subscriptions.all()
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            posts = Post.objects.filter(
                Q(content__icontains=query.lower()) | 
                Q(tag__name__icontains=query.lower()) | 
                Q(content__icontains=query.upper()) | 
                Q(tag__name__icontains=query.upper())
            )
            explored_profiles = explore_profile(query)
            
    trending_posts = get_trending_posts()

    context = {
        'form': form,
        'posts': posts,
        'query': query,
        'author': profile,
        'trending_posts': trending_posts,
        'explored_profiles': explored_profiles,
        'follow_profiles': follow_profiles,
    }
    return render(request, 'explore.html', context)


def explore_profile(query):
    if query:
        profiles = Profile.objects.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )
        return profiles
    return Profile.objects.none()


@login_required
def favorite_posts(request):
    profile = get_or_create_user_profile(request.user)
    favorites = Favorites.objects.filter(user=request.user.profile)
    trending_posts = get_trending_posts()
    follow_profiles = []
    follow_profiles = profile.subscriptions.all()
    
    context = {
        'follow_profiles': follow_profiles,
        'favorites': favorites, 
        'author': profile, 
        'trending_posts': trending_posts
    }
    
    return render(request, 'favorites.html', context)


def communities(request):
    follow_profiles = []
    profile = get_or_create_user_profile(request.user)
    # Получаем все теги
    tags = Tag.objects.all()
    trending_posts = get_trending_posts()
    
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
        
    follow_profiles = profile.subscriptions.all()
    
    context = {
        'follow_profiles': follow_profiles,
        'tags': tags, 
        'posts': posts, 
        'selected_tag': selected_tag_slug, 
        'author': profile, 
        'trending_posts': trending_posts
    }
    
    return render(request, 'communities.html', context)


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
    # Получаем профиль текущего пользователя
    profile = get_or_create_user_profile(request.user)
    chats = Chat.objects.filter(profiles=profile)
    
    # Инициализируем переменные для выбранного чата и профиля собеседника
    selected_chat = None
    messages = []
    other_profile = None

    if chat_id:
        selected_chat = get_object_or_404(Chat, id=chat_id, profiles=profile)
        messages = selected_chat.messages.all()
        other_profile = selected_chat.profiles.exclude(id=profile.id).first()

    # Передаем все чаты, сообщения и профиль другого пользователя в контекст
    context = {
        'chats': chats,
        'selected_chat': selected_chat,
        'messages': messages,
        'other_profile': other_profile,  # Передаем объект профиля
        'author': profile
    }
    return render(request, 'chat.html', context)


@login_required
def create_chat(request):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        try:
            recipient_profile = Profile.objects.get(id=recipient_id)
        except Profile.DoesNotExist:
            return redirect('chat_list')

        # Создание нового чата
        chat = Chat.objects.create()
        chat.profiles.add(request.user.profile, recipient_profile)
        chat.save()

        return redirect('chat_list_with_id', chat_id=chat.id)

    return redirect('chat_list')


@login_required
def search_chat(request):
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient_username')
        try:
            recipient_profile = Profile.objects.get(user__username=recipient_username)
        except Profile.DoesNotExist:
            # Если пользователь не найден, возвращаем сообщение об ошибке
            return render(request, 'chat.html', {'error': 'Пользователь не найден.'})

        # Проверяем, существует ли уже чат с этим пользователем
        chat = Chat.objects.filter(profiles=request.user.profile).filter(profiles=recipient_profile).first()

        context = {
            'recipient_profile': recipient_profile,
            'chat': chat,
        }
        return render(request, 'chat.html', context)

    return redirect('chat_list')


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


@login_required
def request_post(request, post_slug):
    post = get_object_or_404(Post, slug=post_slug)
    profile = get_or_create_user_profile(request.user)

    # Проверка: пользователь не может реквестить свой собственный пост
    if post.author.user == request.user:
        messages.error(request, "You cannot request your own post.")
        return redirect('profile', username=request.user.username)

    # Проверка на существующий запрос
    existing_request = PostRequest.objects.filter(post=post, requester=request.user).first()

    if existing_request:
        # Удаление существующего запроса
        existing_request.delete()
        messages.success(request, "Request removed.")
    else:
        # Создание нового запроса
        PostRequest.objects.create(post=post, requester=request.user)
        messages.success(request, "Post requested.")

    return redirect('profile', username=request.user.username)


def get_trending_posts():
    # Возвращает 5 постов с наибольшим количеством просмотров
    return Tag.objects.annotate(post_count=Count('post')).order_by('-post_count')[:5]


def search_users(request):
    query = request.GET.get('query', '')  # Получаем поисковый запрос из GET параметра
    users = User.objects.filter(
        Q(username__icontains=query)
    ) if query else User.objects.none()  # Если есть запрос, выполняем фильтрацию

    context = {
        'users': users,
        'query': query,
    }
    return render(request, 'home.html', context)


def search_profiles(query=None):
    profiles = Profile.objects.all()

    if query:
        profiles = profiles.filter(user__username__icontains=query)

    # Ограничиваем количество выводимых профилей до 5
    return profiles


def following_profiles(request):
    profile = get_object_or_404(Profile, user=request.user)
    following_profiles = profile.subscriptions.all()

    # Проверяем подписки
    follow_data = []
    for prof in following_profiles:
        follow_data.append({
            'profile': prof,
            'is_subscribed': request.user.profile in prof.subscribed_by.all()  # Проверяем, подписан ли текущий пользователь
        })

    context = {
        'follow_data': follow_data,  # Передаем данные о профилях и статусе подписки
    }
    return context


def followers(request, query=None):
    user_profile = get_or_create_user_profile(request.user)
    profiles = user_profile.subscribed_by.all()
    profile = get_or_create_user_profile(request.user)

    if query:
        profiles = profiles.filter(user__username__icontains=query)

    return render(request, 'followers.html', {'profiles': profiles, 'author': profile})


def following(request, query=None):
    user_profile = get_or_create_user_profile(request.user)
    profiles = user_profile.subscriptions.all()
    profile = get_or_create_user_profile(request.user)

    if query:
        profiles = profiles.filter(user__username__icontains=query)

    return render(request, 'following.html', {'profiles': profiles, 'author': profile})


def get_followers_user(request, user):
    profile = Profile.objects.get(user=request.user)
    followings = profile.subscribed_by.all()
    return render

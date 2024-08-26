from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('profile/<str:username>/', views.profile, name='profile_url'),
    path('logout/', views.logout_user, name='logout_user'),
    path('post_detail/<slug:slug>', views.post_detail, name='post_detail'),
    path('post_detail/<slug:slug>/comment', views.comment, name='comment'),
    path('post/<slug:slug>/like/', views.like_post, name='like_post'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    path('post/<slug:slug>/delete/', views.delete_post, name='delete_post'),
    path('explore/', views.explore, name='explore'),
    path('favorites/', views.favorite_posts, name='favorite_posts'),
    path('communities/', views.communities, name = 'communities'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('chats/', views.chat_list, name='chat_list'),  # Отображение всех чатов
    path('chats/<int:chat_id>/', views.chat_list, name='chat_list_with_id'),
    path('chats/create/', views.create_chat, name='create_chat'),
    path('chats/<int:chat_id>/send/', views.send_message, name='send_message'),
    path('subscribe/<str:username>/', views.subscribe, name='subscribe'),
    path('unsubscribe/<str:username>/', views.unsubscribe, name='unsubscribe'),
    path('profile/<str:username>/', views.profile, name='profile'),
]

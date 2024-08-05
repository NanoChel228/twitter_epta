from django.shortcuts import render, redirect, reverse
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def home(request):
    return render(request, 'home.html')


def register(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                user=form.save()
                login(request, user)
                return redirect('home')
        else:
            form = RegisterForm()
        return render(request, 'register.html', {'form':form})
    return redirect('home')


def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            message = 'Извините, такого пользователя не существует'
            return render(request, 'login.html', {'message': message})
    return render(request, 'login.html', {'message': message})
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import TelegramUser
import requests

TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_BOT_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'


def auth_view(request):
       return render(request, 'auth_app/auth.html')


def callback_view(request):
    # Получаем токен из параметров URL
    token = request.GET.get('token')
    if token:
        # Здесь вы можете проверить токен и получить информацию о пользователе
        # Для упрощения примера предполагаем, что токен совпадает с telegram_id

        # Получаем информацию о пользователе
        response = requests.get(f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getChat?chat_id={token}')
        user_data = response.json().get('result', {})

        # Проверяем, существует ли пользователь в базе данных
        telegram_id = user_data.get('id')
        username = user_data.get('username', '')

        telegram_user, created = TelegramUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={'username': username}
        )

        # Если пользователь создан, создаем стандартного пользователя Django
        if created:
            user = User.objects.create_user(username=username or f'user_{telegram_id}', password='defaultpassword')
            telegram_user.user = user
            telegram_user.save()

        # Логиним пользователя в Django
        login(request, telegram_user.user)

        return redirect('auth_view')

    return redirect('auth_view')
   

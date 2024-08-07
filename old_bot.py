import os
import django
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from django.conf import settings
from django.db import close_old_connections
from asgiref.sync import sync_to_async
from users.models import CustomUser

# Настройка Django
django.setup()

API_TOKEN = '7247982706:AAEnAk1pIXyINNYkSGzgVA_E4VVqmEz6LWc'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Установите переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

async def fetch_music_data(query):
    url = f"{settings.MUSIC_API_URL}?q={query}&api_key={settings.MUSIC_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    close_old_connections()  # Закрыть старые соединения
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    # Используйте sync_to_async для выполнения синхронных операций
    user, created = await sync_to_async(CustomUser.objects.get_or_create)(
        telegram_id=user_id,
        defaults={'username': username, 'first_name': full_name}
    )

    if not created:
        user.username = username
        user.first_name = full_name
        await sync_to_async(user.save)()

    await message.reply(f"Привет, {full_name}! Ваш ID: {user_id}, Username: {username}")

@dp.message_handler(commands=['search'])
async def search(message: types.Message):
    query = message.get_args()
    if not query:
        await message.reply("Please provide a search query.")
        return

    music_data = await fetch_music_data(query)
    if music_data:
        # Пример обработки полученных данных
        response_text = f"Results for '{query}':\n"
        for item in music_data.get('results', []):
            response_text += f"Title: {item.get('title')}\n"
            response_text += f"Artist: {item.get('artist')}\n"
            response_text += f"URL: {item.get('url')}\n\n"

        await message.reply(response_text)
    else:
        await message.reply("No results found or there was an error with the API.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

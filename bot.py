

# bot.py
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from django.db import close_old_connections
from asgiref.sync import sync_to_async
from users.models import CustomUser
from django_setup import setup_django

# Инициализация Django
setup_django()

API_TOKEN = '7247982706:AAEnAk1pIXyINNYkSGzgVA_E4VVqmEz6LWc'
DEEZER_API_KEY = '3cb17374cfmshbd415264f7a22dcp1493d8jsnaad6bdc307c4'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

async def fetch_deezer_info():
    url = "https://deezerdevs-deezer.p.rapidapi.com/infos"
    headers = {
        'x-rapidapi-key': DEEZER_API_KEY,
        'x-rapidapi-host': 'deezerdevs-deezer.p.rapidapi.com'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    close_old_connections()
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    user, created = await sync_to_async(CustomUser.objects.get_or_create)(
        telegram_id=user_id,
        defaults={'username': username, 'first_name': full_name}
    )

    if not created:
        user.username = username
        user.first_name = full_name
        await sync_to_async(user.save)()

    await message.reply(f"Привет, {full_name}! Ваш ID: {user_id}, Username: {username}")

@dp.message_handler(commands=['info'])
async def info(message: types.Message):
    deezer_info = await fetch_deezer_info()
    if deezer_info:
        response_text = f"Deezer Info:\n{deezer_info}"
        await message.reply(response_text)
    else:
        await message.reply("Failed to fetch Deezer info.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

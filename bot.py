import os
import sys
import requests
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEB_APP_URL = os.getenv('WEB_APP_URL', 'http://localhost:5000')

# Отключаем обработку сигналов (нужно для работы в потоке)
if sys.platform != 'win32':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_promo_from_api(keyword):
    """Получает промокод из веб-приложения"""
    try:
        response = requests.get(f"{WEB_APP_URL}/api/promo/{keyword}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching promo: {e}")
    return None

def format_promo_message(data):
    """Форматирует сообщение с промокодом"""
    text = f"{data.get('emoji', '')} **{data['title']}**\n\n"
    text += f"🎫 *Промокод:* `{data['promo']}`\n\n"
    text += f"📋 *Условия:*\n{data['conditions']}\n\n"
    text += f"🔗 [Перейти на сайт]({data['link']})"
    return text

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    pass

@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return
    
    keyword = message.text.lower().strip()
    promo_data = get_promo_from_api(keyword)
    
    if promo_data and 'error' not in promo_data:
        text = format_promo_message(promo_data)
        try:
            await message.answer(text, parse_mode="Markdown")
        except:
            await message.answer(text)

async def start_bot():
    """Запуск бота без обработки сигналов"""
    logger.info("🤖 Telegram bot is starting...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        # Отключаем skip_updates чтобы не было ошибки set_wakeup_fd
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.session.close()
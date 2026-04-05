import os
import requests
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
import asyncio
import logging

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEB_APP_URL = os.getenv('WEB_APP_URL', 'http://localhost:5000')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_promo_from_api(keyword):
    try:
        response = requests.get(f"{WEB_APP_URL}/api/promo/{keyword}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Error: {e}")
    return None

@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return
    keyword = message.text.lower().strip()
    promo_data = get_promo_from_api(keyword)
    if promo_data and 'error' not in promo_data:
        text = f"**{promo_data['title']}**\n\n"
        text += f"Промокод: `{promo_data['promo']}`\n\n"
        text += f"Условия:\n{promo_data['conditions']}\n\n"
        text += f"Ссылка: {promo_data['link']}"
        try:
            await message.answer(text, parse_mode="Markdown")
        except:
            await message.answer(text)

async def main():
    logger.info("🤖 Bot starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
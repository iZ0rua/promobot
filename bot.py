import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Подключение к базе данных
import psycopg2
DATABASE_URL = os.getenv("DATABASE_URL")

def get_promo(keyword):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            "SELECT title, promo, conditions, link FROM promo WHERE keyword = %s",
            (keyword.lower(),)
        )
        row = cur.fetchone()
        conn.close()
        if row:
            return {"title": row[0], "promo": row[1], "conditions": row[2], "link": row[3]}
    except Exception as e:
        logger.error(f"DB error: {e}")
    return None

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return
    keyword = message.text.lower().strip()
    promo = get_promo(keyword)
    if promo:
        text = f"*{promo['title']}*\n"
        text += f"Промокод: `{promo['promo']}`\n"
        if promo.get('conditions'):
            text += f"Условия:\n{promo['conditions']}\n"
        if promo.get('link'):
            text += f"Ссылка: {promo['link']}"
        try:
            await message.answer(text)
        except:
            await message.answer(text, parse_mode=None)

async def main():
    logger.info("Bot starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
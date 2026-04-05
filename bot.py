import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- НАСТРОЙКИ --- впиши свои значения ---
BOT_TOKEN = "8625632756:AAE9eQ347b06t8v9cH9vv0MyLCBA1OIklus"
WEB_APP_URL = "https://promobot-wtxs.onrender.com"
# -----------------------------------------

def get_promo(keyword):
    try:
        response = requests.get(
            f"{WEB_APP_URL}/api/promo/{keyword}",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if "error" not in data:
                return data
    except Exception as e:
        logger.error(f"API error: {e}")
    return None

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return
    keyword = message.text.lower().strip()
    promo = get_promo(keyword)
    if not promo:
        return
    text = f"*{promo['title']}*\n"
    text += f"Промокод: `{promo['promo']}`\n"
    if promo.get("conditions"):
        for line in promo["conditions"].split("\n"):
            if line.strip():
                text += f" - {line.strip()}\n"
    if promo.get("link"):
        text += f"\n[Перейти на сайт]({promo['link']})"
    try:
        await message.answer(text)
    except Exception:
        await message.answer(text, parse_mode=None)

async def main():
    logger.info("Bot starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
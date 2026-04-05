import asyncio
import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties

# Настройка логирования (показывает больше деталей)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# --- НАСТРОЙКИ ---
# Берём токен из переменных окружения (безопаснее!)
BOT_TOKEN = os.getenv('BOT_TOKEN', '8625632756:AAE9eQ347b06t8v9cH9vv0MyLCBA1OIklus')
WEB_APP_URL = os.getenv('WEB_APP_URL', 'https://promobot-gdjx.onrender.com')

def get_promo(keyword):
    """Запрашивает промокод из API"""
    try:
        logger.info(f"🔍 Запрос промокода: {keyword}")
        response = requests.get(
            f"{WEB_APP_URL}/api/promo/{keyword}",
            timeout=5
        )
        logger.info(f"📡 Ответ API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "error" not in data:
                logger.info(f"✅ Промокод найден: {data.get('title')}")
                return data
            else:
                logger.warning(f"⚠️ API вернул ошибку: {data}")
        else:
            logger.warning(f"⚠️ API вернул статус: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ API error: {e}")
    return None

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    """Обрабатывает ВСЕ текстовые сообщения"""
    # Игнорируем не-текст
    if not message.text:
        return
    
    # Логируем входящее сообщение
    user = message.from_user
    text = message.text.strip()
    logger.info(f"💬 Сообщение от @{user.username} (ID: {user.id}): '{text}'")
    
    # Ищем промокод
    keyword = text.lower()
    promo = get_promo(keyword)
    
    if promo:
        # Формируем ответ
        reply = f"*{promo['title']}*\n"
        reply += f"Промокод: `{promo['promo']}`\n"
        
        if promo.get("conditions"):
            for line in promo["conditions"].split("\n"):
                if line.strip():
                    reply += f" - {line.strip()}\n"
        
        if promo.get("link"):
            reply += f"\n[Перейти на сайт]({promo['link']})"
        
        # Отправляем ответ
        try:
            await message.answer(reply)
            logger.info(f"✅ Ответ отправлен пользователю {user.id}")
        except Exception as e:
            logger.error(f"❌ Не удалось отправить сообщение: {e}")
            # Пробуем отправить без форматирования
            try:
                await message.answer(reply, parse_mode=None)
            except:
                pass
    else:
        # Промокод не найден — молчим (как и задумано)
        logger.info(f"🤫 Промокод '{keyword}' не найден, пропускаем")

async def main():
    logger.info("🤖 Bot starting...")
    logger.info(f"🔑 Token: {BOT_TOKEN[:10]}...")  # Показываем начало токена для проверки
    logger.info(f"🌐 API URL: {WEB_APP_URL}")
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("🪝 Webhook удалён, запускаем polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
    finally:
        await bot.session.close()
        logger.info("🔚 Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main())
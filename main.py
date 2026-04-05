import os
import sys
import asyncio
import threading
import logging
from app import create_app
from bot import start_bot
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def run_bot():
    """Функция для запуска бота в отдельном потоке"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_bot())
    except Exception as e:
        logger.error(f"❌ Бот упал: {e}")
    finally:
        loop.close()

if __name__ == '__main__':
    # 1. Создаем приложение Flask
    try:
        app = create_app()
        logger.info("✅ Flask app created")
    except Exception as e:
        logger.error(f"❌ Ошибка Flask: {e}")
        sys.exit(1)

    # 2. Запускаем бота в фоне
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("✅ Bot thread started")

    # 3. Запускаем сайт
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Сайт запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)
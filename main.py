import os
import sys
import threading
import asyncio
import logging
from app import create_app
from bot import start_bot
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def start_bot_thread():
    """Запускает бота в фоновом потоке"""
    def run():
        try:
            logger.info("🤖 Запуск Telegram бота...")
            asyncio.run(start_bot())
        except Exception as e:
            logger.error(f"❌ Бот упал: {e}")
            sys.exit(1)
            
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

try:
    # Создаём Flask приложение
    app = create_app()
    
    # Запускаем бота в фоне
    start_bot_thread()
    
    # Запускаем веб-сервер
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)
    
except Exception as e:
    logger.error(f"💥 Критическая ошибка при запуске: {e}")
    sys.exit(1)
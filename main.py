import os
import asyncio
import threading
import logging
from concurrent.futures import ThreadPoolExecutor
from app import create_app
from bot import dp, bot, on_startup, on_shutdown
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def run_bot():
    """Запускает бота в отдельном event loop"""
    async def start_bot():
        try:
            await on_startup()
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
        finally:
            await on_shutdown()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

try:
    # Создаём Flask приложение
    app = create_app()
    
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("✅ Bot thread started")
    
    # Запускаем веб-сервер
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Server running on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)
    
except Exception as e:
    logger.error(f"💥 Critical error: {e}")
    import traceback
    traceback.print_exc()
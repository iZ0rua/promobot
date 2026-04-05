import os
import threading
import asyncio
from app import create_app
from bot import start_bot
from dotenv import load_dotenv

load_dotenv()

# Создаём Flask приложение
app = create_app()

def run_bot():
    """Запускает бота в отдельном потоке"""
    print("🤖 Starting Telegram bot...")
    try:
        asyncio.run(start_bot())
    except Exception as e:
        print(f"❌ Bot error: {e}")

if __name__ == '__main__':
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем веб-сервер
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting web server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
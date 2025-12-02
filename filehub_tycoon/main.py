# File Hub Tycoon Simulator
# Telegram Bot для симуляции управления файловым хабом

import os
import signal
import sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from http.server import HTTPServer, BaseHTTPRequestHandler

from utils.config import Config
from utils.database import Database
from utils.state_manager import StateManager
from handlers.command_handlers import CommandHandlers
from handlers.callback_handlers import CallbackHandlers
from game.game_engine import GameEngine
from game.models import GameState

# Загрузка переменных окружения
load_dotenv()

# Глобальные переменные для graceful shutdown
bot_app = None
shutdown_flag = False

class TorrentTrackerBot:
    def __init__(self):
        self.config = Config()
        self.db = Database()
        self.state_manager = StateManager(self.db)
        self.game_engine = GameEngine()
        
        # Инициализация приложения бота
        self.application = Application.builder().token(
            self.config.BOT_TOKEN
        ).build()
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка обработчиков команд и callback-запросов"""
        command_handlers = CommandHandlers(self.state_manager, self.game_engine)
        callback_handlers = CallbackHandlers(self.state_manager, self.game_engine)
        
        # Обработчики команд
        self.application.add_handler(CommandHandler("start", command_handlers.start_command))
        self.application.add_handler(CommandHandler("dashboard", command_handlers.dashboard_command))
        self.application.add_handler(CommandHandler("plan", command_handlers.plan_command))
        self.application.add_handler(CommandHandler("hire", command_handlers.hire_command))
        self.application.add_handler(CommandHandler("upgrade", command_handlers.upgrade_command))
        self.application.add_handler(CommandHandler("marketing", command_handlers.marketing_command))
        self.application.add_handler(CommandHandler("hosting", command_handlers.hosting_command))
        self.application.add_handler(CommandHandler("law", command_handlers.law_command))
        self.application.add_handler(CommandHandler("community", command_handlers.community_command))
        self.application.add_handler(CommandHandler("report", command_handlers.report_command))
        self.application.add_handler(CommandHandler("next", command_handlers.next_turn_command))
        self.application.add_handler(CommandHandler("save", command_handlers.save_command))
        self.application.add_handler(CommandHandler("load", command_handlers.load_command))
        
        # Обработчики callback-запросов
        self.application.add_handler(CallbackQueryHandler(callback_handlers.handle_callback))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, command_handlers.handle_text))
    
    def run(self):
        """Запуск бота"""
        print("🚀 Запуск Torrent Tracker Tycoon Bot...")
        
        # Регистрируем обработчики сигналов для graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        global shutdown_flag
        print(f"\n🛑 Получен сигнал {signum}, инициируем graceful shutdown...")
        shutdown_flag = True
        if self.application:
            self.application.stop()
        sys.exit(0)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Health check handler для Railway"""
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Отключаем логирование health checks"""
        pass

def start_health_server():
    """Запуск health check сервера"""
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"🏥 Health check server запущен на порту {port}")
    server.serve_forever()

def main():
    """Главная функция"""
    # Запускаем health check сервер в отдельном потоке
    import threading
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Запускаем бота
    bot = TorrentTrackerBot()
    bot.run()

if __name__ == "__main__":
    main()
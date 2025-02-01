import asyncio
import threading
from django.core.management import call_command
from django.apps import AppConfig

class TelegramBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bot'

    def ready(self):
        # Faqatgina asosiy Django ilovasi ishga tushganda botni ishga tushurish
        if not self.is_running_test():
            thread = threading.Thread(target=self.run_bot)
            thread.daemon = True  # Django yopilganda thread ham to'xtashi uchun
            thread.start()

    def run_bot(self):
        # Async event loop yaratish va botni ishga tushurish
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            call_command('start_bot')  # Telegram botni ishga tushirish
        except Exception as e:
            print(f"Botni ishga tushirishda xatolik yuz berdi: {e}")

    def is_running_test(self):
        # Test rejimida ishlayotganligini tekshirish
        import sys
        return 'test' in sys.argv
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Start the Telegram bot'

    def handle(self, *args, **kwargs):
        from telegram_bot.bot import main  # Telegram botning asosiy funksiyasini chaqirish
        self.stdout.write("Starting Telegram Bot...")
        main()  # Telegram botni ishga tushurish

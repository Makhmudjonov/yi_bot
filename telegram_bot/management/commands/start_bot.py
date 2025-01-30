# telegram_bot/management/commands/start_bot.py
from django.core.management.base import BaseCommand
from telegram_bot.bot import main  # bot.py ichidagi main funksiyasini import qilamiz

class Command(BaseCommand):
    help = 'Start the Telegram bot'

    def handle(self, *args, **kwargs):
        self.stdout.write('Botni ishga tushurish...')
        main()  # botni ishga tushirish

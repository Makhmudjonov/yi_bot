from django.core.management.base import BaseCommand
from telegram_bot.bot import main  # Botni ishga tushiruvchi funksiya

class Command(BaseCommand):
    help = 'Telegram botni ishga tushirish'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Bot ishga tushmoqda...'))
        main()  # Botni ishga tushirish
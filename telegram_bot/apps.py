from django.apps import AppConfig
from django.core.management import call_command

class TelegramBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bot'

    def ready(self):
        # Django ilovasi ishga tushganda, botni ishga tushurish
        call_command('start_bot')



 

    

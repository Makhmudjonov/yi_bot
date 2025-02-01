from django.db import models

class UserData(models.Model):
    user_id = models.BigIntegerField()  # Foydalanuvchi ID (Telegram ID)
    name = models.CharField(max_length=255)  # Foydalanuvchi ismi
    surname = models.CharField(max_length=255)  # Familiya
    faculty = models.CharField(max_length=255)  # Fakultet
    course = models.IntegerField()  # Kurs (1-6)
    direction = models.CharField(max_length=255)  # Yo'nalish
    phone_number = models.CharField(max_length=15, null=True)  # Telefon raqami
    material_type = models.CharField(max_length=50, null=True)  # Material turi (video, rasm, fayl)
    material_file_id = models.CharField(max_length=255, null=True)  # Materialning file ID
    material_file_link = models.CharField(max_length=512, null=True, blank=True)  # Media fayl linki
    created_at = models.DateTimeField(auto_now_add=True)  # Yuborilgan sana va vaqt
    is_confirmed = models.BooleanField(default=False)  # Tasdiqlanganligini tekshirish

    def __str__(self):
        return f'{self.name} {self.surname}'

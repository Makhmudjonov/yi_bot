import logging
from asgiref.sync import sync_to_async  # Django ORM uchun
import telegram
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackContext,
    ConversationHandler
)
from .models import UserData

# 🔹 Bot sozlamalari
TELEGRAM_TOKEN = '7568610120:AAE3WLLatYjv2GwR4raqHr2EANeycACVk-8'
CHANNEL_ID = '@TTA_Yoshlar_Ittifoqi'
GROUP_ID = '-1002418149612'  # Guruh ID (-100 bilan boshlanadi)
USER_DATA = {}  # Foydalanuvchi vaqtinchalik ma'lumotlari

# 🔹 Holatlar
CONTACT, SURNAME, NAME, FACULTY, COURSE, DIRECTION, MATERIAL, CONFIRM = range(8)

# 🔹 Log sozlamalari
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔹 Django ORM async funksiya
@sync_to_async
def create_or_update_user_data(user_id, name, surname, faculty, course, direction, phone_number, material_type, material_file_id):
    # Foydalanuvchi mavjudligini tekshirish
    user_data = UserData.objects.filter(user_id=user_id).first()

    if user_data:
        # Foydalanuvchi mavjud bo'lsa, yangilaymiz
        user_data.name = name
        user_data.surname = surname
        user_data.faculty = faculty
        user_data.course = course
        user_data.direction = direction
        user_data.phone_number = phone_number
        user_data.material_type = material_type
        user_data.material_file_id = material_file_id
        user_data.save()
    else:
        # Agar foydalanuvchi mavjud bo'lmasa, yangi yaratamiz
        user_data = UserData.objects.create(
            user_id=user_id,
            name=name,
            surname=surname,
            faculty=faculty,
            course=course,
            direction=direction,
            phone_number=phone_number,
            material_type=material_type,
            material_file_id=material_file_id
        )

    return user_data

@sync_to_async
def get_user_data(user_id):
    return UserData.objects.get(user_id=user_id)

@sync_to_async
def update_user_data(user_data):
    user_data.is_confirmed = True
    user_data.save()

# 🔹 /start komandasi
async def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id

    # 🔸 Kanalga a'zo bo'lganini tekshirish
    chat_member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
    if chat_member.status not in ["member", "administrator", "creator"]:
        await update.message.reply_text(
            f"Salom! Iltimos, {CHANNEL_ID} kanaliga a'zo bo'ling va /start ni qayta bosing."
        )
        return ConversationHandler.END

    # 🔸 Kontakt so‘rash
    USER_DATA[user_id] = {}
    await update.message.reply_text("Iltimos, kontaktingizni yuboring.",
                                    reply_markup=telegram.ReplyKeyboardMarkup(
                                        [[telegram.KeyboardButton("📱 Kontakt yuborish", request_contact=True)]],
                                        one_time_keyboard=True
                                    ))
    return CONTACT

# 🔹 Kontakt qabul qilish
async def handle_contact(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    USER_DATA[user_id]['contact'] = update.message.contact.phone_number
    await update.message.reply_text("Familiyangizni kiriting:")
    return SURNAME

# 🔹 Familiya qabul qilish
async def surname(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    USER_DATA[user_id]['surname'] = update.message.text
    await update.message.reply_text("Ismingizni kiriting:")
    return NAME

# 🔹 Ism qabul qilish
async def name(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    USER_DATA[user_id]['name'] = update.message.text
    await update.message.reply_text("Fakultetingizni tanlang (IT, Ekonomika, Gumanitar):")
    return FACULTY

# 🔹 Fakultet qabul qilish
async def faculty(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    USER_DATA[user_id]['faculty'] = update.message.text
    await update.message.reply_text("Kursni tanlang (1-6):")
    return COURSE

# 🔹 Kurs qabul qilish
async def course(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    try:
        course = int(update.message.text)
        if 1 <= course <= 6:
            USER_DATA[user_id]['course'] = course
            await update.message.reply_text("Yo‘nalishni tanlang (Web, Data Science, AI):")
            return DIRECTION
    except ValueError:
        pass
    await update.message.reply_text("Iltimos, 1-6 oralig‘ida kursni kiriting.")
    return COURSE

# 🔹 Yo'nalish qabul qilish
async def direction(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    direction = update.message.text

    # Foydalanuvchi shu yo'nalish uchun ro'yxatdan o'tganligini tekshirish
    existing_user = await UserData.objects.filter(user_id=user_id, direction=direction).first()
    if existing_user:
        await update.message.reply_text("Siz avval ushbu yo'nalishda ro'yxatdan o'tgansiz.")
        return ConversationHandler.END

    USER_DATA[user_id]['direction'] = direction
    await update.message.reply_text("Material yuboring (video, rasm, hujjat):")
    return MATERIAL

# 🔹 Material qabul qilish
async def material(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    material_type, material_file_id = None, None

    if update.message.video:
        material_type, material_file_id = "video", update.message.video.file_id
    elif update.message.photo:
        material_type, material_file_id = "photo", update.message.photo[-1].file_id
    elif update.message.document:
        material_type, material_file_id = "document", update.message.document.file_id

    if material_type:
        # Foydalanuvchi ma'lumotlarini yaratish yoki yangilash
        await create_or_update_user_data(user_id, USER_DATA[user_id]['name'], USER_DATA[user_id]['surname'],
                                         USER_DATA[user_id]['faculty'], USER_DATA[user_id]['course'],
                                         USER_DATA[user_id]['direction'], USER_DATA[user_id]['contact'],
                                         material_type, material_file_id)

        await update.message.reply_text("Ma'lumotlaringizni tasdiqlaysizmi? (Ha / Yo'q)")
        return CONFIRM
    else:
        await update.message.reply_text("Iltimos, video, rasm yoki fayl yuboring.")
        return MATERIAL

# 🔹 Tasdiqlash
async def confirm(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    if update.message.text.lower() in ["ha", "yes"]:
        user_data = await get_user_data(user_id)

        # 🔸 Materialni guruhga jo‘natish
        if user_data.material_type == "video":
            await context.bot.send_video(GROUP_ID, video=user_data.material_file_id, caption=str(user_data))
        elif user_data.material_type == "photo":
            await context.bot.send_photo(GROUP_ID, photo=user_data.material_file_id, caption=str(user_data))
        elif user_data.material_type == "document":
            await context.bot.send_document(GROUP_ID, document=user_data.material_file_id, caption=str(user_data))

        await update.message.reply_text("Ma'lumotlaringiz guruhga yuborildi.")
        await update_user_data(user_data)

    return ConversationHandler.END

# 🔹 Botni ishga tushirish
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONTACT: [MessageHandler(filters.CONTACT, handle_contact)],
            SURNAME: [MessageHandler(filters.TEXT, surname)],
            NAME: [MessageHandler(filters.TEXT, name)],
            FACULTY: [MessageHandler(filters.TEXT, faculty)],
            COURSE: [MessageHandler(filters.TEXT, course)],
            DIRECTION: [MessageHandler(filters.TEXT, direction)],
            MATERIAL: [MessageHandler(filters.ALL, material)],
            CONFIRM: [MessageHandler(filters.TEXT, confirm)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()

import logging
from asgiref.sync import sync_to_async
import telegram
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackContext,
    ConversationHandler
)
from .models import UserData
from datetime import datetime

# 🔹 Bot sozlamalari
TELEGRAM_TOKEN = '7568610120:AAH4NuORomzRJ9c2RlPxsSdYhlUQ-apbMWk'  # Tokenni o'zgartiring
CHANNEL_ID = '@TTA_Yoshlar_Ittifoqi'
GROUP_ID = '-1002418149612'  # Guruh ID (-100 bilan boshlanadi)

# 🔹 Holatlar
CONTACT, SURNAME, NAME, FACULTY, COURSE, DIRECTION, MATERIAL, CONFIRM = range(8)

# 🔹 Log sozlamalari
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🔹 Django ORM async funksiyalari
@sync_to_async
def create_user_data(user_id, name, surname, faculty, course, direction, phone_number, material_type, material_file_id, material_file_link):
    logger.info(f"Yangi foydalanuvchi ma'lumotlarini saqlamoqda: {user_id}, {name} {surname}")
    return UserData.objects.create(
        user_id=user_id,
        name=name,
        surname=surname,
        faculty=faculty,
        course=course,
        direction=direction,
        phone_number=phone_number,
        material_type=material_type,
        material_file_id=material_file_id,
        material_file_link=material_file_link
    )

@sync_to_async
def get_user_data(user_id):
    return UserData.objects.filter(user_id=user_id).first()

@sync_to_async
def check_existing_registration(user_id, direction):
    return UserData.objects.filter(user_id=user_id, direction=direction).exists()

@sync_to_async
def update_user_data(user_data):
    user_data.is_confirmed = True
    user_data.save()

@sync_to_async
def get_all_user_data(user_id):
    return list(UserData.objects.filter(user_id=user_id))

@sync_to_async
def get_last_user_data(user_id):
    try:
        # created_at bo'yicha eng so'nggi yozuvni qaytaramiz
        return UserData.objects.filter(user_id=user_id).latest('created_at')
    except UserData.DoesNotExist:
        return None

# 🔹 /start komandasi
async def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    try:
        chat_member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        if chat_member.status not in ["member", "administrator", "creator"]:
            await update.message.reply_text(
                f"Salom! Iltimos, {CHANNEL_ID} kanaliga a'zo bo'ling va /start ni qayta bosing."
            )
            return ConversationHandler.END
    except Exception as e:
        logger.error(f"Kanalga a'zolikni tekshirishda xatolik: {e}")
        await update.message.reply_text("Kanalga a'zolikni tekshirishda xatolik yuz berdi.")
        return ConversationHandler.END

    context.user_data.clear()
    await update.message.reply_text(
        "Iltimos, kontaktingizni yuboring.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Kontakt yuborish", request_contact=True)]],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    return CONTACT

# 🔹 Kontakt qabul qilish
async def handle_contact(update: Update, context: CallbackContext) -> int:
    context.user_data['contact'] = update.message.contact.phone_number
    await update.message.reply_text("Familiyangizni kiriting:")
    return SURNAME

# 🔹 Familiya qabul qilish
async def surname(update: Update, context: CallbackContext) -> int:
    context.user_data['surname'] = update.message.text
    await update.message.reply_text("Ismingizni kiriting:")
    return NAME

# 🔹 Ism qabul qilish
async def name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    faculty_buttons = faculty_buttons = [
    ["1-son davolash", "2-son davolash"],
    ["Tibbiy profilaktika va jamoat salomatligi, ekologiya va atrof muhit muhofazasi va kimyo"],
    ["Pediatriya, stomatologiya, xalqtabobati va tibbiy pedagogika"],
    ["Farmatsiya, menejment, tibbiybiologiya, biotibbiyot muhandisligiva oliy ma'lumotli hamshira"],
    ["Xalqaro"]
]
    await update.message.reply_text(
        "Fakultetingizni tanlang:",
        reply_markup=ReplyKeyboardMarkup(faculty_buttons, one_time_keyboard=True, resize_keyboard=True)
    )
    return FACULTY

# 🔹 Fakultet qabul qilish (faqat tugmalar orqali)
# Fakultet qabul qilish (faqat tugmalar orqali)
async def faculty(update: Update, context: CallbackContext) -> int:
    valid_faculties = [
        "1-son davolash", "2-son davolash",
        "Tibbiy profilaktika va jamoat salomatligi, ekologiya va atrof muhit muhofazasi va kimyo",
        "Pediatriya, stomatologiya, xalqtabobati va tibbiy pedagogika",
        "Farmatsiya, menejment, tibbiybiologiya, biotibbiyot muhandisligiva oliy ma'lumotli hamshira",
        "Xalqaro"
    ]
    if update.message.text not in valid_faculties:
        await update.message.reply_text("Iltimos, tugmalardan foydalaning.")
        return FACULTY
    context.user_data['faculty'] = update.message.text
    course_buttons = [["1", "2", "3"], ["4", "5", "6"]]
    await update.message.reply_text(
        "Kursni tanlang:",
        reply_markup=ReplyKeyboardMarkup(course_buttons, one_time_keyboard=True, resize_keyboard=True)
    )
    return COURSE

# 🔹 Kurs qabul qilish (faqat tugmalar orqali)
async def course(update: Update, context: CallbackContext) -> int:
    if update.message.text not in ["1", "2", "3", "4", "5", "6"]:
        await update.message.reply_text("Iltimos, tugmalardan foydalaning: 1, 2, 3, 4, 5 yoki 6")
        return COURSE
    context.user_data['course'] = int(update.message.text)
    direction_buttons = [["Eng yaxshi videorilik", "Eng yaxshi maqola", "Navoiyshunos bilimdon"]]
    await update.message.reply_text(
        "Yo‘nalishni tanlang:",
        reply_markup=ReplyKeyboardMarkup(direction_buttons, one_time_keyboard=True, resize_keyboard=True)
    )
    return DIRECTION

# 🔹 Yo'nalish qabul qilish (faqat tugmalar orqali)
# Yo'nalish qabul qilish (faqat tugmalar orqali)
# Yo'nalish qabul qilish (faqat tugmalar orqali)
async def direction(update: Update, context: CallbackContext) -> int:
    valid_directions = ["Eng yaxshi videorilik", "Eng yaxshi maqola", "Navoiyshunos bilimdon"]
    
    # Agar foydalanuvchi tugmalardan tashqari matn kiritgan bo'lsa
    if update.message.text not in valid_directions:
        await update.message.reply_text("Iltimos, belgilangan yo'nalishlardan birini tanlang:")
        return DIRECTION

    context.user_data['direction'] = update.message.text
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
        # Fayl linkini olish
        file_obj = await context.bot.get_file(material_file_id)
        file_link = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_obj.file_path}"
        await create_user_data(
            user_id, 
            context.user_data['name'], 
            context.user_data['surname'],
            context.user_data['faculty'], 
            context.user_data['course'],
            context.user_data['direction'], 
            context.user_data['contact'],
            material_type, 
            material_file_id,
            file_link
        )
        confirm_buttons = [["Ha", "Yo'q"]]
        await update.message.reply_text(
            "Ma'lumotlaringizni tasdiqlaysizmi?",
            reply_markup=ReplyKeyboardMarkup(confirm_buttons, one_time_keyboard=True, resize_keyboard=True)
        )
        return CONFIRM
    else:
        await update.message.reply_text("Iltimos, video, rasm yoki fayl yuboring.")
        return MATERIAL

# 🔹 Tasdiqlash (faqat tugmalar orqali, faqat so'nggi yuborilgan yozuv guruhga yuboriladi)
async def confirm(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() not in ["ha", "yo'q", "yes", "no"]:
        await update.message.reply_text("Iltimos, faqat 'Ha' yoki 'Yo'q' tugmalaridan foydalaning.")
        return CONFIRM
    user_id = update.message.chat_id
    if update.message.text.lower() in ["ha", "yes"]:
        last_user_data = await get_last_user_data(user_id)
        if last_user_data:
            created_str = last_user_data.created_at.strftime("%Y-%m-%d %H:%M:%S")
            caption = (
                f"Foydalanuvchi: {last_user_data.name} {last_user_data.surname}\n"
                f"Fakultet: {last_user_data.faculty}\n"
                f"Kurs: {last_user_data.course}\n"
                f"Yo'nalish: {last_user_data.direction}\n"
                f"Telefon: {last_user_data.phone_number}\n"
                f"Fayl linki: {last_user_data.material_file_link}\n"
                f"Yuborilgan sana va vaqt: {created_str}"
            )
            try:
                if last_user_data.material_type == "video":
                    await context.bot.send_video(GROUP_ID, video=last_user_data.material_file_id, caption=caption)
                elif last_user_data.material_type == "photo":
                    await context.bot.send_photo(GROUP_ID, photo=last_user_data.material_file_id, caption=caption)
                elif last_user_data.material_type == "document":
                    await context.bot.send_document(GROUP_ID, document=last_user_data.material_file_id, caption=caption)
            except Exception as e:
                logger.error(f"Media yuborishda xatolik: {e}")
            await update.message.reply_text("Ma'lumotlaringiz guruhga yuborildi.")
    context.user_data.clear()
    return ConversationHandler.END

# 🔹 Botni ishga tushirish
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.request_kwargs = {"timeout": 60}
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONTACT: [MessageHandler(filters.CONTACT, handle_contact)],
            SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, surname)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            FACULTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, faculty)],
            COURSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, course)],
            DIRECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, direction)],
            MATERIAL: [MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, material)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()

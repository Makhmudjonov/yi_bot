from django.conf import settings
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.ext import ConversationHandler
from .models import UserData
import logging

# Bot tokenini o'zgartiring
TELEGRAM_TOKEN = '7568610120:AAE3WLLatYjv2GwR4raqHr2EANeycACVk-8'
CHANNEL_ID = '@TTA_Yoshlar_Ittifoqi'  # Kanal ID
GROUP_ID = '2418149612'  # Guruh ID
USER_DATA = {}  # Foydalanuvchi ma'lumotlarini saqlash

# Vazifalar uchun holatlar
CONTACT, SURNAME, NAME, FACULTY, COURSE, DIRECTION, MATERIAL, CONFIRM = range(8)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. /start buyrug'ini qo'llash
async def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id

    # Kanalga a'zo bo'lishni tekshirish
    if update.message.chat.type == 'channel':
        chat_member = await update.message.chat.get_member(user_id)
        if chat_member.status != 'member':
            await update.message.reply_text(
                f"Salom! Iltimos, {CHANNEL_ID} kanaliga a'zo bo'ling, so'ngra botdan foydalanishni davom ettirishingiz mumkin."
            )
            return ConversationHandler.END

    # A'zo bo'lgan foydalanuvchidan kontakt so'rash
    user_data = USER_DATA.setdefault(user_id, {'step': 0})
    user_data['step'] = 1
    await update.message.reply_text('Kanalga a\'zo bo\'lgansiz. Iltimos, kontaktingizni yuboring.')
    return CONTACT


# 2. Kontaktni qayta ishlash
async def handle_contact(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    contact = update.message.contact
    USER_DATA[user_id]['contact'] = contact.phone_number
    USER_DATA[user_id]['step'] = 2
    await update.message.reply_text('Familiyangizni kiriting:')  # to'g'ri metod
    return SURNAME

# 3. Familiya
async def surname(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    surname = update.message.text
    USER_DATA[user_id]['surname'] = surname
    await update.message.reply_text('Ismingizni kiriting:')
    return NAME

# 4. Ism
async def name(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    name = update.message.text
    USER_DATA[user_id]['name'] = name
    await update.message.reply_text('Fakultetingizni tanlang (IT, Ekonomika, Gumanitar):')
    return FACULTY

# 5. Fakultet
async def faculty(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    faculty = update.message.text
    USER_DATA[user_id]['faculty'] = faculty
    await update.message.reply_text('Kursni tanlang (1-6):')
    return COURSE

# 6. Kurs
async def course(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    try:
        course = int(update.message.text)
        if 1 <= course <= 6:
            USER_DATA[user_id]['course'] = course
            await update.message.reply_text('Yo\'nalishni tanlang (Web, Data Science, AI):')
            return DIRECTION
        else:
            await update.message.reply_text('Iltimos, 1-6 oralig\'ida kursni kiriting.')
    except ValueError:
        await update.message.reply_text('Iltimos, raqam kiriting.')

    return COURSE

# 7. Yo'nalish
async def direction(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    direction = update.message.text
    USER_DATA[user_id]['direction'] = direction
    await update.message.reply_text('Material yuboring (video, rasm, fayl):')
    return MATERIAL

# 8. Material yuborish
async def material(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id

    if update.message.video or update.message.photo or update.message.document:
        material_type = None
        material_file_id = None

        # Material turi va file_id aniqlash
        if update.message.video:
            material_type = 'video'
            material_file_id = update.message.video.file_id
        elif update.message.photo:
            material_type = 'photo'
            material_file_id = update.message.photo[-1].file_id
        elif update.message.document:
            material_type = 'document'
            material_file_id = update.message.document.file_id

        # Ma'lumotlar bazasiga saqlash
        user_data = UserData.objects.create(
            user_id=user_id,
            name=USER_DATA[user_id]['name'],
            surname=USER_DATA[user_id]['surname'],
            faculty=USER_DATA[user_id]['faculty'],
            course=USER_DATA[user_id]['course'],
            direction=USER_DATA[user_id]['direction'],
            phone_number=USER_DATA[user_id].get('contact'),
            material_type=material_type,
            material_file_id=material_file_id
        )

        # Foydalanuvchidan tasdiqlashni so'rash
        update.message.reply_text(
            f"Sizning ma'lumotlaringiz: \n"
            f"Ism: {USER_DATA[user_id]['name']}\n"
            f"Familiya: {USER_DATA[user_id]['surname']}\n"
            f"Fakultet: {USER_DATA[user_id]['faculty']}\n"
            f"Kurs: {USER_DATA[user_id]['course']}\n"
            f"Yo'nalish: {USER_DATA[user_id]['direction']}\n"
        )
        update.message.reply_text('Ma\'lumotlaringiz to\'g\'rimi? Iltimos, tasdiqlang.')
        return CONFIRM
    else:
        update.message.reply_text('Iltimos, video, rasm yoki fayl yuboring.')
    return MATERIAL

# 9. Tasdiqlash
def confirm(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    if update.message.text.lower() in ['ha', 'yes']:
        # Ma'lumotlar to'g'ri bo'lsa, guruhga yuboriladi
        user_data = UserData.objects.get(user_id=user_id)
        
        # Materialni yuborish
        if user_data.material_type == 'video':
            context.bot.send_video(GROUP_ID, video=user_data.material_file_id, caption=str(user_data))
        elif user_data.material_type == 'photo':
            context.bot.send_photo(GROUP_ID, photo=user_data.material_file_id, caption=str(user_data))
        elif user_data.material_type == 'document':
            context.bot.send_document(GROUP_ID, document=user_data.material_file_id, caption=str(user_data))
        
        update.message.reply_text('Ma\'lumotlaringiz guruhga yuborildi.')
        user_data.is_confirmed = True  # Tasdiqlanganligini belgilash
        user_data.save()  # Ma'lumotlarni yangilash
        USER_DATA[user_id] = {}  # Foydalanuvchi ma'lumotlarini tozalash
    else:
        update.message.reply_text('Ma\'lumotlar rad etildi. Iltimos, qayta yuboring.')
        return MATERIAL
    return ConversationHandler.END

# Botni ishga tushurish
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()  # Updater o'rniga Application

    # Foydalanuvchilar bilan muloqot qilish uchun ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CONTACT: [MessageHandler(filters.CONTACT, handle_contact)],
            SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, surname)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            FACULTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, faculty)],
            COURSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, course)],
            DIRECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, direction)],
            MATERIAL: [MessageHandler(filters.TEXT | filters.VIDEO | filters.PHOTO | filters.ALL, material)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.run_polling()  # Updater.start_polling() o'rniga application.run_polling()
    application.idle()  # Updater.idle() o'rniga application.idle()

if __name__ == '__main__':
    main()

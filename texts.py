"""
Internationalization module with translations for Russian, Uzbek, and English.
"""

from typing import Any

TEXTS: dict[str, dict[str, str]] = {
    # Language selection
    "choose_language": {
        "ru": "🌐 Выберите язык / Tilni tanlang / Choose language:",
        "uz": "🌐 Выберите язык / Tilni tanlang / Choose language:",
        "en": "🌐 Выберите язык / Tilni tanlang / Choose language:",
    },
    "language_selected": {
        "ru": "✅ Выбран русский язык.",
        "uz": "✅ O'zbek tili tanlandi.",
        "en": "✅ English language selected.",
    },
    
    # Welcome message
    "welcome": {
        "ru": "🎓 Добро пожаловать в бот регистрации на Олимпиаду!\n\nВы можете зарегистрировать одного или нескольких участников.\n\nДавайте начнём процесс регистрации.",
        "uz": "🎓 Olimpiadaga ro'yxatdan o'tish botiga xush kelibsiz!\n\nSiz bir yoki bir nechta ishtirokchini ro'yxatdan o'tkazishingiz mumkin.\n\nRo'yxatdan o'tish jarayonini boshlaymiz.",
        "en": "🎓 Welcome to the Olympiad Registration Bot!\n\nYou can register one or more participants.\n\nLet's start the registration process.",
    },
    
    # Parent Name
    "ask_parent_name": {
        "ru": "👤 Введите ФИО родителя/опекуна:",
        "uz": "👤 Ota-ona/vasiy FIOsini kiriting:",
        "en": "👤 Enter parent/guardian's full name:",
    },
    "invalid_parent_name": {
        "ru": "❌ ФИО должно содержать только буквы и пробелы. Попробуйте ещё раз:",
        "uz": "❌ FIO faqat harflar va bo'shliqlardan iborat bo'lishi kerak. Qaytadan urinib ko'ring:",
        "en": "❌ Name must contain only letters and spaces. Please try again:",
    },
    
    # Email
    "ask_email": {
        "ru": "📧 Введите ваш Email для связи:",
        "uz": "📧 Aloqa uchun Email manzilingizni kiriting:",
        "en": "📧 Enter your contact Email:",
    },
    "invalid_email": {
        "ru": "❌ Неверный формат Email. Пример: example@mail.com\nПопробуйте ещё раз:",
        "uz": "❌ Email formati noto'g'ri. Misol: example@mail.com\nQaytadan urinib ko'ring:",
        "en": "❌ Invalid Email format. Example: example@mail.com\nPlease try again:",
    },
    
    # Participant Surname
    "ask_surname": {
        "ru": "📝 Введите фамилию участника:",
        "uz": "📝 Ishtirokchi familiyasini kiriting:",
        "en": "📝 Enter participant's surname:",
    },
    "invalid_surname": {
        "ru": "❌ Фамилия должна содержать только буквы. Попробуйте ещё раз:",
        "uz": "❌ Familiya faqat harflardan iborat bo'lishi kerak. Qaytadan urinib ko'ring:",
        "en": "❌ Surname must contain only letters. Please try again:",
    },
    
    # Participant Name
    "ask_name": {
        "ru": "📝 Введите имя участника:",
        "uz": "📝 Ishtirokchi ismini kiriting:",
        "en": "📝 Enter participant's first name:",
    },
    "invalid_name": {
        "ru": "❌ Имя должно содержать только буквы. Попробуйте ещё раз:",
        "uz": "❌ Ism faqat harflardan iborat bo'lishi kerak. Qaytadan urinib ko'ring:",
        "en": "❌ Name must contain only letters. Please try again:",
    },
    
    # Grade (1-8 only)
    "ask_grade": {
        "ru": "🎒 Введите класс участника (1-8):",
        "uz": "🎒 Ishtirokchi sinfini kiriting (1-8):",
        "en": "🎒 Enter participant's grade (1-8):",
    },
    "invalid_grade": {
        "ru": "❌ Класс должен быть числом от 1 до 8. Олимпиада проводится только для 1-8 классов.\nПопробуйте ещё раз:",
        "uz": "❌ Sinf 1 dan 8 gacha bo'lgan raqam bo'lishi kerak. Olimpiada faqat 1-8 sinflar uchun o'tkaziladi.\nQaytadan urinib ko'ring:",
        "en": "❌ Grade must be a number from 1 to 8. The Olympiad is only for grades 1-8.\nPlease try again:",
    },
    
    # School
    "ask_school": {
        "ru": "🏫 Введите название школы участника:",
        "uz": "🏫 Ishtirokchi maktabining nomini kiriting:",
        "en": "🏫 Enter participant's school name:",
    },
    "invalid_school": {
        "ru": "❌ Название школы не может быть пустым. Попробуйте ещё раз:",
        "uz": "❌ Maktab nomi bo'sh bo'lishi mumkin emas. Qaytadan urinib ko'ring:",
        "en": "❌ School name cannot be empty. Please try again:",
    },
    
    # Phone
    "ask_phone": {
        "ru": "📱 Поделитесь вашим номером телефона, нажав кнопку ниже:",
        "uz": "📱 Quyidagi tugmani bosib telefon raqamingizni ulashing:",
        "en": "📱 Share your phone number by pressing the button below:",
    },
    "share_phone_button": {
        "ru": "📞 Поделиться номером",
        "uz": "📞 Raqamni ulashish",
        "en": "📞 Share Phone Number",
    },
    "invalid_phone": {
        "ru": "❌ Пожалуйста, используйте кнопку для отправки номера телефона.",
        "uz": "❌ Iltimos, telefon raqamini yuborish uchun tugmadan foydalaning.",
        "en": "❌ Please use the button to share your phone number.",
    },
    
    # Payment
    "payment_info": {
        "ru": "💳 Для завершения регистрации необходимо оплатить участие в Олимпиаде.\n\n💰 Сумма: {amount} сум\n\n👇 Нажмите кнопку ниже для оплаты через Payme.\n\n⚠️ После оплаты обязательно нажмите \"Я оплатил\" и отправьте скриншот чека.",
        "uz": "💳 Ro'yxatdan o'tishni yakunlash uchun Olimpiada ishtirok haqini to'lashingiz kerak.\n\n💰 Summa: {amount} so'm\n\n👇 Payme orqali to'lash uchun quyidagi tugmani bosing.\n\n⚠️ To'lovdan so'ng \"Men to'ladim\" tugmasini bosing va chek skrinshotini yuboring.",
        "en": "💳 To complete registration, you need to pay the Olympiad participation fee.\n\n💰 Amount: {amount} UZS\n\n👇 Press the button below to pay via Payme.\n\n⚠️ After payment, click \"I have paid\" and send a screenshot of the receipt.",
    },
    "payment_button": {
        "ru": "💸 Оплатить через Payme",
        "uz": "💸 Payme orqali to'lash",
        "en": "💸 Pay via Payme",
    },
    "payment_done_button": {
        "ru": "✅ Я оплатил (прикрепить скриншот)",
        "uz": "✅ Men to'ladim (skrinshot biriktirish)",
        "en": "✅ I have paid (attach screenshot)",
    },
    
    # Screenshot
    "ask_screenshot": {
        "ru": "📸 Отлично! Теперь отправьте скриншот чека об оплате для подтверждения:",
        "uz": "📸 Ajoyib! Endi tasdiqlash uchun to'lov chekining skrinshotini yuboring:",
        "en": "📸 Great! Now send a screenshot of the payment receipt for verification:",
    },
    "invalid_screenshot": {
        "ru": "❌ Пожалуйста, отправьте изображение (скриншот чека).",
        "uz": "❌ Iltimos, rasm yuboring (chek skrinshoti).",
        "en": "❌ Please send an image (screenshot of the receipt).",
    },
    
    # Completion
    "registration_complete": {
        "ru": "🎉 Поздравляем! Регистрация успешно завершена!\n\n📋 Данные участника:\n• Фамилия: {surname}\n• Имя: {name}\n• Класс: {grade}\n• Школа: {school}\n\n👤 Родитель: {parent_name}\n📧 Email: {email}\n📱 Телефон: {phone}\n\n✅ Оплата подтверждена.\n\nУдачи на Олимпиаде! 🏆",
        "uz": "🎉 Tabriklaymiz! Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!\n\n📋 Ishtirokchi ma'lumotlari:\n• Familiya: {surname}\n• Ism: {name}\n• Sinf: {grade}\n• Maktab: {school}\n\n👤 Ota-ona: {parent_name}\n📧 Email: {email}\n📱 Telefon: {phone}\n\n✅ To'lov tasdiqlandi.\n\nOlimpiadada omad! 🏆",
        "en": "🎉 Congratulations! Registration is complete!\n\n📋 Participant details:\n• Surname: {surname}\n• Name: {name}\n• Grade: {grade}\n• School: {school}\n\n👤 Parent: {parent_name}\n📧 Email: {email}\n📱 Phone: {phone}\n\n✅ Payment confirmed.\n\nGood luck at the Olympiad! 🏆",
    },
    
    # Register another child
    "register_another": {
        "ru": "➕ Зарегистрировать ещё одного участника",
        "uz": "➕ Yana bir ishtirokchini ro'yxatdan o'tkazish",
        "en": "➕ Register another participant",
    },
    "register_another_prompt": {
        "ru": "Хотите зарегистрировать ещё одного участника?",
        "uz": "Yana bir ishtirokchini ro'yxatdan o'tkazmoqchimisiz?",
        "en": "Would you like to register another participant?",
    },
    
    # Admin
    "admin_export_success": {
        "ru": "✅ Экспорт данных успешно выполнен.",
        "uz": "✅ Ma'lumotlar eksporti muvaffaqiyatli amalga oshirildi.",
        "en": "✅ Data export completed successfully.",
    },
    "admin_export_empty": {
        "ru": "📭 База данных пуста. Нет зарегистрированных пользователей.",
        "uz": "📭 Ma'lumotlar bazasi bo'sh. Ro'yxatdan o'tgan foydalanuvchilar yo'q.",
        "en": "📭 Database is empty. No registered users.",
    },
    "admin_access_denied": {
        "ru": "🚫 У вас нет доступа к этой команде.",
        "uz": "🚫 Sizda bu buyruqqa kirish huquqi yo'q.",
        "en": "🚫 You don't have access to this command.",
    },
    
    # Errors
    "error_occurred": {
        "ru": "❌ Произошла ошибка. Пожалуйста, попробуйте позже или свяжитесь с администратором.",
        "uz": "❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring yoki administrator bilan bog'laning.",
        "en": "❌ An error occurred. Please try again later or contact the administrator.",
    },
    
    # Cancel
    "cancel": {
        "ru": "❌ Отмена",
        "uz": "❌ Bekor qilish",
        "en": "❌ Cancel",
    },
    "cancelled": {
        "ru": "🚫 Регистрация отменена. Для начала заново введите /start",
        "uz": "🚫 Ro'yxatdan o'tish bekor qilindi. Qayta boshlash uchun /start kiriting",
        "en": "🚫 Registration cancelled. Enter /start to begin again",
    },
    
    # Help
    "help": {
        "ru": "ℹ️ Этот бот предназначен для регистрации на Олимпиаду.\n\n📌 Вы можете зарегистрировать несколько участников с одного аккаунта.\n\nКоманды:\n/start - Начать регистрацию\n/cancel - Отменить регистрацию\n/help - Показать справку",
        "uz": "ℹ️ Bu bot Olimpiadaga ro'yxatdan o'tish uchun mo'ljallangan.\n\n📌 Bitta akkauntdan bir nechta ishtirokchini ro'yxatdan o'tkazishingiz mumkin.\n\nBuyruqlar:\n/start - Ro'yxatdan o'tishni boshlash\n/cancel - Ro'yxatdan o'tishni bekor qilish\n/help - Yordam ko'rsatish",
        "en": "ℹ️ This bot is designed for Olympiad registration.\n\n📌 You can register multiple participants from one account.\n\nCommands:\n/start - Start registration\n/cancel - Cancel registration\n/help - Show help",
    },
    
    # My ID (for admin setup)
    "your_id": {
        "ru": "🆔 Ваш Telegram ID: `{user_id}`",
        "uz": "🆔 Sizning Telegram ID: `{user_id}`",
        "en": "🆔 Your Telegram ID: `{user_id}`",
    },
}

# Language button labels
LANGUAGE_BUTTONS = {
    "ru": "🇷🇺 Русский",
    "uz": "🇺🇿 O'zbekcha",
    "en": "🇬🇧 English",
}


def get_text(key: str, lang: str, **kwargs: Any) -> str:
    """
    Get translated text by key and language.
    
    Args:
        key: Text key from TEXTS dictionary
        lang: Language code ('ru', 'uz', 'en')
        **kwargs: Format arguments for the text
        
    Returns:
        Translated and formatted text, or key if not found
    """
    text_dict = TEXTS.get(key, {})
    text = text_dict.get(lang, text_dict.get("en", key))
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text

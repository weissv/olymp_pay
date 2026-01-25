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
        "ru": "🎓 Добро пожаловать в бот регистрации на Олимпиаду!\n\nДавайте начнём процесс регистрации.",
        "uz": "🎓 Olimpiadaga ro'yxatdan o'tish botiga xush kelibsiz!\n\nRo'yxatdan o'tish jarayonini boshlaymiz.",
        "en": "🎓 Welcome to the Olympiad Registration Bot!\n\nLet's start the registration process.",
    },
    
    # Already registered
    "already_registered": {
        "ru": "⚠️ Вы уже зарегистрированы на Олимпиаду!\n\nЕсли у вас есть вопросы, обратитесь к администратору.",
        "uz": "⚠️ Siz allaqachon Olimpiadaga ro'yxatdan o'tgansiz!\n\nSavollaringiz bo'lsa, administratorga murojaat qiling.",
        "en": "⚠️ You are already registered for the Olympiad!\n\nIf you have any questions, please contact the administrator.",
    },
    
    # Surname
    "ask_surname": {
        "ru": "📝 Введите вашу фамилию:",
        "uz": "📝 Familiyangizni kiriting:",
        "en": "📝 Enter your surname:",
    },
    "invalid_surname": {
        "ru": "❌ Фамилия должна содержать только буквы. Попробуйте ещё раз:",
        "uz": "❌ Familiya faqat harflardan iborat bo'lishi kerak. Qaytadan urinib ko'ring:",
        "en": "❌ Surname must contain only letters. Please try again:",
    },
    
    # Name
    "ask_name": {
        "ru": "📝 Введите ваше имя:",
        "uz": "📝 Ismingizni kiriting:",
        "en": "📝 Enter your first name:",
    },
    "invalid_name": {
        "ru": "❌ Имя должно содержать только буквы. Попробуйте ещё раз:",
        "uz": "❌ Ism faqat harflardan iborat bo'lishi kerak. Qaytadan urinib ko'ring:",
        "en": "❌ Name must contain only letters. Please try again:",
    },
    
    # Grade
    "ask_grade": {
        "ru": "🎒 Введите ваш класс (1-11):",
        "uz": "🎒 Sinfingizni kiriting (1-11):",
        "en": "🎒 Enter your grade (1-11):",
    },
    "invalid_grade": {
        "ru": "❌ Класс должен быть числом от 1 до 11. Попробуйте ещё раз:",
        "uz": "❌ Sinf 1 dan 11 gacha bo'lgan raqam bo'lishi kerak. Qaytadan urinib ko'ring:",
        "en": "❌ Grade must be a number from 1 to 11. Please try again:",
    },
    
    # School
    "ask_school": {
        "ru": "🏫 Введите название вашей школы:",
        "uz": "🏫 Maktabingiz nomini kiriting:",
        "en": "🏫 Enter your school name:",
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
        "ru": "💳 Для завершения регистрации необходимо оплатить участие в Олимпиаде.\n\nНажмите кнопку ниже для оплаты через Payme.",
        "uz": "💳 Ro'yxatdan o'tishni yakunlash uchun Olimpiada ishtirok haqini to'lashingiz kerak.\n\nPayme orqali to'lash uchun quyidagi tugmani bosing.",
        "en": "💳 To complete registration, you need to pay the Olympiad participation fee.\n\nPress the button below to pay via Payme.",
    },
    "payment_title": {
        "ru": "Регистрация на Олимпиаду",
        "uz": "Olimpiadaga ro'yxatdan o'tish",
        "en": "Olympiad Registration",
    },
    "payment_description": {
        "ru": "Оплата участия в Олимпиаде",
        "uz": "Olimpiada ishtirok haqini to'lash",
        "en": "Olympiad Participation Fee Payment",
    },
    "payment_success": {
        "ru": "✅ Оплата успешно получена! Спасибо!",
        "uz": "✅ To'lov muvaffaqiyatli qabul qilindi! Rahmat!",
        "en": "✅ Payment successfully received! Thank you!",
    },
    "payment_failed": {
        "ru": "❌ Оплата не прошла. Пожалуйста, попробуйте ещё раз.",
        "uz": "❌ To'lov amalga oshmadi. Iltimos, qaytadan urinib ko'ring.",
        "en": "❌ Payment failed. Please try again.",
    },
    
    # Screenshot
    "ask_screenshot": {
        "ru": "📸 Теперь отправьте скриншот чека об оплате для подтверждения:",
        "uz": "📸 Endi tasdiqlash uchun to'lov chekining skrinshotini yuboring:",
        "en": "📸 Now send a screenshot of the payment receipt for verification:",
    },
    "invalid_screenshot": {
        "ru": "❌ Пожалуйста, отправьте изображение (скриншот чека).",
        "uz": "❌ Iltimos, rasm yuboring (chek skrinshoti).",
        "en": "❌ Please send an image (screenshot of the receipt).",
    },
    
    # Completion
    "registration_complete": {
        "ru": "🎉 Поздравляем! Ваша регистрация успешно завершена!\n\n📋 Ваши данные:\n• Фамилия: {surname}\n• Имя: {name}\n• Класс: {grade}\n• Школа: {school}\n• Телефон: {phone}\n\n✅ Оплата подтверждена.\n\nУдачи на Олимпиаде! 🏆",
        "uz": "🎉 Tabriklaymiz! Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!\n\n📋 Sizning ma'lumotlaringiz:\n• Familiya: {surname}\n• Ism: {name}\n• Sinf: {grade}\n• Maktab: {school}\n• Telefon: {phone}\n\n✅ To'lov tasdiqlandi.\n\nOlimpiadada omad! 🏆",
        "en": "🎉 Congratulations! Your registration is complete!\n\n📋 Your details:\n• Surname: {surname}\n• Name: {name}\n• Grade: {grade}\n• School: {school}\n• Phone: {phone}\n\n✅ Payment confirmed.\n\nGood luck at the Olympiad! 🏆",
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
        "ru": "ℹ️ Этот бот предназначен для регистрации на Олимпиаду.\n\nКоманды:\n/start - Начать регистрацию\n/cancel - Отменить регистрацию\n/help - Показать справку",
        "uz": "ℹ️ Bu bot Olimpiadaga ro'yxatdan o'tish uchun mo'ljallangan.\n\nBuyruqlar:\n/start - Ro'yxatdan o'tishni boshlash\n/cancel - Ro'yxatdan o'tishni bekor qilish\n/help - Yordam ko'rsatish",
        "en": "ℹ️ This bot is designed for Olympiad registration.\n\nCommands:\n/start - Start registration\n/cancel - Cancel registration\n/help - Show help",
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

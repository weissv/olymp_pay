"""
Handlers module with FSM logic for the Olympiad Registration Bot.
Refactored to support:
- Multiple registrations per Telegram account
- Parent name and email fields
- Payme checkout with fixed amount
- Grades 1-8 only
"""

import base64
import io
import logging
import re
from datetime import datetime

import pandas as pd
from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import ADMIN_IDS, MAX_GRADE, MIN_GRADE, OLYMPIAD_PRICE, PAYME_MERCHANT_ID
from db import DatabaseManager, LanguageEnum, engine
from texts import LANGUAGE_BUTTONS, get_text

logger = logging.getLogger(__name__)

# Create router
router = Router()


class RegState(StatesGroup):
    """Registration states for FSM."""
    LanguageSelect = State()
    ParentName = State()      # NEW: Parent/Guardian name
    Email = State()           # NEW: Contact email
    Surname = State()         # Participant's surname
    Name = State()            # Participant's name
    Grade = State()           # Grades 1-8 only
    School = State()
    Phone = State()
    Payment = State()         # Show Payme link
    ScreenshotProof = State()


# ==================== Helper Functions ====================

def create_language_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard for language selection."""
    buttons = [
        [InlineKeyboardButton(text=label, callback_data=f"lang_{code}")]
        for code, label in LANGUAGE_BUTTONS.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_phone_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Create reply keyboard for phone number sharing."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text("share_phone_button", lang), request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def create_cancel_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Create reply keyboard with cancel button."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=get_text("cancel", lang))]],
        resize_keyboard=True,
    )


def create_payment_keyboard(lang: str, payme_url: str) -> InlineKeyboardMarkup:
    """Create inline keyboard with Payme link and 'I paid' button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("payment_button", lang), url=payme_url)],
            [InlineKeyboardButton(text=get_text("payment_done_button", lang), callback_data="payment_done")],
        ]
    )


def create_register_another_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Create reply keyboard with 'Register another' button."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=get_text("register_another", lang))]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def validate_name(text: str) -> bool:
    """Validate that text contains only letters, spaces, hyphens, and apostrophes."""
    return bool(re.match(r'^[a-zA-Zа-яА-ЯёЁўЎқҚғҒҳҲ\s\-\']+$', text.strip()))


def validate_email(email: str) -> bool:
    """Validate email format (basic validation)."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_grade(text: str) -> tuple[bool, int]:
    """Validate that grade is a number within range 1-8."""
    try:
        grade = int(text.strip())
        if MIN_GRADE <= grade <= MAX_GRADE:
            return True, grade
        return False, 0
    except ValueError:
        return False, 0


def generate_payme_link(
    merchant_id: str,
    amount: int,
    charge_id: str,
) -> str:
    """
    Generate Payme checkout URL with base64-encoded parameters.
    
    Args:
        merchant_id: Payme Merchant ID (from Payme Business dashboard)
        amount: Amount in tiyins (fixed)
        charge_id: Charge ID from database (format: {db_id}_{Surname}_{Name}_{Grade})
        
    Returns:
        Payme checkout URL with fixed amount
    """
    # Build parameters for Payme checkout
    # Format: m=MERCHANT_ID;ac.charge_id=CHARGE_ID;a=AMOUNT;l=ru
    params = f"m={merchant_id};ac.charge_id={charge_id};a={amount};l=ru"
    
    # Encode to base64
    encoded = base64.b64encode(params.encode('utf-8')).decode('utf-8')
    
    # Build checkout URL
    payme_url = f"https://checkout.paycom.uz/{encoded}"
    
    logger.info(f"Generated Payme URL with charge_id={charge_id}, amount={amount}")
    
    return payme_url


def is_cancel_text(text: str) -> bool:
    """Check if text is a cancel command."""
    cancel_texts = [get_text("cancel", "ru"), get_text("cancel", "uz"), get_text("cancel", "en")]
    return text.strip() in cancel_texts


# ==================== Command Handlers ====================

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Handle /start command - begin registration."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    
    logger.info(f"[{user_id}] [{username}] - Started registration (/start)")
    
    # Clear any existing state and start fresh
    await state.clear()
    
    # Show language selection (allow multiple registrations, so no check for existing user)
    await message.answer(
        get_text("choose_language", "en"),
        reply_markup=create_language_keyboard(),
    )
    await state.set_state(RegState.LanguageSelect)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    """Handle /cancel command."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    
    logger.info(f"[{user_id}] [{username}] - Cancelled registration")
    
    data = await state.get_data()
    lang = data.get("language", "en")
    
    await state.clear()
    await message.answer(
        get_text("cancelled", lang),
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext) -> None:
    """Handle /help command."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    
    logger.info(f"[{user_id}] [{username}] - Requested help (/help)")
    
    data = await state.get_data()
    lang = data.get("language", "en")
    
    await message.answer(get_text("help", lang))


@router.message(Command("myid"))
async def cmd_myid(message: Message, state: FSMContext) -> None:
    """Handle /myid command - show user's Telegram ID."""
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data.get("language", "en")
    
    await message.answer(
        get_text("your_id", lang, user_id=user_id),
        parse_mode="Markdown"
    )


@router.message(Command("export"))
async def cmd_export(message: Message) -> None:
    """Handle /export command - admin only."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    
    logger.info(f"[{user_id}] [{username}] - Attempted export command")
    
    if user_id not in ADMIN_IDS:
        logger.warning(f"[{user_id}] [{username}] - Access denied for /export")
        await message.answer(get_text("admin_access_denied", "en"))
        return
    
    logger.info(f"[{user_id}] [{username}] - Admin export started")
    
    try:
        async with engine.connect() as conn:
            df = await conn.run_sync(
                lambda sync_conn: pd.read_sql("SELECT * FROM users", sync_conn)
            )
        
        if df.empty:
            await message.answer(get_text("admin_export_empty", "en"))
            return
        
        # Convert timezone-aware datetime to timezone-naive for Excel compatibility
        if 'created_at' in df.columns:
            df['created_at'] = df['created_at'].dt.tz_localize(None)
        
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Registrations')
        excel_buffer.seek(0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"olympiad_registrations_{timestamp}.xlsx"
        
        document = BufferedInputFile(
            file=excel_buffer.read(),
            filename=filename,
        )
        
        await message.answer_document(
            document=document,
            caption=get_text("admin_export_success", "en"),
        )
        
        logger.info(f"[{user_id}] [{username}] - Export successful, {len(df)} records")
        
    except Exception as e:
        logger.error(f"[{user_id}] [{username}] - Export error: {e}")
        await message.answer(get_text("error_occurred", "en"))


@router.message(Command("view"))
async def cmd_view(message: Message) -> None:
    """Handle /view command - admin only. View registration by ID with screenshot."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    
    if user_id not in ADMIN_IDS:
        logger.warning(f"[{user_id}] [{username}] - Access denied for /view")
        await message.answer(get_text("admin_access_denied", "en"))
        return
    
    # Parse registration ID from command
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("📋 Использование: /view {ID}\n\nПример: /view 4")
            return
        
        registration_id = int(parts[1])
    except ValueError:
        await message.answer("❌ ID должен быть числом. Пример: /view 4")
        return
    
    logger.info(f"[{user_id}] [{username}] - Viewing registration ID: {registration_id}")
    
    try:
        user = await DatabaseManager.get_registration_by_id(registration_id)
        
        if not user:
            await message.answer(f"❌ Регистрация с ID {registration_id} не найдена.")
            return
        
        # Format registration info
        info = f"""
📋 **Регистрация #{user.id}**

👤 **Родитель:** {user.parent_name}
📧 **Email:** {user.email}
📱 **Телефон:** {user.phone}

👨‍🎓 **Участник:**
• Фамилия: {user.surname}
• Имя: {user.name}
• Класс: {user.grade}
• Школа: {user.school}

🔖 **Charge ID:** `{user.charge_id or 'N/A'}`
💳 **Статус оплаты:** {'✅ Оплачено' if user.payment_status else '❌ Не оплачено'}
📅 **Дата регистрации:** {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}

🆔 **Telegram ID:** {user.telegram_id}
👤 **Username:** @{user.username or 'N/A'}
"""
        
        # Send info message
        await message.answer(info, parse_mode="Markdown")
        
        # Send screenshot if exists
        if user.screenshot_file_id:
            await message.answer_photo(
                photo=user.screenshot_file_id,
                caption=f"📸 Скриншот оплаты для регистрации #{user.id}"
            )
        else:
            await message.answer("⚠️ Скриншот не загружен.")
        
        logger.info(f"[{user_id}] [{username}] - Viewed registration #{registration_id}")
        
    except Exception as e:
        logger.error(f"[{user_id}] [{username}] - View error: {e}")
        await message.answer(get_text("error_occurred", "en"))
        await message.answer(get_text("error_occurred", "en"))


# ==================== Language Selection Handler ====================

@router.callback_query(StateFilter(RegState.LanguageSelect), F.data.startswith("lang_"))
async def process_language_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Process language selection callback."""
    user_id = callback.from_user.id
    username = callback.from_user.username or "N/A"
    
    lang_code = callback.data.replace("lang_", "")
    
    logger.info(f"[{user_id}] [{username}] - Selected language: {lang_code}")
    
    if lang_code not in ["ru", "uz", "en"]:
        lang_code = "en"
    
    await state.update_data(language=lang_code)
    await callback.answer()
    
    await callback.message.edit_text(get_text("language_selected", lang_code))
    await callback.message.answer(get_text("welcome", lang_code))
    
    # Ask for parent name first
    await callback.message.answer(
        get_text("ask_parent_name", lang_code),
        reply_markup=create_cancel_keyboard(lang_code),
    )
    await state.set_state(RegState.ParentName)


# ==================== Parent Name Handler ====================

@router.message(StateFilter(RegState.ParentName), F.text)
async def process_parent_name(message: Message, state: FSMContext) -> None:
    """Process parent name input."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    parent_name = message.text.strip()
    
    if is_cancel_text(parent_name):
        return await cmd_cancel(message, state)
    
    logger.info(f"[{user_id}] [{username}] - Entered parent name: {parent_name}")
    
    if not validate_name(parent_name) or len(parent_name) < 2:
        logger.warning(f"[{user_id}] [{username}] - Invalid parent name: {parent_name}")
        await message.answer(get_text("invalid_parent_name", lang))
        return
    
    await state.update_data(parent_name=parent_name)
    await message.answer(
        get_text("ask_email", lang),
        reply_markup=create_cancel_keyboard(lang),
    )
    await state.set_state(RegState.Email)


# ==================== Email Handler ====================

@router.message(StateFilter(RegState.Email), F.text)
async def process_email(message: Message, state: FSMContext) -> None:
    """Process email input."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    email = message.text.strip()
    
    if is_cancel_text(email):
        return await cmd_cancel(message, state)
    
    logger.info(f"[{user_id}] [{username}] - Entered email: {email}")
    
    if not validate_email(email):
        logger.warning(f"[{user_id}] [{username}] - Invalid email: {email}")
        await message.answer(get_text("invalid_email", lang))
        return
    
    await state.update_data(email=email)
    await message.answer(
        get_text("ask_surname", lang),
        reply_markup=create_cancel_keyboard(lang),
    )
    await state.set_state(RegState.Surname)


# ==================== Surname Handler ====================

@router.message(StateFilter(RegState.Surname), F.text)
async def process_surname(message: Message, state: FSMContext) -> None:
    """Process participant's surname input."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    surname = message.text.strip()
    
    if is_cancel_text(surname):
        return await cmd_cancel(message, state)
    
    logger.info(f"[{user_id}] [{username}] - Entered surname: {surname}")
    
    if not validate_name(surname) or len(surname) < 2:
        logger.warning(f"[{user_id}] [{username}] - Invalid surname: {surname}")
        await message.answer(get_text("invalid_surname", lang))
        return
    
    await state.update_data(surname=surname)
    await message.answer(
        get_text("ask_name", lang),
        reply_markup=create_cancel_keyboard(lang),
    )
    await state.set_state(RegState.Name)


# ==================== Name Handler ====================

@router.message(StateFilter(RegState.Name), F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    """Process participant's name input."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    name = message.text.strip()
    
    if is_cancel_text(name):
        return await cmd_cancel(message, state)
    
    logger.info(f"[{user_id}] [{username}] - Entered name: {name}")
    
    if not validate_name(name) or len(name) < 2:
        logger.warning(f"[{user_id}] [{username}] - Invalid name: {name}")
        await message.answer(get_text("invalid_name", lang))
        return
    
    await state.update_data(name=name)
    await message.answer(
        get_text("ask_grade", lang),
        reply_markup=create_cancel_keyboard(lang),
    )
    await state.set_state(RegState.Grade)


# ==================== Grade Handler ====================

@router.message(StateFilter(RegState.Grade), F.text)
async def process_grade(message: Message, state: FSMContext) -> None:
    """Process grade input (1-8 only)."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    grade_text = message.text.strip()
    
    if is_cancel_text(grade_text):
        return await cmd_cancel(message, state)
    
    logger.info(f"[{user_id}] [{username}] - Entered grade: {grade_text}")
    
    is_valid, grade = validate_grade(grade_text)
    if not is_valid:
        logger.warning(f"[{user_id}] [{username}] - Invalid grade: {grade_text}")
        await message.answer(get_text("invalid_grade", lang))
        return
    
    await state.update_data(grade=grade)
    await message.answer(
        get_text("ask_school", lang),
        reply_markup=create_cancel_keyboard(lang),
    )
    await state.set_state(RegState.School)


# ==================== School Handler ====================

@router.message(StateFilter(RegState.School), F.text)
async def process_school(message: Message, state: FSMContext) -> None:
    """Process school input."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    school = message.text.strip()
    
    if is_cancel_text(school):
        return await cmd_cancel(message, state)
    
    logger.info(f"[{user_id}] [{username}] - Entered school: {school}")
    
    if not school or len(school) < 2:
        logger.warning(f"[{user_id}] [{username}] - Invalid school: {school}")
        await message.answer(get_text("invalid_school", lang))
        return
    
    await state.update_data(school=school)
    await message.answer(
        get_text("ask_phone", lang),
        reply_markup=create_phone_keyboard(lang),
    )
    await state.set_state(RegState.Phone)


# ==================== Phone Handler ====================

@router.message(StateFilter(RegState.Phone), F.contact)
async def process_phone_contact(message: Message, state: FSMContext) -> None:
    """Process phone contact."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    phone = message.contact.phone_number
    
    logger.info(f"[{user_id}] [{username}] - Shared phone: {phone}")
    
    await state.update_data(phone=phone)
    
    try:
        # Create registration in database FIRST to get order_id
        # payment_status=False until screenshot is received
        user = await DatabaseManager.create_user(
            telegram_id=user_id,
            username=username if username != "N/A" else None,
            parent_name=data["parent_name"],
            email=data["email"],
            phone=phone,
            surname=data["surname"],
            name=data["name"],
            grade=data["grade"],
            school=data["school"],
            language=LanguageEnum(lang),
            payment_status=False,  # Will be updated after screenshot
            screenshot_file_id=None,
        )
        
        logger.info(f"[{user_id}] [{username}] - Created DB record ID: {user.id}, charge_id: {user.charge_id}")
        
        # Store registration ID for later update
        await state.update_data(registration_id=user.id, charge_id=user.charge_id)
        
        # Generate Payme link with charge_id from database
        payme_url = generate_payme_link(
            merchant_id=PAYME_MERCHANT_ID,
            amount=OLYMPIAD_PRICE,
            charge_id=user.charge_id,
        )
        
        # Format amount for display (tiyins to sum)
        amount_display = OLYMPIAD_PRICE // 100
        
        await message.answer(
            get_text("payment_info", lang, amount=amount_display),
            reply_markup=create_payment_keyboard(lang, payme_url),
        )
        
        await state.set_state(RegState.Payment)
        
    except Exception as e:
        logger.error(f"[{user_id}] [{username}] - Database error creating record: {e}")
        await message.answer(get_text("error_occurred", lang))


@router.message(StateFilter(RegState.Phone), F.text)
async def process_phone_text(message: Message, state: FSMContext) -> None:
    """Handle text input when expecting phone contact."""
    data = await state.get_data()
    lang = data.get("language", "en")
    
    if is_cancel_text(message.text.strip()):
        return await cmd_cancel(message, state)
    
    await message.answer(
        get_text("invalid_phone", lang),
        reply_markup=create_phone_keyboard(lang),
    )


# ==================== Payment Handler ====================

@router.callback_query(StateFilter(RegState.Payment), F.data == "payment_done")
async def process_payment_done(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle 'I have paid' button click."""
    user_id = callback.from_user.id
    username = callback.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    logger.info(f"[{user_id}] [{username}] - Clicked 'I have paid'")
    
    await callback.answer()
    await callback.message.answer(
        get_text("ask_screenshot", lang),
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(RegState.ScreenshotProof)


# ==================== Screenshot Handler ====================

@router.message(StateFilter(RegState.ScreenshotProof), F.photo)
async def process_screenshot(message: Message, state: FSMContext) -> None:
    """Process screenshot upload and complete registration."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    photo = message.photo[-1]
    file_id = photo.file_id
    
    logger.info(f"[{user_id}] [{username}] - Uploaded screenshot: {file_id}")
    
    try:
        # Get registration ID from state
        registration_id = data.get("registration_id")
        charge_id = data.get("charge_id")
        
        if registration_id:
            # Update existing registration with payment status
            user = await DatabaseManager.update_registration_payment(
                registration_id=registration_id,
                payment_status=True,
                screenshot_file_id=file_id,
            )
            logger.info(f"[{user_id}] [{username}] - Updated registration ID: {registration_id}, charge_id: {charge_id}")
        else:
            # Fallback: create new registration (shouldn't happen normally)
            logger.warning(f"[{user_id}] [{username}] - No registration_id in state, creating new record")
            user = await DatabaseManager.create_user(
                telegram_id=user_id,
                username=username if username != "N/A" else None,
                parent_name=data["parent_name"],
                email=data["email"],
                phone=data["phone"],
                surname=data["surname"],
                name=data["name"],
                grade=data["grade"],
                school=data["school"],
                language=LanguageEnum(lang),
                payment_status=True,
                screenshot_file_id=file_id,
            )
        
        logger.info(f"[{user_id}] [{username}] - Registration completed, DB ID: {user.id}, charge_id: {user.charge_id}")
        
        # Send completion message with charge_id
        await message.answer(
            get_text(
                "registration_complete",
                lang,
                surname=data["surname"],
                name=data["name"],
                grade=data["grade"],
                school=data["school"],
                parent_name=data["parent_name"],
                email=data["email"],
                phone=data["phone"],
                charge_id=user.charge_id,
            ),
            parse_mode="Markdown",
        )
        
        # Show "Register another" button
        await message.answer(
            get_text("register_another_prompt", lang),
            reply_markup=create_register_another_keyboard(lang),
        )
        
        # Clear state but keep language for convenience
        await state.clear()
        await state.update_data(language=lang)
        
    except Exception as e:
        logger.error(f"[{user_id}] [{username}] - Database error: {e}")
        await message.answer(get_text("error_occurred", lang))


@router.message(StateFilter(RegState.ScreenshotProof), ~F.photo)
async def process_invalid_screenshot(message: Message, state: FSMContext) -> None:
    """Handle non-photo input when expecting screenshot."""
    data = await state.get_data()
    lang = data.get("language", "en")
    
    logger.warning(f"[{message.from_user.id}] - Invalid screenshot input")
    
    await message.answer(get_text("invalid_screenshot", lang))


# ==================== Register Another Handler ====================

@router.message(F.text.in_([
    get_text("register_another", "ru"),
    get_text("register_another", "uz"),
    get_text("register_another", "en"),
]))
async def process_register_another(message: Message, state: FSMContext) -> None:
    """Handle 'Register another' button click."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    logger.info(f"[{user_id}] [{username}] - Starting another registration")
    
    # Clear state and restart
    await state.clear()
    await state.update_data(language=lang)
    
    # Skip language selection, go directly to parent name
    await message.answer(get_text("welcome", lang))
    await message.answer(
        get_text("ask_parent_name", lang),
        reply_markup=create_cancel_keyboard(lang),
    )
    await state.set_state(RegState.ParentName)


# ==================== Fallback Handler ====================

@router.message()
async def handle_unknown(message: Message, state: FSMContext) -> None:
    """Handle unknown messages."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    
    logger.info(f"[{user_id}] [{username}] - Unknown message: {message.text or message.content_type}")
    
    current_state = await state.get_state()
    
    if current_state is None:
        data = await state.get_data()
        lang = data.get("language", "en")
        await message.answer(get_text("help", lang))

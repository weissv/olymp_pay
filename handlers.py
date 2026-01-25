"""
Handlers module with FSM logic for the Olympiad Registration Bot.
"""

import io
import logging
import re
from datetime import datetime

import pandas as pd
from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    ContentType,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import ADMIN_IDS, MAX_GRADE, MIN_GRADE, OLYMPIAD_CURRENCY, OLYMPIAD_PRICE, PAYMENT_PROVIDER_TOKEN
from db import DatabaseManager, LanguageEnum, User, engine
from texts import LANGUAGE_BUTTONS, get_text

logger = logging.getLogger(__name__)

# Create router
router = Router()


class RegState(StatesGroup):
    """Registration states for FSM."""
    LanguageSelect = State()
    Surname = State()
    Name = State()
    Grade = State()
    School = State()
    Phone = State()
    Payment = State()
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


def validate_name(text: str) -> bool:
    """Validate that text contains only letters and spaces."""
    # Allow letters from various alphabets (Latin, Cyrillic, etc.) and spaces
    pattern = r'^[\p{L}\s\-\']+$'
    # Simplified pattern for common cases
    return bool(re.match(r'^[a-zA-Zа-яА-ЯёЁўЎқҚғҒҳҲ\s\-\']+$', text.strip()))


def validate_grade(text: str) -> tuple[bool, int]:
    """Validate that grade is a number within range."""
    try:
        grade = int(text.strip())
        if MIN_GRADE <= grade <= MAX_GRADE:
            return True, grade
        return False, 0
    except ValueError:
        return False, 0


# ==================== Command Handlers ====================

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Handle /start command - begin registration."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    
    logger.info(f"[{user_id}] [{username}] - Started registration (/start)")
    
    # Check if user already registered
    if await DatabaseManager.user_exists(user_id):
        # Get user's language preference
        user = await DatabaseManager.get_user_by_telegram_id(user_id)
        lang = user.language.value if user else "en"
        await message.answer(get_text("already_registered", lang))
        await state.clear()
        return
    
    # Clear any existing state and start fresh
    await state.clear()
    
    # Show language selection
    await message.answer(
        get_text("choose_language", "en"),
        reply_markup=create_language_keyboard(),
    )
    await state.set_state(RegState.LanguageSelect)


@router.message(Command("cancel"))
@router.message(F.text.in_([get_text("cancel", "ru"), get_text("cancel", "uz"), get_text("cancel", "en")]))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    """Handle /cancel command or cancel button."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    
    logger.info(f"[{user_id}] [{username}] - Cancelled registration")
    
    # Get user's language from state data
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
    
    # Get user's language from state data or default
    data = await state.get_data()
    lang = data.get("language", "en")
    
    await message.answer(get_text("help", lang))


@router.message(Command("export"))
async def cmd_export(message: Message) -> None:
    """Handle /export command - admin only."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    
    logger.info(f"[{user_id}] [{username}] - Attempted export command")
    
    # Check admin access
    if user_id not in ADMIN_IDS:
        logger.warning(f"[{user_id}] [{username}] - Access denied for /export")
        await message.answer(get_text("admin_access_denied", "en"))
        return
    
    logger.info(f"[{user_id}] [{username}] - Admin export started")
    
    try:
        # Fetch all users using Pandas
        async with engine.connect() as conn:
            df = await conn.run_sync(
                lambda sync_conn: pd.read_sql("SELECT * FROM users", sync_conn)
            )
        
        if df.empty:
            await message.answer(get_text("admin_export_empty", "en"))
            return
        
        # Generate Excel file
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Registrations')
        excel_buffer.seek(0)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"olympiad_registrations_{timestamp}.xlsx"
        
        # Send file
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


# ==================== Language Selection Handler ====================

@router.callback_query(StateFilter(RegState.LanguageSelect), F.data.startswith("lang_"))
async def process_language_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Process language selection callback."""
    user_id = callback.from_user.id
    username = callback.from_user.username or "N/A"
    
    lang_code = callback.data.replace("lang_", "")
    
    logger.info(f"[{user_id}] [{username}] - Selected language: {lang_code}")
    
    # Validate language code
    if lang_code not in ["ru", "uz", "en"]:
        lang_code = "en"
    
    # Save language to state
    await state.update_data(language=lang_code)
    
    # Acknowledge callback
    await callback.answer()
    
    # Send confirmation and welcome
    await callback.message.edit_text(get_text("language_selected", lang_code))
    await callback.message.answer(get_text("welcome", lang_code))
    
    # Ask for surname
    await callback.message.answer(
        get_text("ask_surname", lang_code),
        reply_markup=create_cancel_keyboard(lang_code),
    )
    await state.set_state(RegState.Surname)


# ==================== Surname Handler ====================

@router.message(StateFilter(RegState.Surname), F.text)
async def process_surname(message: Message, state: FSMContext) -> None:
    """Process surname input."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    surname = message.text.strip()
    
    # Check for cancel
    if surname in [get_text("cancel", "ru"), get_text("cancel", "uz"), get_text("cancel", "en")]:
        return await cmd_cancel(message, state)
    
    logger.info(f"[{user_id}] [{username}] - Entered surname: {surname}")
    
    # Validate surname
    if not validate_name(surname) or len(surname) < 2:
        logger.warning(f"[{user_id}] [{username}] - Invalid surname: {surname}")
        await message.answer(get_text("invalid_surname", lang))
        return
    
    # Save surname and ask for name
    await state.update_data(surname=surname)
    await message.answer(
        get_text("ask_name", lang),
        reply_markup=create_cancel_keyboard(lang),
    )
    await state.set_state(RegState.Name)


# ==================== Name Handler ====================

@router.message(StateFilter(RegState.Name), F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    """Process name input."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    name = message.text.strip()
    
    # Check for cancel
    if name in [get_text("cancel", "ru"), get_text("cancel", "uz"), get_text("cancel", "en")]:
        return await cmd_cancel(message, state)
    
    logger.info(f"[{user_id}] [{username}] - Entered name: {name}")
    
    # Validate name
    if not validate_name(name) or len(name) < 2:
        logger.warning(f"[{user_id}] [{username}] - Invalid name: {name}")
        await message.answer(get_text("invalid_name", lang))
        return
    
    # Save name and ask for grade
    await state.update_data(name=name)
    await message.answer(
        get_text("ask_grade", lang),
        reply_markup=create_cancel_keyboard(lang),
    )
    await state.set_state(RegState.Grade)


# ==================== Grade Handler ====================

@router.message(StateFilter(RegState.Grade), F.text)
async def process_grade(message: Message, state: FSMContext) -> None:
    """Process grade input."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    grade_text = message.text.strip()
    
    # Check for cancel
    if grade_text in [get_text("cancel", "ru"), get_text("cancel", "uz"), get_text("cancel", "en")]:
        return await cmd_cancel(message, state)
    
    logger.info(f"[{user_id}] [{username}] - Entered grade: {grade_text}")
    
    # Validate grade
    is_valid, grade = validate_grade(grade_text)
    if not is_valid:
        logger.warning(f"[{user_id}] [{username}] - Invalid grade: {grade_text}")
        await message.answer(get_text("invalid_grade", lang))
        return
    
    # Save grade and ask for school
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
    
    # Check for cancel
    if school in [get_text("cancel", "ru"), get_text("cancel", "uz"), get_text("cancel", "en")]:
        return await cmd_cancel(message, state)
    
    logger.info(f"[{user_id}] [{username}] - Entered school: {school}")
    
    # Validate school
    if not school or len(school) < 2:
        logger.warning(f"[{user_id}] [{username}] - Invalid school: {school}")
        await message.answer(get_text("invalid_school", lang))
        return
    
    # Save school and ask for phone
    await state.update_data(school=school)
    await message.answer(
        get_text("ask_phone", lang),
        reply_markup=create_phone_keyboard(lang),
    )
    await state.set_state(RegState.Phone)


# ==================== Phone Handler ====================

@router.message(StateFilter(RegState.Phone), F.contact)
async def process_phone_contact(message: Message, state: FSMContext, bot: Bot) -> None:
    """Process phone contact."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    phone = message.contact.phone_number
    
    logger.info(f"[{user_id}] [{username}] - Shared phone: {phone}")
    
    # Save phone
    await state.update_data(phone=phone)
    
    # Remove keyboard and send payment info
    await message.answer(
        get_text("payment_info", lang),
        reply_markup=ReplyKeyboardRemove(),
    )
    
    # Send invoice
    await bot.send_invoice(
        chat_id=message.chat.id,
        title=get_text("payment_title", lang),
        description=get_text("payment_description", lang),
        payload=f"olympiad_registration_{user_id}",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency=OLYMPIAD_CURRENCY,
        prices=[
            LabeledPrice(label=get_text("payment_title", lang), amount=OLYMPIAD_PRICE)
        ],
        start_parameter="olympiad-registration",
    )
    
    await state.set_state(RegState.Payment)


@router.message(StateFilter(RegState.Phone), F.text)
async def process_phone_text(message: Message, state: FSMContext) -> None:
    """Handle text input when expecting phone contact."""
    data = await state.get_data()
    lang = data.get("language", "en")
    
    # Check for cancel
    if message.text.strip() in [get_text("cancel", "ru"), get_text("cancel", "uz"), get_text("cancel", "en")]:
        return await cmd_cancel(message, state)
    
    await message.answer(
        get_text("invalid_phone", lang),
        reply_markup=create_phone_keyboard(lang),
    )


# ==================== Payment Handlers ====================

@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery) -> None:
    """Process pre-checkout query - confirm payment."""
    user_id = pre_checkout_query.from_user.id
    username = pre_checkout_query.from_user.username or "N/A"
    
    logger.info(f"[{user_id}] [{username}] - Pre-checkout query received")
    
    # Always confirm pre-checkout
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message, state: FSMContext) -> None:
    """Process successful payment."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    logger.info(f"[{user_id}] [{username}] - Payment successful: {message.successful_payment.total_amount} {message.successful_payment.currency}")
    
    # Update state with payment info
    await state.update_data(payment_status=True)
    
    # Send success message
    await message.answer(get_text("payment_success", lang))
    
    # Ask for screenshot
    await message.answer(get_text("ask_screenshot", lang))
    await state.set_state(RegState.ScreenshotProof)


# ==================== Screenshot Handler ====================

@router.message(StateFilter(RegState.ScreenshotProof), F.photo)
async def process_screenshot(message: Message, state: FSMContext) -> None:
    """Process screenshot upload."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    data = await state.get_data()
    lang = data.get("language", "en")
    
    # Get the largest photo
    photo = message.photo[-1]
    file_id = photo.file_id
    
    logger.info(f"[{user_id}] [{username}] - Uploaded screenshot: {file_id}")
    
    # Save screenshot file ID
    await state.update_data(screenshot_file_id=file_id)
    
    # Get all data and save to database
    final_data = await state.get_data()
    
    try:
        # Create user in database
        user = await DatabaseManager.create_user(
            telegram_id=user_id,
            username=username if username != "N/A" else None,
            surname=final_data["surname"],
            name=final_data["name"],
            grade=final_data["grade"],
            school=final_data["school"],
            phone=final_data["phone"],
            language=LanguageEnum(lang),
            payment_status=True,
            screenshot_file_id=file_id,
        )
        
        logger.info(f"[{user_id}] [{username}] - Registration completed, DB ID: {user.id}")
        
        # Send completion message
        await message.answer(
            get_text(
                "registration_complete",
                lang,
                surname=final_data["surname"],
                name=final_data["name"],
                grade=final_data["grade"],
                school=final_data["school"],
                phone=final_data["phone"],
            ),
            reply_markup=ReplyKeyboardRemove(),
        )
        
        # Clear state
        await state.clear()
        
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


# ==================== Fallback Handler ====================

@router.message()
async def handle_unknown(message: Message, state: FSMContext) -> None:
    """Handle unknown messages."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    
    logger.info(f"[{user_id}] [{username}] - Unknown message: {message.text or message.content_type}")
    
    # Get current state
    current_state = await state.get_state()
    
    if current_state is None:
        # No active state, suggest /start
        data = await state.get_data()
        lang = data.get("language", "en")
        await message.answer(get_text("help", lang))

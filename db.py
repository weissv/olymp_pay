"""
Database module with SQLAlchemy async setup.
Structured for easy migration from SQLite to PostgreSQL.
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Integer, String, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import DATABASE_URL


class LanguageEnum(str, enum.Enum):
    """Supported languages enumeration."""
    RU = "ru"
    UZ = "uz"
    EN = "en"


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class User(Base):
    """User model for storing registration data.
    
    NOTE: telegram_id is NOT unique - one parent can register multiple children.
    """
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # REMOVED unique=True to allow multiple registrations per Telegram account
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Parent/Guardian info
    parent_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Participant (child) info
    surname: Mapped[str] = mapped_column(String(255), nullable=False)  # Participant's surname
    name: Mapped[str] = mapped_column(String(255), nullable=False)      # Participant's name
    grade: Mapped[int] = mapped_column(Integer, nullable=False)         # Grades 1-8 only
    school: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Charge ID for Payme (format: {id}_{Surname}_{Name}_{Grade})
    charge_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, unique=True, index=True)
    
    # System fields
    language: Mapped[LanguageEnum] = mapped_column(
        Enum(LanguageEnum, native_enum=False, length=10),
        nullable=False,
        default=LanguageEnum.RU
    )
    payment_status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    screenshot_file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, participant={self.name} {self.surname})>"


# Database engine and session factory
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    future=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database and create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get a new database session."""
    async with async_session() as session:
        return session


class DatabaseManager:
    """Manager class for database operations."""
    
    @staticmethod
    def transliterate_for_order_id(text: str) -> str:
        """Transliterate Cyrillic to Latin and clean for order_id."""
        cyrillic_to_latin = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            'ў': 'o', 'қ': 'q', 'ғ': 'g', 'ҳ': 'h',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
            'Ў': 'O', 'Қ': 'Q', 'Ғ': 'G', 'Ҳ': 'H',
        }
        result = ''
        for char in text:
            result += cyrillic_to_latin.get(char, char)
        # Remove spaces and special characters, keep only alphanumeric
        import re
        result = re.sub(r'[^a-zA-Z0-9]', '', result)
        return result
    
    @staticmethod
    def generate_charge_id(db_id: int, surname: str, name: str, grade: int) -> str:
        """Generate charge_id in format: {db_id}_{Surname}_{Name}_{Grade}.
        
        Example: 12345_Ivanov_Ivan_5
        """
        clean_surname = DatabaseManager.transliterate_for_order_id(surname)
        clean_name = DatabaseManager.transliterate_for_order_id(name)
        return f"{db_id}_{clean_surname}_{clean_name}_{grade}"
    
    @staticmethod
    async def create_user(
        telegram_id: int,
        username: Optional[str],
        parent_name: str,
        email: str,
        phone: str,
        surname: str,
        name: str,
        grade: int,
        school: str,
        language: LanguageEnum,
        payment_status: bool = False,
        screenshot_file_id: Optional[str] = None,
    ) -> User:
        """Create a new user/registration in the database.
        
        NOTE: Multiple registrations with the same telegram_id are allowed.
        The charge_id is generated after insert to include the database ID.
        Format: {db_id}_{Surname}_{Name}_{Grade}
        """
        async with async_session() as session:
            user = User(
                telegram_id=telegram_id,
                username=username,
                parent_name=parent_name,
                email=email,
                phone=phone,
                surname=surname,
                name=name,
                grade=grade,
                school=school,
                language=language,
                payment_status=payment_status,
                screenshot_file_id=screenshot_file_id,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            # Generate charge_id with the database ID
            user.charge_id = DatabaseManager.generate_charge_id(
                db_id=user.id,
                surname=surname,
                name=name,
                grade=grade
            )
            await session.commit()
            await session.refresh(user)
            return user
    
    @staticmethod
    async def get_registrations_by_telegram_id(telegram_id: int) -> list[User]:
        """Get all registrations by Telegram ID."""
        from sqlalchemy import select
        
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id).order_by(User.created_at.desc())
            )
            return list(result.scalars().all())
    
    @staticmethod
    async def get_registration_by_id(registration_id: int) -> Optional[User]:
        """Get registration by database ID."""
        from sqlalchemy import select
        
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.id == registration_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_registration_by_charge_id(charge_id: str) -> Optional[User]:
        """Get registration by charge_id (for Payme callback)."""
        from sqlalchemy import select
        
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.charge_id == charge_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def update_registration_payment(registration_id: int, payment_status: bool, screenshot_file_id: Optional[str] = None) -> Optional[User]:
        """Update registration payment status and screenshot."""
        from sqlalchemy import select
        
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.id == registration_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user.payment_status = payment_status
                if screenshot_file_id:
                    user.screenshot_file_id = screenshot_file_id
                await session.commit()
                await session.refresh(user)
            return user
    
    @staticmethod
    async def get_all_users() -> list[User]:
        """Get all users from the database."""
        from sqlalchemy import select
        
        async with async_session() as session:
            result = await session.execute(select(User).order_by(User.created_at.desc()))
            return list(result.scalars().all())
    
    @staticmethod
    async def get_registration_count_by_telegram_id(telegram_id: int) -> int:
        """Get count of registrations for a Telegram ID."""
        from sqlalchemy import select, func
        
        async with async_session() as session:
            result = await session.execute(
                select(func.count(User.id)).where(User.telegram_id == telegram_id)
            )
            return result.scalar() or 0

    @staticmethod
    async def get_detailed_statistics() -> dict:
        """
        Get comprehensive statistics for admin /news command.
        Returns detailed breakdown of registrations, payments, grades, etc.
        """
        from sqlalchemy import select, func, distinct, case
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        async with async_session() as session:
            stats = {}
            
            # 1. Total registrations
            total_result = await session.execute(select(func.count(User.id)))
            stats['total_registrations'] = total_result.scalar() or 0
            
            # 2. Unique Telegram users (parents)
            unique_users_result = await session.execute(
                select(func.count(distinct(User.telegram_id)))
            )
            stats['unique_telegram_users'] = unique_users_result.scalar() or 0
            
            # 3. Payment statistics
            paid_result = await session.execute(
                select(func.count(User.id)).where(User.payment_status == True)
            )
            stats['paid_count'] = paid_result.scalar() or 0
            stats['unpaid_count'] = stats['total_registrations'] - stats['paid_count']
            stats['payment_rate'] = round(
                (stats['paid_count'] / stats['total_registrations'] * 100) if stats['total_registrations'] > 0 else 0, 1
            )
            
            # 4. Screenshots uploaded
            screenshots_result = await session.execute(
                select(func.count(User.id)).where(User.screenshot_file_id.isnot(None))
            )
            stats['screenshots_uploaded'] = screenshots_result.scalar() or 0
            
            # 5. Registrations by grade
            grades_result = await session.execute(
                select(User.grade, func.count(User.id)).group_by(User.grade).order_by(User.grade)
            )
            stats['by_grade'] = {row[0]: row[1] for row in grades_result.fetchall()}
            
            # 6. Paid registrations by grade
            paid_by_grade_result = await session.execute(
                select(User.grade, func.count(User.id))
                .where(User.payment_status == True)
                .group_by(User.grade)
                .order_by(User.grade)
            )
            stats['paid_by_grade'] = {row[0]: row[1] for row in paid_by_grade_result.fetchall()}
            
            # 7. Registrations by language
            lang_result = await session.execute(
                select(User.language, func.count(User.id)).group_by(User.language)
            )
            stats['by_language'] = {str(row[0].value): row[1] for row in lang_result.fetchall()}
            
            # 8. Today's registrations
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_result = await session.execute(
                select(func.count(User.id)).where(User.created_at >= today_start)
            )
            stats['today_registrations'] = today_result.scalar() or 0
            
            # 9. Today's paid
            today_paid_result = await session.execute(
                select(func.count(User.id)).where(
                    User.created_at >= today_start,
                    User.payment_status == True
                )
            )
            stats['today_paid'] = today_paid_result.scalar() or 0
            
            # 10. Last 7 days registrations
            week_ago = datetime.now() - timedelta(days=7)
            week_result = await session.execute(
                select(func.count(User.id)).where(User.created_at >= week_ago)
            )
            stats['last_7_days_registrations'] = week_result.scalar() or 0
            
            # 11. Last 7 days paid
            week_paid_result = await session.execute(
                select(func.count(User.id)).where(
                    User.created_at >= week_ago,
                    User.payment_status == True
                )
            )
            stats['last_7_days_paid'] = week_paid_result.scalar() or 0
            
            # 12. Top schools (by registration count)
            schools_result = await session.execute(
                select(User.school, func.count(User.id).label('cnt'))
                .group_by(User.school)
                .order_by(func.count(User.id).desc())
                .limit(10)
            )
            stats['top_schools'] = [(row[0], row[1]) for row in schools_result.fetchall()]
            
            # 13. Average registrations per user (parent)
            stats['avg_registrations_per_user'] = round(
                stats['total_registrations'] / stats['unique_telegram_users'] if stats['unique_telegram_users'] > 0 else 0, 2
            )
            
            # 14. Users with multiple registrations
            multi_reg_result = await session.execute(
                select(func.count(distinct(User.telegram_id)))
                .where(
                    User.telegram_id.in_(
                        select(User.telegram_id)
                        .group_by(User.telegram_id)
                        .having(func.count(User.id) > 1)
                    )
                )
            )
            stats['users_with_multiple_registrations'] = multi_reg_result.scalar() or 0
            
            # 15. Registrations by date (last 7 days breakdown)
            daily_stats = []
            for i in range(7):
                day = datetime.now() - timedelta(days=i)
                day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)
                
                day_count_result = await session.execute(
                    select(func.count(User.id)).where(
                        User.created_at >= day_start,
                        User.created_at < day_end
                    )
                )
                day_paid_result = await session.execute(
                    select(func.count(User.id)).where(
                        User.created_at >= day_start,
                        User.created_at < day_end,
                        User.payment_status == True
                    )
                )
                daily_stats.append({
                    'date': day_start.strftime('%d.%m'),
                    'registrations': day_count_result.scalar() or 0,
                    'paid': day_paid_result.scalar() or 0
                })
            stats['daily_breakdown'] = daily_stats
            
            # 16. First and last registration timestamps
            first_result = await session.execute(
                select(User.created_at).order_by(User.created_at.asc()).limit(1)
            )
            last_result = await session.execute(
                select(User.created_at).order_by(User.created_at.desc()).limit(1)
            )
            first_reg = first_result.scalar_one_or_none()
            last_reg = last_result.scalar_one_or_none()
            stats['first_registration'] = first_reg.strftime('%d.%m.%Y %H:%M') if first_reg else 'N/A'
            stats['last_registration'] = last_reg.strftime('%d.%m.%Y %H:%M') if last_reg else 'N/A'
            
            # 17. Potential revenue
            from config import OLYMPIAD_PRICE
            stats['total_potential_revenue'] = stats['total_registrations'] * OLYMPIAD_PRICE
            stats['actual_revenue'] = stats['paid_count'] * OLYMPIAD_PRICE
            stats['pending_revenue'] = stats['unpaid_count'] * OLYMPIAD_PRICE
            
            return stats

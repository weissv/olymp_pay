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
    """User model for storing registration data."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    surname: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    school: Mapped[str] = mapped_column(String(500), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
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
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name={self.name} {self.surname})>"


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
    async def create_user(
        telegram_id: int,
        username: Optional[str],
        surname: str,
        name: str,
        grade: int,
        school: str,
        phone: str,
        language: LanguageEnum,
        payment_status: bool = False,
        screenshot_file_id: Optional[str] = None,
    ) -> User:
        """Create a new user in the database."""
        async with async_session() as session:
            user = User(
                telegram_id=telegram_id,
                username=username,
                surname=surname,
                name=name,
                grade=grade,
                school=school,
                phone=phone,
                language=language,
                payment_status=payment_status,
                screenshot_file_id=screenshot_file_id,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    
    @staticmethod
    async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        from sqlalchemy import select
        
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user_payment(telegram_id: int, payment_status: bool) -> Optional[User]:
        """Update user payment status."""
        from sqlalchemy import select
        
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user.payment_status = payment_status
                await session.commit()
                await session.refresh(user)
            return user
    
    @staticmethod
    async def update_user_screenshot(telegram_id: int, screenshot_file_id: str) -> Optional[User]:
        """Update user screenshot file ID."""
        from sqlalchemy import select
        
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if user:
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
    async def user_exists(telegram_id: int) -> bool:
        """Check if user already exists."""
        user = await DatabaseManager.get_user_by_telegram_id(telegram_id)
        return user is not None

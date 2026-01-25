# 🏆 Olympiad Registration Bot

A production-ready Telegram bot for Olympiad registration built with **aiogram 3.x**, **SQLAlchemy Async**, and **Pandas**.

## ✨ Features

- **Multi-language Support**: Russian, Uzbek, English
- **Complete Registration Flow**: FSM-based step-by-step registration
- **Payment Integration**: Payme provider support via Telegram Payments
- **Screenshot Verification**: Manual verification option for payments
- **Admin Export**: Export all registrations to Excel
- **Comprehensive Logging**: All user interactions logged

## 📁 Project Structure

```
olymp_pay/
├── config.py          # Configuration and environment variables
├── db.py              # Database models and async engine
├── texts.py           # Internationalization (i18n) texts
├── handlers.py        # FSM handlers and bot logic
├── middleware.py      # Logging and throttling middleware
├── main.py            # Entry point
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variables template
└── README.md          # Documentation
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd olymp_pay
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual values
```

Required environment variables:
- `BOT_TOKEN` - Get from [@BotFather](https://t.me/BotFather)
- `PAYMENT_PROVIDER_TOKEN` - Get from Payme or BotFather payments setup
- `ADMIN_IDS` - Comma-separated Telegram user IDs for admin access

### 3. Run the Bot

```bash
python main.py
```

## 📋 Registration Flow

1. **Language Selection** - User chooses preferred language
2. **Surname** - Enter surname (text validation)
3. **Name** - Enter first name (text validation)
4. **Grade** - Enter grade/class (1-11 validation)
5. **School** - Enter school name
6. **Phone** - Share contact via button
7. **Payment** - Pay via Payme invoice
8. **Screenshot** - Upload payment receipt screenshot
9. **Complete** - Registration confirmed

## 🔧 Admin Commands

| Command | Description |
|---------|-------------|
| `/export` | Export all registrations to Excel file |

Only users listed in `ADMIN_IDS` can use admin commands.

## 🗄️ Database

The bot uses SQLAlchemy with async support. Default is SQLite for development, easily switchable to PostgreSQL for production.

### SQLite (Development)
```
DATABASE_URL=sqlite+aiosqlite:///./olympiad.db
```

### PostgreSQL (Production)
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/olympiad
```

### User Table Schema

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| telegram_id | BigInteger | Unique Telegram user ID |
| username | String | Telegram username |
| surname | String | User's surname |
| name | String | User's first name |
| grade | Integer | School grade (1-11) |
| school | String | School name |
| phone | String | Phone number |
| language | Enum | Preferred language (ru/uz/en) |
| payment_status | Boolean | Payment completed |
| screenshot_file_id | String | Telegram file ID of receipt |
| created_at | DateTime | Registration timestamp |

## 📝 Logging

All user interactions are logged to:
- **Console** - For real-time monitoring
- **bot.log** - For persistent storage

Log format:
```
[2024-01-15 10:30:45] [INFO] [handlers] - [123456789] [username] - Started registration (/start)
```

## 🔒 Security Notes

1. Never commit `.env` file to version control
2. Use environment variables for sensitive data
3. Regularly rotate bot tokens
4. Keep `ADMIN_IDS` updated and minimal

## 🐛 Troubleshooting

### Bot doesn't start
- Check `BOT_TOKEN` is valid
- Ensure all dependencies are installed

### Payments don't work
- Verify `PAYMENT_PROVIDER_TOKEN` is correct
- Check Payme integration in BotFather

### Database errors
- Ensure write permissions in project directory
- For PostgreSQL, verify connection string

## 📄 License

MIT License - Feel free to use and modify.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

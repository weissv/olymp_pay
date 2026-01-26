# 🏆 Olympiad Registration Bot

A production-ready Telegram bot for Olympiad registration built with **aiogram 3.x**, **SQLAlchemy Async**, and **Pandas**.

## ✨ Features

- **Multi-language Support**: Russian, Uzbek, English
- **Multiple Participants**: Register multiple children from one Telegram account
- **Complete Registration Flow**: FSM-based step-by-step registration
- **Payme Integration**: Checkout URL-based payment (no native Telegram payments)
- **Screenshot Verification**: Upload payment receipt for verification
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
├── nixpacks.toml      # Deployment config (Coolify/Nixpacks)
├── runtime.txt        # Python version specification
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
- `PAYME_MERCHANT_ID` - Get from Payme Business dashboard
- `ADMIN_IDS` - Comma-separated Telegram user IDs for admin access

### 3. Run the Bot

```bash
python main.py
```

## 📋 Registration Flow

1. **Language Selection** - User chooses preferred language
2. **Parent Name** - Enter parent/guardian full name
3. **Email** - Enter contact email
4. **Participant Surname** - Enter participant's surname
5. **Participant Name** - Enter participant's first name
6. **Grade** - Enter grade (1-8 only, Olympiad restriction)
7. **School** - Enter school name
8. **Phone** - Share contact via button
9. **Payment** - Click Payme link and complete payment
10. **Screenshot** - Upload payment receipt screenshot
11. **Complete** - Registration confirmed
12. **Register Another** - Option to register another participant

## 💳 Payment System

The bot uses **Payme checkout URLs** (not native Telegram payments):

1. User fills registration data
2. Bot generates a checkout URL with base64-encoded parameters:
   - Merchant ID
   - Amount (in tiyin)
   - User ID
   - Student name
   - Grade
3. User clicks "Pay via Payme" button → opens Payme checkout page
4. After payment, user clicks "I have paid" and uploads screenshot
5. Admin can verify payments via exported Excel

### Payme URL Format
```
https://checkout.paycom.uz/{base64_encoded_params}
```

Parameters:
```
m={merchant_id};ac.user_id={telegram_id};ac.student={student_name};ac.grade={grade};a={amount}
```

## 🔧 Commands

| Command | Description | Access |
|---------|-------------|--------|
| `/start` | Start registration | All users |
| `/help` | Show help information | All users |
| `/cancel` | Cancel current registration | All users |
| `/myid` | Show your Telegram ID | All users |
| `/export` | Export registrations to Excel | Admins only |

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

**Note**: The bot auto-converts `postgres://` to `postgresql+asyncpg://` for compatibility with services like Coolify.

### User Table Schema

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key, auto-increment |
| telegram_id | BigInteger | Telegram user ID (NOT unique - allows multiple registrations) |
| username | String | Telegram username |
| parent_name | String | Parent/Guardian full name |
| email | String | Contact email |
| phone | String | Phone number |
| surname | String | Participant's surname |
| name | String | Participant's first name |
| grade | Integer | School grade (1-8) |
| school | String | School name |
| language | Enum | Preferred language (ru/uz/en) |
| payment_status | Boolean | Payment completed |
| screenshot_file_id | String | Telegram file ID of receipt |
| created_at | DateTime | Registration timestamp |

## 🚀 Deployment (Coolify)

The bot is configured for Coolify deployment with Nixpacks:

1. Push to your Git repository
2. Connect repository in Coolify
3. Set environment variables in Coolify dashboard
4. Deploy

Required files:
- `nixpacks.toml` - Build configuration
- `runtime.txt` - Python version (3.10)

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
5. Verify payment screenshots manually

## 🐛 Troubleshooting

### Bot doesn't start
- Check `BOT_TOKEN` is valid
- Ensure all dependencies are installed

### Payment link doesn't work
- Verify `PAYME_MERCHANT_ID` is correct
- Check merchant is activated in Payme Business

### Database errors
- Ensure write permissions in project directory
- For PostgreSQL, verify connection string
- If migrating from old schema, drop and recreate tables

### Deployment issues on Coolify
- Check `nixpacks.toml` configuration
- Ensure `runtime.txt` specifies Python version
- Verify all environment variables are set

## 📄 License

MIT License - Feel free to use and modify.

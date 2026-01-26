# Настройка валидации платежей через Payme Webhook

## 📋 Что нужно сделать

### 1. В личном кабинете Payme Business

1. **Войдите в настройки мерчанта** (`6971f5d5922bebc549a8f6d7`)
2. **Найдите раздел "Webhook" или "Endpoint"**
3. **Укажите URL вашего сервера:**
   ```
   https://ваш-домен.com/payme/webhook
   ```
   Или если используете Coolify:
   ```
   https://your-app-domain.coolify.io/payme/webhook
   ```

4. **Сохраните настройки**

---

## 🔐 Как работает валидация

Payme отправляет POST запросы на ваш webhook URL в формате JSON-RPC 2.0:

### Методы которые будет вызывать Payme:

1. **CheckPerformTransaction** - проверка возможности оплаты
2. **CreateTransaction** - создание транзакции
3. **PerformTransaction** - подтверждение оплаты
4. **CancelTransaction** - отмена платежа
5. **CheckTransaction** - проверка статуса

---

## 💻 Код для обработки webhook

Добавьте в ваш проект файл `payme_webhook.py`:

\`\`\`python
"""
Payme Webhook Handler
Документация: https://developer.help.paycom.uz/metody-merchant-api
"""

import hashlib
import base64
import logging
from typing import Dict, Any
from datetime import datetime

from aiogram import Router
from aiogram.types import Update
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse

from config import PAYME_SECRET_KEY
from db import DatabaseManager

logger = logging.getLogger(__name__)

# Создайте FastAPI app или используйте существующий
app = FastAPI()


def verify_payme_signature(auth_header: str) -> bool:
    """Проверка подписи запроса от Payme."""
    try:
        # Формат: Basic base64(merchant_id:secret_key)
        if not auth_header or not auth_header.startswith('Basic '):
            return False
        
        encoded = auth_header.replace('Basic ', '')
        decoded = base64.b64decode(encoded).decode('utf-8')
        
        # Проверяем что secret_key совпадает
        if PAYME_SECRET_KEY in decoded:
            return True
        return False
    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return False


@app.post("/payme/webhook")
async def payme_webhook(
    request: Request,
    authorization: str = Header(None)
):
    """
    Обработчик webhook от Payme.
    Валидирует платежи по charge_id.
    """
    
    # Проверка подписи
    if not verify_payme_signature(authorization):
        logger.warning("Invalid Payme signature")
        return JSONResponse(
            status_code=401,
            content={
                "error": {
                    "code": -32504,
                    "message": "Insufficient privilege to perform this method."
                }
            }
        )
    
    # Получаем тело запроса
    try:
        body = await request.json()
        logger.info(f"Payme webhook received: {body}")
    except Exception as e:
        logger.error(f"Failed to parse webhook body: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
        )
    
    method = body.get("method")
    params = body.get("params", {})
    request_id = body.get("id")
    
    # Обработка методов
    if method == "CheckPerformTransaction":
        return await check_perform_transaction(params, request_id)
    
    elif method == "CreateTransaction":
        return await create_transaction(params, request_id)
    
    elif method == "PerformTransaction":
        return await perform_transaction(params, request_id)
    
    elif method == "CancelTransaction":
        return await cancel_transaction(params, request_id)
    
    elif method == "CheckTransaction":
        return await check_transaction(params, request_id)
    
    else:
        return JSONResponse(
            content={
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                },
                "id": request_id
            }
        )


async def check_perform_transaction(params: Dict[str, Any], request_id: int):
    """
    Проверка возможности выполнения транзакции.
    Паметр ac.charge_id должен существовать в БД.
    """
    try:
        account = params.get("account", {})
        charge_id = account.get("charge_id")
        amount = params.get("amount")  # в тийинах
        
        if not charge_id:
            return JSONResponse(
                content={
                    "error": {
                        "code": -31050,
                        "message": "charge_id not provided"
                    },
                    "id": request_id
                }
            )
        
        # Проверяем существование charge_id в БД
        user = await DatabaseManager.get_registration_by_charge_id(charge_id)
        
        if not user:
            return JSONResponse(
                content={
                    "error": {
                        "code": -31050,
                        "message": "Registration not found"
                    },
                    "id": request_id
                }
            )
        
        # Проверка суммы (опционально)
        # from config import OLYMPIAD_PRICE
        # if amount != OLYMPIAD_PRICE:
        #     return error "Invalid amount"
        
        # Всё ок
        return JSONResponse(
            content={
                "result": {
                    "allow": True
                },
                "id": request_id
            }
        )
        
    except Exception as e:
        logger.error(f"CheckPerformTransaction error: {e}")
        return JSONResponse(
            content={
                "error": {
                    "code": -32400,
                    "message": "Internal error"
                },
                "id": request_id
            }
        )


async def create_transaction(params: Dict[str, Any], request_id: int):
    """
    Создание транзакции (резервирование платежа).
    Сохраняем transaction_id и ставим статус "pending".
    """
    try:
        transaction_id = params.get("id")
        account = params.get("account", {})
        charge_id = account.get("charge_id")
        amount = params.get("amount")
        time = params.get("time")  # Unix timestamp в миллисекундах
        
        user = await DatabaseManager.get_registration_by_charge_id(charge_id)
        
        if not user:
            return JSONResponse(
                content={
                    "error": {
                        "code": -31050,
                        "message": "Registration not found"
                    },
                    "id": request_id
                }
            )
        
        # Здесь можно сохранить transaction_id в отдельную таблицу
        # или добавить поле в User модель
        
        # TODO: Сохраните transaction_id, amount, time в БД
        # await DatabaseManager.save_payme_transaction(
        #     charge_id=charge_id,
        #     transaction_id=transaction_id,
        #     amount=amount,
        #     state=1  # 1 = created
        # )
        
        return JSONResponse(
            content={
                "result": {
                    "create_time": time,
                    "transaction": str(user.id),
                    "state": 1
                },
                "id": request_id
            }
        )
        
    except Exception as e:
        logger.error(f"CreateTransaction error: {e}")
        return JSONResponse(
            content={
                "error": {
                    "code": -32400,
                    "message": "Internal error"
                },
                "id": request_id
            }
        )


async def perform_transaction(params: Dict[str, Any], request_id: int):
    """
    Подтверждение оплаты.
    Обновляем payment_status = True в БД.
    """
    try:
        transaction_id = params.get("id")
        
        # TODO: Найдите запись по transaction_id
        # transaction = await DatabaseManager.get_transaction(transaction_id)
        # user = await DatabaseManager.get_registration_by_charge_id(transaction.charge_id)
        
        # Для простоты - обновим по transaction_id напрямую
        # await DatabaseManager.update_registration_payment(
        #     registration_id=user.id,
        #     payment_status=True,
        #     screenshot_file_id=None  # Оплата через Payme, скриншот не нужен
        # )
        
        # TODO: Обновите state транзакции на 2 (performed)
        
        perform_time = int(datetime.now().timestamp() * 1000)
        
        return JSONResponse(
            content={
                "result": {
                    "transaction": str(transaction_id),
                    "perform_time": perform_time,
                    "state": 2
                },
                "id": request_id
            }
        )
        
    except Exception as e:
        logger.error(f"PerformTransaction error: {e}")
        return JSONResponse(
            content={
                "error": {
                    "code": -32400,
                    "message": "Internal error"
                },
                "id": request_id
            }
        )


async def cancel_transaction(params: Dict[str, Any], request_id: int):
    """Отмена транзакции."""
    try:
        transaction_id = params.get("id")
        reason = params.get("reason")
        
        # TODO: Обновите state транзакции на -1 или -2 (cancelled)
        
        cancel_time = int(datetime.now().timestamp() * 1000)
        
        return JSONResponse(
            content={
                "result": {
                    "transaction": str(transaction_id),
                    "cancel_time": cancel_time,
                    "state": -1
                },
                "id": request_id
            }
        )
        
    except Exception as e:
        logger.error(f"CancelTransaction error: {e}")
        return JSONResponse(
            content={
                "error": {
                    "code": -32400,
                    "message": "Internal error"
                },
                "id": request_id
            }
        )


async def check_transaction(params: Dict[str, Any], request_id: int):
    """Проверка статуса транзакции."""
    try:
        transaction_id = params.get("id")
        
        # TODO: Получите статус из БД
        # transaction = await DatabaseManager.get_transaction(transaction_id)
        
        return JSONResponse(
            content={
                "result": {
                    "create_time": 0,  # TODO: из БД
                    "perform_time": 0,  # TODO: из БД
                    "cancel_time": 0,
                    "transaction": str(transaction_id),
                    "state": 2,  # TODO: из БД
                    "reason": None
                },
                "id": request_id
            }
        )
        
    except Exception as e:
        logger.error(f"CheckTransaction error: {e}")
        return JSONResponse(
            content={
                "error": {
                    "code": -32400,
                    "message": "Internal error"
                },
                "id": request_id
            }
        )
\`\`\`

---

## 🗄️ Дополнительная таблица для транзакций (опционально)

Добавьте в `db.py`:

\`\`\`python
class PaymeTransaction(Base):
    """Payme transactions table."""
    
    __tablename__ = "payme_transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    charge_id: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # в тийинах
    state: Mapped[int] = mapped_column(Integer, nullable=False)  # 1=created, 2=performed, -1=cancelled
    create_time: Mapped[int] = mapped_column(BigInteger, nullable=False)
    perform_time: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    cancel_time: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    reason: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
\`\`\`

---

## 🧪 Тестирование

1. **Откройте Payme URL** и сделайте тестовую оплату
2. **Проверьте логи сервера** - должны появиться записи о вызовах webhook
3. **В Payme Business** проверьте статус транзакции - должен быть "Оплачено"
4. **В вашей БД** проверьте что `payment_status = true`

---

## 📚 Коды ошибок Payme

| Код | Описание |
|-----|----------|
| -31050 | charge_id не найден в системе |
| -31051 | Неверная сумма платежа |
| -31008 | Транзакция не может быть отменена |
| -32504 | Неверная подпись |
| -32700 | Ошибка парсинга JSON |
| -32400 | Внутренняя ошибка |

---

## 🔗 Полезные ссылки

- [Документация Payme Merchant API](https://developer.help.paycom.uz/metody-merchant-api)
- [Коды ошибок](https://developer.help.paycom.uz/obshie-harakteristiki/kody-oshibok)
- [Тестирование](https://developer.help.paycom.uz/testirovanie)

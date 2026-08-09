import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    PreCheckoutQuery,
)

from config import BOT_TOKEN, WEBAPP_URL, PREMIUM_PRICE_STARS
from database import get_or_create_user, grant_premium

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("codelingo-bot")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await get_or_create_user(message.from_user.id, message.from_user.username or "")

    if not WEBAPP_URL:
        await message.answer(
            "Привет! Я CodeLingo 👾\n\n"
            "BASE_URL ещё не настроен на сервере, поэтому кнопка мини-приложения недоступна. "
            "Проверь переменные окружения (см. README)."
        )
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Открыть CodeLingo", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
    )
    await message.answer(
        "Привет! Я <b>CodeLingo</b> 👾\n"
        "Учу программированию так же затягивающе, как Duolingo учит языкам.\n\n"
        "Жми кнопку ниже и поехали 👇",
        reply_markup=kb,
        parse_mode="HTML",
    )


@dp.message(F.text == "/premium")
async def cmd_premium(message: Message):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="CodeLingo Premium",
        description="Безлимитные HP, никаких пауз в обучении. Подписка на 30 дней.",
        payload=f"premium_{message.from_user.id}",
        currency="XTR",
        prices=[{"label": "Premium (30 дней)", "amount": PREMIUM_PRICE_STARS}],
        provider_token="",
    )


@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    user_id = message.from_user.id
    new_until = await grant_premium(user_id)
    await message.answer(
        "✅ Premium активирован!\n"
        "Теперь у тебя ∞ HP и доступ ко всем плюшкам. Возвращайся в приложение 🚀"
    )
    log.info(f"User {user_id} activated premium until {new_until}")

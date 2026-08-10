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
import sqlite3
import datetime
import json
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import google.generativeai as genai

# ================= КОНФИГУРАЦИЯ =================
BOT_TOKEN = "8743038849:AAFB8sEkKZ8ilU_m5EAhryP8tQMSxipXfFs"
GEMINI_API_KEY = "AQ.Ab8RN6LIlfOAAokOO_Mu16sY5lXwxjCBKCAv1UCxEtzxdh6kDQ"

# ⚠️ ВСТАВЬ СВОЙ ТЕЛЕГРАМ ID (узнать можно в боте @userinfobot)
OWNER_ID = 123456789  

# Ссылка на твой задеплоенный WebApp (Vercel / GitHub Pages)
WEBAPP_URL = "https://your-username.github.io/your-repo/webapp"
CHANNEL_AVATAR_URL = "https://i.imgur.com/example.jpg"  # Ссылка на аватарку ТГК

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================= БАЗА ДАННЫХ =================
conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    role TEXT DEFAULT 'user',
    last_quiz_date TEXT
)
''')
conn.commit()

def get_user_status(user_id: int) -> str:
    if user_id == OWNER_ID:
        return f"👑 СТАТУС: ВЛАДЕЛЕЦ 👑\n\n[⁠]({CHANNEL_AVATAR_URL})"
    
    cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    role = res[0] if res else 'user'
    
    if role == 'premium':
        return "Статус: Premium ⭐️"
    return "Статус: Обычный 👤"

def check_limit(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    
    cursor.execute("SELECT role, last_quiz_date FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    if not res:
        return True
    
    role, last_date = res
    if role == 'premium':
        return True
    
    today = str(datetime.date.today())
    return last_date != today

def update_quiz_date(user_id: int):
    today = str(datetime.date.today())
    cursor.execute("""
        INSERT INTO users (user_id, last_quiz_date) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET last_quiz_date = excluded.last_quiz_date
    """, (user_id, today))
    conn.commit()

# ================= ИИ ГЕНЕРАЦИЯ =================
async def generate_questions(language: str):
    prompt = f"""
    Сгенерируй 10 уникальных вопросов для изучения языка: {language}.
    Формат строго JSON array:
    [
      {{
        "question": "Текст вопроса",
        "options": ["A", "B", "C", "D"],
        "answer": 0
      }}
    ]
    """
    try:
        response = await asyncio.to_thread(
            model.generate_content, 
            prompt, 
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Ошибка Gemini: {e}")
        return None

# ================= ХЕНДЛЕРЫ =================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    role = 'owner' if message.from_user.id == OWNER_ID else 'user'
    cursor.execute("INSERT OR IGNORE INTO users (user_id, role) VALUES (?, ?)", (message.from_user.id, role))
    conn.commit()
    
    status_text = get_user_status(message.from_user.id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Открыть WebApp", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="🌍 Выбрать язык (В боте)", callback_data="start_quiz")],
        [InlineKeyboardButton(text="⭐ Купить Premium", callback_data="buy_premium")]
    ])
    
    await message.answer(
        f"Привет! Добро пожаловать в бот изучения языков.\n\n{status_text}", 
        reply_markup=kb, 
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "start_quiz")
async def start_quiz_callback(call: types.CallbackQuery):
    if not check_limit(call.from_user.id):
        await call.message.answer("❌ Дневной лимит исчерпан (1 тест в день).\n\nОформите **Premium**, чтобы учиться без ограничений!")
        await call.answer()
        return

    languages = [
        "Английский", "Испанский", "Немецкий", "Французский", 
        "Китайский", "Японский", "Итальянский", "Арабский", 
        "Русский", "Корейский", "Португальский", "Турецкий"
    ]
    
    buttons = [[InlineKeyboardButton(text=lang, callback_data=f"lang_{lang}")] for lang in languages]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await call.message.edit_text("Выберите один из 12 языков:", reply_markup=kb)
    await call.answer()

@dp.callback_query(F.data.startswith("lang_"))
async def process_lang(call: types.CallbackQuery):
    selected_lang = call.data.split("_")[1]
    await call.message.edit_text(f"⏳ Gemini генерирует 10 вопросов по языку **{selected_lang}**...", parse_mode="Markdown")
    
    questions = await generate_questions(selected_lang)
    if not questions or len(questions) < 10:
        await call.message.answer("Ошибка генерации. Попробуйте еще раз.")
        return
        
    update_quiz_date(call.from_user.id)
    await call.message.answer(f"✅ Вопросы готовы! Можно начинать тест по языку {selected_lang}.")

# Прием данных из WebApp
@dp.message(F.web_app_data)
async def web_app_receive(message: types.Message):
    data = json.loads(message.web_app_data.data)
    await message.answer(f"Получены данные из WebApp: {data}")

# Команда выдачи премиума владельцем
@dp.message(Command("grant_premium"))
async def grant_premium(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return
    try:
        target_id = int(message.text.split()[1])
        cursor.execute("UPDATE users SET role = 'premium' WHERE user_id = ?", (target_id,))
        conn.commit()
        await message.answer(f"Пользователю `{target_id}` успешно выдан Premium!", parse_mode="Markdown")
    except Exception:
        await message.answer("Использование: `/grant_premium <user_id>`", parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


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

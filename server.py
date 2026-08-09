import time
import hashlib
import hmac
from urllib.parse import parse_qsl

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from aiogram.types import Update

from config import (
    BOT_TOKEN,
    WEBHOOK_PATH,
    WEBHOOK_URL,
    PREMIUM_PRICE_STARS,
)
from bot import bot, dp
from database import (
    init_db,
    get_or_create_user,
    update_field,
    is_premium,
    spend_hp,
    add_xp,
)

app = FastAPI(title="CodeLingo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LANGUAGES = [
    "Python", "JavaScript", "HTML/CSS", "C++", "Java", "C#",
    "Kotlin", "Swift", "Go", "Rust", "PHP", "SQL",
]
LEVELS = ["novice", "experienced", "master"]


def check_telegram_auth(init_data: str) -> dict:
    if not init_data:
        raise HTTPException(status_code=401, detail="no init data")
    parsed = dict(parse_qsl(init_data, strict_parsing=True))
    received_hash = parsed.pop("hash", None)
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if calculated_hash != received_hash:
        raise HTTPException(status_code=401, detail="invalid init data")
    return parsed


def verify_user(path_user_id: int, x_init_data: str = "") -> int:
    if not x_init_data:
        return path_user_id
    import json
    parsed = check_telegram_auth(x_init_data)
    try:
        tg_user = json.loads(parsed.get("user", "{}"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=401, detail="bad user payload")
    if tg_user.get("id") and int(tg_user["id"]) != path_user_id:
        raise HTTPException(status_code=403, detail="user id mismatch")
    return path_user_id


@app.on_event("startup")
async def on_startup():
    await init_db()
    if WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


@app.get("/health")
async def health():
    return {"status": "ok", "time": time.time()}


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/api/meta")
async def meta():
    return {"languages": LANGUAGES, "levels": LEVELS, "premium_price_stars": PREMIUM_PRICE_STARS}


@app.get("/api/user/{user_id}")
async def api_get_user(user_id: int):
    row = await get_or_create_user(user_id)
    premium = await is_premium(row)
    row["premium"] = premium
    return JSONResponse(row)


@app.post("/api/user/{user_id}/level")
async def api_set_level(user_id: int, request: Request, x_init_data: str = Header(default="", alias="X-Init-Data")):
    user_id = verify_user(user_id, x_init_data)
    body = await request.json()
    level = body.get("level")
    if level not in LEVELS:
        raise HTTPException(status_code=400, detail="invalid level")
    await get_or_create_user(user_id)
    await update_field(user_id, level=level)
    return {"ok": True}


@app.post("/api/user/{user_id}/language")
async def api_set_language(user_id: int, request: Request, x_init_data: str = Header(default="", alias="X-Init-Data")):
    user_id = verify_user(user_id, x_init_data)
    body = await request.json()
    language = body.get("language")
    if language not in LANGUAGES:
        raise HTTPException(status_code=400, detail="invalid language")
    await get_or_create_user(user_id)
    await update_field(user_id, language=language)
    return {"ok": True}


@app.post("/api/user/{user_id}/answer")
async def api_answer(user_id: int, request: Request, x_init_data: str = Header(default="", alias="X-Init-Data")):
    user_id = verify_user(user_id, x_init_data)
    body = await request.json()
    correct = bool(body.get("correct"))
    row = await get_or_create_user(user_id)
    premium = await is_premium(row)

    if correct:
        xp = await add_xp(user_id, 10)
        hp = row["hp"]
    else:
        xp = row["xp"]
        if premium:
            hp = row["hp"]
        else:
            hp = await spend_hp(user_id)

    return {"xp": xp, "hp": hp, "premium": premium, "out_of_hp": (not premium and hp <= 0)}


@app.post("/api/create_invoice")
async def api_create_invoice(request: Request):
    body = await request.json()
    user_id = body.get("user_id")
    link = await bot.create_invoice_link(
        title="CodeLingo Premium",
        description="Безлимитные HP и все плюшки на 30 дней.",
        payload=f"premium_{user_id}",
        currency="XTR",
        prices=[{"label": "Premium (30 дней)", "amount": PREMIUM_PRICE_STARS}],
        provider_token="",
    )
    return {"link": link}


app.mount("/app", StaticFiles(directory="webapp", html=True), name="webapp")

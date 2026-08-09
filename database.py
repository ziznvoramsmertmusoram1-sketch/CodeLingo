import time
import aiosqlite
from config import DB_PATH, DEFAULT_HP, PREMIUM_DURATION_DAYS

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    level TEXT,
    language TEXT,
    hp INTEGER DEFAULT 5,
    xp INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    last_active REAL,
    premium_until REAL DEFAULT 0,
    created_at REAL
);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(SCHEMA)
        await db.commit()


async def get_or_create_user(user_id: int, username: str = "") -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        if row:
            return dict(row)
        now = time.time()
        await db.execute(
            "INSERT INTO users (user_id, username, level, language, hp, xp, streak, last_active, premium_until, created_at) "
            "VALUES (?, ?, NULL, NULL, ?, 0, 0, ?, 0, ?)",
            (user_id, username, DEFAULT_HP, now, now),
        )
        await db.commit()
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return dict(row)


async def update_field(user_id: int, **fields):
    if not fields:
        return
    keys = ", ".join(f"{k} = ?" for k in fields.keys())
    values = list(fields.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {keys} WHERE user_id = ?", values)
        await db.commit()


async def is_premium(user_row: dict) -> bool:
    return (user_row.get("premium_until") or 0) > time.time()


async def grant_premium(user_id: int, days: int = PREMIUM_DURATION_DAYS):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT premium_until FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        now = time.time()
        current_until = (row["premium_until"] if row and row["premium_until"] else 0)
        base = current_until if current_until > now else now
        new_until = base + days * 86400
        await db.execute(
            "UPDATE users SET premium_until = ?, hp = ? WHERE user_id = ?",
            (new_until, DEFAULT_HP, user_id),
        )
        await db.commit()
        return new_until


async def spend_hp(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT hp FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        new_hp = max(0, (row["hp"] if row else DEFAULT_HP) - 1)
        await db.execute("UPDATE users SET hp = ? WHERE user_id = ?", (new_hp, user_id))
        await db.commit()
        return new_hp


async def add_xp(user_id: int, amount: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT xp FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        new_xp = (row["xp"] if row else 0) + amount
        await db.execute("UPDATE users SET xp = ?, last_active = ? WHERE user_id = ?", (new_xp, time.time(), user_id))
        await db.commit()
        return new_xp

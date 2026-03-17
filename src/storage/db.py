from __future__ import annotations

import aiosqlite


CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_SESSIONS = """
CREATE TABLE IF NOT EXISTS generation_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    platform TEXT,
    niche TEXT,
    product TEXT,
    audience TEXT,
    goal TEXT,
    tone TEXT,
    length TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_CONTENT_PACKS = """
CREATE TABLE IF NOT EXISTS content_packs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES generation_sessions(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    is_demo INTEGER NOT NULL DEFAULT 1,
    content_json TEXT NOT NULL DEFAULT '{}',
    md_path TEXT,
    txt_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_PAYMENTS = """
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    session_id INTEGER NOT NULL REFERENCES generation_sessions(id),
    amount_rub INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    provider TEXT NOT NULL DEFAULT 'dummy',
    provider_payment_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


async def init_db(db_path: str) -> aiosqlite.Connection:
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA foreign_keys=ON")
    await conn.execute(CREATE_USERS)
    await conn.execute(CREATE_SESSIONS)
    await conn.execute(CREATE_CONTENT_PACKS)
    await conn.execute(CREATE_PAYMENTS)
    await conn.commit()
    return conn

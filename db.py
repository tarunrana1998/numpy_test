"""Asynchronous database connection helpers for MySQL.

Contains one helper:
- `get_engine` using `SQLAlchemy`'s async extension (connection-pooling / ORM-ready)

Fill credentials or set environment variables before using.
"""
from typing import Optional
import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
    from sqlalchemy import text
except ImportError:
    create_async_engine = None
    AsyncEngine = None
    text = None


def get_engine(user: str, password: str, host: str, port: int, database: str, driver: str = "aiomysql") -> AsyncEngine:
    """Return an Async SQLAlchemy Engine for MySQL.

    Example dialect: `mysql+aiomysql` (requires `aiomysql` installed).
    """
    if create_async_engine is None:
        raise ImportError("SQLAlchemy asyncio extension is not installed.")
    
    password_encoded = urllib.parse.quote_plus(password)
    url = f"mysql+{driver}://{user}:{password_encoded}@{host}:{port}/{database}"
    engine = create_async_engine(url, pool_pre_ping=True)
    return engine


def _get_env_params():
    """Return connection params from environment variables."""
    host = os.getenv("MYSQL_HOST", "localhost")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DB", "test")
    port = int(os.getenv("MYSQL_PORT", 3306))
    return host, user, password, database, port


async def connect_from_env():
    """Try to connect using environment variables asynchronously."""
    host, user, password, database, port = _get_env_params()
    engine = get_engine(user, password, host, port, database)
    
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        return {"type": "engine", "result": result.all()}


async def fetch_all_products():
    """Fetch all rows from `products` table using env credentials asynchronously."""
    host, user, password, database, port = _get_env_params()
    engine = get_engine(user, password, host, port, database)
    
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT * FROM products"))
        try:
            return [dict(r) for r in result.mappings().all()]
        except Exception:
            return [tuple(r) for r in result.fetchall()]


async def fetch_product_by_id(product_id: int):
    """Fetch a single product by `id` using env credentials asynchronously."""
    host, user, password, database, port = _get_env_params()
    engine = get_engine(user, password, host, port, database)
    
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT * FROM products WHERE id = :id"), {"id": product_id})
        try:
            rows = result.mappings().all()
            return dict(rows[0]) if rows else None
        except Exception:
            rows = result.fetchall()
            return tuple(rows[0]) if rows else None


if __name__ == "__main__":
    import asyncio
    
    async def test():
        try:
            out = await connect_from_env()
            print("Connection type:", out["type"])
            print("Query result:", out["result"])
        except Exception as e:
            print("Connection test failed:", e)

    asyncio.run(test())

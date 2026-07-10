"""Database connection helpers for MySQL.

Contains one helper:
- `get_engine` using `SQLAlchemy` (connection-pooling / ORM-ready)

Fill credentials or set environment variables before using.
"""
from typing import Optional
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from sqlalchemy import create_engine, text
except Exception:
    create_engine = None
    text = None


def get_engine(user: str, password: str, host: str, port: int, database: str, driver: str = "pymysql"):
    """Return a SQLAlchemy Engine for MySQL.

    Example dialect: `mysql+pymysql` (requires `pymysql` installed).
    """
    import urllib.parse
    if create_engine is None:
        raise ImportError("SQLAlchemy is not installed. Install with `pip install sqlalchemy pymysql`")
    
    password_encoded = urllib.parse.quote_plus(password)
    url = f"mysql+{driver}://{user}:{password_encoded}@{host}:{port}/{database}"
    engine = create_engine(url, pool_pre_ping=True)
    return engine


def connect_from_env():
    """Try to connect using environment variables.

    Env vars used: MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT
    Uses SQLAlchemy engine.
    """
    host = os.getenv("MYSQL_HOST", "localhost")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DB", "test")
    port = int(os.getenv("MYSQL_PORT", 3306))

    engine = get_engine(user, password, host, port, database)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        return {"type": "engine", "result": result.all()}


def _get_env_params():
    """Return connection params from environment variables."""
    host = os.getenv("MYSQL_HOST", "localhost")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DB", "test")
    port = int(os.getenv("MYSQL_PORT", 3306))
    return host, user, password, database, port


def fetch_all_products():
    """Fetch all rows from `products` table using env credentials.

    Returns a list of rows as dictionaries when possible.
    """
    host, user, password, database, port = _get_env_params()
    engine = get_engine(user, password, host, port, database)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM products"))
        try:
            return [dict(r) for r in result.mappings().all()]
        except Exception:
            return [tuple(r) for r in result.fetchall()]


def fetch_product_by_id(product_id: int):
    """Fetch a single product by `id` using env credentials.

    Returns a single row (dict or tuple) or None if not found.
    """
    host, user, password, database, port = _get_env_params()
    engine = get_engine(user, password, host, port, database)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM products WHERE id = :id"), {"id": product_id})
        try:
            rows = result.mappings().all()
            return dict(rows[0]) if rows else None
        except Exception:
            rows = result.fetchall()
            return tuple(rows[0]) if rows else None


if __name__ == "__main__":
    # Quick manual test when running this file directly.
    try:
        out = connect_from_env()
        print("Connection type:", out["type"])
        print("Query result:", out["result"])
    except Exception as e:
        print("Connection test failed:", e)

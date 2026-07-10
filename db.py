"""Database connection helpers for MySQL.

Contains two helpers:
- `get_connection` using `mysql-connector-python` (raw connector)
- `get_engine` using `SQLAlchemy` (connection-pooling / ORM-ready)

Fill credentials or set environment variables before using.
"""
from typing import Optional
import os

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except Exception:
    mysql = None
    MySQLError = Exception

try:
    from sqlalchemy import create_engine, text
except Exception:
    create_engine = None
    text = None


def get_connection(host: str, user: str, password: str, database: str, port: int = 3306):
    """Return a mysql.connector connection.

    Raises the underlying exception on failure.
    """
    if mysql is None:
        raise ImportError("mysql-connector-python is not installed. Install with `pip install mysql-connector-python`")
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
        )
        if conn.is_connected():
            return conn
        raise MySQLError("Connection failed without exception")
    except MySQLError:
        raise


def get_engine(user: str, password: str, host: str, port: int, database: str, driver: str = "pymysql"):
    """Return a SQLAlchemy Engine for MySQL.

    Example dialect: `mysql+pymysql` (requires `pymysql` installed).
    """
    if create_engine is None:
        raise ImportError("SQLAlchemy is not installed. Install with `pip install sqlalchemy pymysql`")
    url = f"mysql+{driver}://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(url, pool_pre_ping=True)
    return engine


def connect_from_env():
    """Try to connect using environment variables.

    Env vars used: MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT
    Prefer SQLAlchemy engine; fall back to raw connector.
    """
    host = os.getenv("MYSQL_HOST", "localhost")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DB", "test")
    port = int(os.getenv("MYSQL_PORT", 3306))

    # Try SQLAlchemy first
    try:
        if create_engine is not None:
            engine = get_engine(user, password, host, port, database)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return {"type": "engine", "result": result.all()}
    except Exception as e:
        last_err = e

    # Fallback to raw connector
    try:
        conn = get_connection(host, user, password, database, port)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {"type": "connector", "result": rows}
    except Exception:
        raise last_err


if __name__ == "__main__":
    # Quick manual test when running this file directly.
    try:
        out = connect_from_env()
        print("Connection type:", out["type"])
        print("Query result:", out["result"])
    except Exception as e:
        print("Connection test failed:", e)

import asyncio
from sqlalchemy import text
from db import get_engine, _get_env_params

async def main():
    host, user, password, database, port = _get_env_params()
    engine = get_engine(user, password, host, port, database)

    # Get a connection from the pool
    async with engine.connect() as conn:
        # Execute a query using async await
        result = await conn.execute(text("SELECT NOW()"))
        print("Database time:", result.all())
    
    # Gracefully close all connections in the pool
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

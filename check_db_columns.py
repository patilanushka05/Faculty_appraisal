import asyncio
from src.setup.database import engine
from sqlalchemy import text

async def check_columns():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'book_publications'"))
        columns = [r[0] for r in res]
        print(f"Columns in book_publications: {columns}")

if __name__ == "__main__":
    asyncio.run(check_columns())

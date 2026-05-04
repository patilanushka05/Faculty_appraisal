import asyncio
from src.setup.database import engine
from sqlalchemy import text

async def check_all_columns():
    tables = [
        'journal_publications', 'book_publications', 'ict_pedagogy', 
        'research_guidance', 'research_projects', 'ipr', 
        'research_awards', 'conference_papers', 'research_proposals', 
        'product_developments', 'self_development', 'industrial_training'
    ]
    async with engine.connect() as conn:
        for table in tables:
            res = await conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'"))
            columns = [r[0] for r in res]
            print(f"Columns in {table}: {columns}")

if __name__ == "__main__":
    asyncio.run(check_all_columns())

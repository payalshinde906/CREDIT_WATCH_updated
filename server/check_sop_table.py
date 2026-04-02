import asyncio
from app.database import engine
from sqlalchemy import text

async def check():
    async with engine.connect() as conn:
        try:
            res = await conn.execute(text("SELECT count(*) FROM sop_documents"))
            print(f"Table sop_documents exists. Row count: {res.scalar()}")
        except Exception as e:
            print(f"Error checking sop_documents: {e}")

if __name__ == "__main__":
    asyncio.run(check())

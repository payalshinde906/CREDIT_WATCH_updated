import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import text

async def check():
    async with AsyncSessionLocal() as session:
        res = await session.execute(text('SELECT count(*) FROM plans'))
        count = res.scalar()
        print(f"Plans count: {count}")
        
        if count > 0:
            res_rows = await session.execute(text('SELECT name, price FROM plans'))
            for row in res_rows:
                print(f"- {row.name}: {row.price}")

if __name__ == "__main__":
    asyncio.run(check())

import asyncio
import uuid
from app.database import AsyncSessionLocal
from app.models import Plan
from sqlalchemy import select

DEFAULT_PLANS = [
    { 
        "id": str(uuid.uuid4()), 
        "name": "base", 
        "display_name": "Base", 
        "price": 500, 
        "validity_days": 30, 
        "follow_up_limit": 999, 
        "legal_assistance_limit": 0,
        "description": "Entry-level plan for small businesses",
        "is_active": True
    },
    { 
        "id": str(uuid.uuid4()), 
        "name": "royal", 
        "display_name": "Royal", 
        "price": 1000, 
        "validity_days": 180, 
        "follow_up_limit": 999, 
        "legal_assistance_limit": 5,
        "description": "For growing businesses with legal support",
        "is_active": True
    },
    { 
        "id": str(uuid.uuid4()), 
        "name": "groups", 
        "display_name": "Groups", 
        "price": 2000, 
        "validity_days": 365, 
        "follow_up_limit": 999, 
        "legal_assistance_limit": 20,
        "description": "For organizations managing multiple business entities",
        "is_active": True
    },
    { 
        "id": str(uuid.uuid4()), 
        "name": "enterprise", 
        "display_name": "Enterprise", 
        "price": 100000, 
        "validity_days": 365, 
        "follow_up_limit": 999, 
        "legal_assistance_limit": 100,
        "description": "Enterprise solution with maximum legal assistance",
        "is_active": True
    },
]

async def seed_plans():
    async with AsyncSessionLocal() as session:
        # Check if plans exist
        stmt = select(Plan)
        result = await session.execute(stmt)
        existing = result.scalars().all()
        
        if existing:
            print(f"Server already has {len(existing)} plans. Skipping seed.")
            return

        print("Seeding default plans...")
        for p_data in DEFAULT_PLANS:
            plan = Plan(**p_data)
            session.add(plan)
        
        await session.commit()
        print("Plans seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_plans())

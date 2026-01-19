"""
Quick database connection test script
Run this to verify your database connection is working
"""
import asyncio
import sys
from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_connection():
    """Test database connection"""
    print("=" * 60)
    print("Database Connection Test")
    print("=" * 60)
    print(f"Database URL: {settings.DATABASE_URL.replace(settings.DATABASE_URL.split('@')[0].split('//')[1] if '@' in settings.DATABASE_URL else '', '***') if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    print()
    
    try:
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
        )
        
        print("Attempting to connect...")
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version(), current_database()"))
            row = result.fetchone()
            print("✅ SUCCESS! Database connection working!")
            print()
            print(f"PostgreSQL Version: {row[0]}")
            print(f"Current Database: {row[1]}")
            print()
            print("You can now run the server with: python main.py")
            return True
            
    except Exception as e:
        print("❌ FAILED! Database connection error:")
        print(f"   {str(e)}")
        print()
        print("Common issues:")
        print("1. PostgreSQL is not running")
        print("2. DATABASE_URL is incorrect")
        print("3. Database doesn't exist")
        print("4. Wrong username/password")
        print()
        print("Solutions:")
        print("- Check DATABASE_SETUP.md for detailed instructions")
        print("- Create a .env file with correct DATABASE_URL")
        print("- Ensure PostgreSQL is running")
        print("- Create the database: CREATE DATABASE creditdatawatch;")
        return False
    finally:
        try:
            await engine.dispose()
        except:
            pass

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)


"""
Test registration endpoint directly
"""
import asyncio
import sys
sys.path.insert(0, '.')

async def test_register():
    from app.database import get_db
    from app.services import AuthService
    from app.schemas import RegisterRequest
    
    try:
        # Create test request
        request = RegisterRequest(
            company_name="Test Company",
            email="test123@test.com",
            password="test1234",
            phone="+919876543210",
            gstin="22AAAAACOCOALZ5"
        )
        
        # Get db session
        async for db in get_db():
            result = await AuthService.register(request, db)
            print(f"Success: {result}")
            break
            
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_register())

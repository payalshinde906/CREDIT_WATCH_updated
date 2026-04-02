from fastapi import APIRouter, HTTPException, Depends
from app.utils import ResponseFormatter
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

router = APIRouter()

@router.post("/chat")
async def chat(req: dict, db: AsyncSession = Depends(get_db)):
    message = req.get("message", "")
    if not message:
        return ResponseFormatter.create_error("Message is required", status_code=400)
    
    try:
        from app.models import SOPDocument
        from sqlalchemy import select
        sop_result = await db.execute( 
            select(SOPDocument).order_by( 
                SOPDocument.uploaded_at.desc() 
            ).limit(1) 
        ) 
        sop = sop_result.scalar_one_or_none() 
        context = ""
        if sop:
            context = f"\n\nContext from SOP: {sop.content[:1000]}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": f"You are a credit assistant for CreditDataWatch. {context}\n\nUser: {message}",
                    "stream": False
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                ai_response = response.json().get("response", "")
                return ResponseFormatter.create_success(data={"reply": ai_response})
            else:
                return ResponseFormatter.create_success(data={"reply": "I am having trouble connecting to my AI core right now. How else can I help?"})
                
    except httpx.ConnectError:
        return ResponseFormatter.create_success(data={"reply": "Ollama is not running. Please start Ollama on localhost:11434 to enable AI chat."})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseFormatter.create_success(data={"reply": f"An unexpected error occurred in the chat system: {str(e)}"})

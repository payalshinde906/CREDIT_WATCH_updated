from fastapi import APIRouter, HTTPException, Depends
from app.utils import ResponseFormatter
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

router = APIRouter()

@router.post("/chat")
async def chat(req: dict, db: AsyncSession = Depends(get_db)):
    """Chat with AI assistant"""
    message = req.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    # Load SOP from database 
    from app.models import SOPDocument 
    from sqlalchemy import select 
    
    sop_result = await db.execute( 
        select(SOPDocument).order_by( 
            SOPDocument.uploaded_at.desc() 
        ).limit(1) 
    ) 
    sop = sop_result.scalar_one_or_none() 
    sop_context = "" 
    if sop: 
        sop_context = f""" 
 
 COMPANY SOP DOCUMENT ({sop.filename}): 
 {sop.content[:8000]} 
 
 Use this SOP document to answer 
 questions when relevant. 
 """ 

    system_prompt = f"""You are the 
official AI Assistant for 
CreditDataWatch — India's Credit 
Intelligence Hub. 
 
 CRITICAL INSTRUCTION: 
 If a Company SOP document is provided 
 below, you MUST answer questions using 
 that SOP document as your PRIMARY 
 source of information. Always quote 
 or reference the SOP when answering. 
 
 ABOUT CREDITDATAWATCH: 
 CreditDataWatch is India's Business 
 Credit Management ecosystem. It helps 
 GST-registered businesses track vendor 
 payments, report defaulters, manage 
 purchase orders, and access credit 
 intelligence reports. 
 
 FEATURES: 
 - Purchase Order Management: Add, edit, 
   track and send reminders for POs 
 - Credibility Index: AI-powered vendor 
   credit scores and report cards 
 - Defaulter Reporting: Report and expose 
   non-paying vendors nationally 
 - Credit Reports: Detailed CIR reports 
 - Wallet: Manage account credits 
 - Membership Plans: Base, Royal, 
   Groups, Enterprise 
 - Settlement: Resolve payment disputes 
 
 USER ROLES: 
 - MASTER_ADMIN: Full control, bypasses 
   all subscription checks 
 - COMPANY_ADMIN: Manages company 
   users and settings 
 - FINANCE: Manages financial aspects 
 - LEGAL: Manages legal aspects 
 - OPERATIONS: Manages operational 
 - USER: Basic user access 
 
 RULES: 
 1. Always answer from SOP document first 
 2. If answer is in SOP — quote it directly 
 3. Give numbered step by step answers 
 4. Only answer CreditDataWatch questions 
 5. If unrelated question — politely redirect 
 """ 
    system_prompt = system_prompt + sop_context + """ 
 
 REMINDER: Use the SOP document above 
 as your PRIMARY source. Quote directly 
 from it when answering questions. 
 """ 

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": f"{system_prompt}\n\n**Question:** {message}\n\n**Answer:**",
                    "stream": False
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            reply = data.get("response", "").strip()
            # Format response as numbered steps
            reply = "\n".join(f"{i+1}. {line}" for i, line in enumerate(reply.split("\n")))
            return ResponseFormatter.create_success(data={"reply": reply})
    except httpx.RequestError:
        return ResponseFormatter.create_success(data={"reply": "I am currently unavailable. Please try again later."})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

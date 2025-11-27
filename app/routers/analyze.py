import base64
import json
from datetime import datetime, date
from typing import Generic, TypeVar, Literal, Optional
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from openai import OpenAI
import google.generativeai as genai
from app.core.config import OPENAI_TOKEN, GEMINI_TOKEN
from app.db.mongo import get_database
from app.models.analysis import Analysis

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    status: bool
    message: str
    data: Optional[T] = None

class ErrorResponse(BaseModel):
    status: bool
    message: str

router = APIRouter(prefix="/analyze", tags=["Analysis"])


async def check_and_get_usage_limit(db, model: str):
    """
    Check if the model usage is within limit for today.
    
    Args:
        db: Database instance
        model: Model type ('JR' or 'SR')
    
    Returns:
        Usage limit document if within limit
    
    Raises:
        HTTPException if usage limit exceeded
    """
    collection = db["UsageLimit"]
    today_str = date.today().strftime("%d-%m-%Y")
    print(today_str)
    
    try:
        usage_doc = await collection.find_one({"date": today_str})
        
        if model == 'JR':
            jr_used = usage_doc.get("jrUsed", 0)
            jr_limit = usage_doc.get("jrLimit", 0)
            if jr_used >= jr_limit:
                raise HTTPException(
                    status_code=429,
                    detail="JR model usage limit exceeded for today"
                )
        elif model == 'SR':
            sr_used = usage_doc.get("srUsed", 0)
            sr_limit = usage_doc.get("srLimit", 0)
            if sr_used >= sr_limit:
                raise HTTPException(
                    status_code=429,
                    detail="SR model usage limit exceeded for today"
                )
        
        return usage_doc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Usage limit check failed: {str(exc)}"
        )


async def increment_usage_count(db, model: str):
    """
    Increment the usage count for the model in UsageLimit collection.
    
    Args:
        db: Database instance
        model: Model type ('JR' or 'SR')
    """
    collection = db["UsageLimit"]
    today_str = date.today().strftime("%d-%m-%Y")
    
    try:
        if model == 'JR':
            await collection.update_one(
                {"date": today_str},
                {"$inc": {"jrUsed": 1}}
            )
        elif model == 'SR':
            await collection.update_one(
                {"date": today_str},
                {"$inc": {"srUsed": 1}}
            )
    except Exception as exc:
        print(f"Warning: Failed to increment usage count: {str(exc)}")


async def call_openai_analysis(image_base64: str, organ: str, clinical_context: str) -> dict:
    """
    Call OpenAI GPT-4o-mini to analyze the slide image.
    
    Returns:
        dict with keys: observation, preliminaryDiagnosis, confidenceLevel, disclaimer
    """
    client = OpenAI(api_key=OPENAI_TOKEN)
    
    prompt = f"""Analyze this pathology slide image and provide a medical assessment.

Organ: {organ}
Clinical Context: {clinical_context}

Please provide your analysis in the following JSON format:
{{
    "observation": "Your detailed observations about the slide",
    "preliminaryDiagnosis": "Your preliminary diagnosis based on the slide",
    "confidenceLevel": "Low/Medium/High",
    "disclaimer": "Medical disclaimer about the analysis"
}}

Important: Return ONLY valid JSON, no additional text."""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=1024
    )
    response_text = response.choices[0].message.content

    # ---- CLEAN THE RESPONSE ----
    clean_text = response_text.strip()

    if clean_text.startswith("```"):
        clean_text = clean_text.replace("```json", "")
        clean_text = clean_text.replace("```", "")
        clean_text = clean_text.strip()

    print("CLEANED RESPONSE:", clean_text)

    # ---- PARSE JSON ----
    result = json.loads(clean_text)
    return result

async def call_gemini_25_pro_analysis(image_base64: str, organ: str, clinical_context: str) -> dict:
    """
    Call Google Gemini 2.5 Pro to analyze the slide image.
    
    Returns:
        dict with keys: observation, preliminaryDiagnosis, confidenceLevel, disclaimer
    """
    genai.configure(api_key=GEMINI_TOKEN)
    
    prompt = f"""Analyze this pathology slide image and provide a medical assessment.

Organ: {organ}
Clinical Context: {clinical_context}

Please provide your analysis in the following JSON format:
{{
    "observation": "Your detailed observations about the slide",
    "preliminaryDiagnosis": "Your preliminary diagnosis based on the slide",
    "confidenceLevel": "Low/Medium/High",
    "disclaimer": "Medical disclaimer about the analysis"
}}

Important: Return ONLY valid JSON, no additional text."""
    
    image_data = base64.b64decode(image_base64)
    
    model = genai.GenerativeModel("gemini-2.5-pro")
    
    response = model.generate_content([
        prompt,
        {"mime_type": "image/jpeg", "data": image_data}
    ])
    
    response_text = response.text
    # result = json.loads(response_text)
        # ---- CLEAN THE RESPONSE ----
    clean_text = response_text.strip()

    if clean_text.startswith("```"):
        clean_text = clean_text.replace("```json", "")
        clean_text = clean_text.replace("```", "")
        clean_text = clean_text.strip()

    print("CLEANED RESPONSE:", clean_text)

    # ---- PARSE JSON ----
    result = json.loads(clean_text)
    return result


@router.post("", response_model=ApiResponse[Analysis])
async def analyze_slide(
    slideImage: UploadFile = File(...),
    organ: str = Form(...),
    clinicalContext: str = Form(...),
    model: Literal['JR', 'SR'] = Form(...)
):
    """
    Analyze a slide image and store the analysis data.
    
    Args:
        slideImage: Image file (jpg, png, etc.)
        organ: Organ name
        clinicalContext: Clinical context for the analysis
        model: Model type ('JR' or 'SR')
    
    Returns:
        ApiResponse containing the stored Analysis document with analysis results
    """
    if slideImage is None:
        return ApiResponse(status=False, message="slideImage: Field required")

    if organ is None:
        return ApiResponse(status=False, message="organ: Field required")

    if clinicalContext is None:
        return ApiResponse(status=False, message="clinicalContext: Field required")

    if model is None:
        return ApiResponse(status=False, message="model: Field required")
    
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database client not initialized")
    
    await check_and_get_usage_limit(db, model)
    
    collection = db["Analysis"]
    
    try:
        file_content = await slideImage.read()
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        
        analysis_doc = {
            "slideImage": image_base64,
            "organ": organ,
            "clinicalContext": clinicalContext,
            "model": model,
            "createdAt": datetime.utcnow()
        }
        
        if model == 'JR':
            result_data = await call_openai_analysis(image_base64, organ, clinicalContext)
            analysis_doc.update({
                "observation": result_data.get("observation"),
                "preliminaryDiagnosis": result_data.get("preliminaryDiagnosis"),
                "confidenceLevel": result_data.get("confidenceLevel"),
                "disclaimer": result_data.get("disclaimer")
            })
        elif model == 'SR':
            result_data = await call_gemini_25_pro_analysis(image_base64, organ, clinicalContext)
            analysis_doc.update({
                "observation": result_data.get("observation"),
                "preliminaryDiagnosis": result_data.get("preliminaryDiagnosis"),
                "confidenceLevel": result_data.get("confidenceLevel"),
                "disclaimer": result_data.get("disclaimer")
            })
        
        result = await collection.insert_one(analysis_doc)
        
        analysis_doc["id"] = str(result.inserted_id)
        
        await increment_usage_count(db, model)
        
        return ApiResponse(
            status=True,
            message="Analysis stored successfully",
            data=Analysis(**analysis_doc)
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(exc)}")

"""
Vision API endpoint - Secure proxy for Gemini Vision API.
Protects API key from frontend exposure with rate limiting.
"""

from fastapi import APIRouter, HTTPException, Request, File, UploadFile
from pydantic import BaseModel, Field
import httpx
import json
import re

from app.core.config import get_settings
from app.core.rate_limiter import rate_limiter

router = APIRouter()
settings = get_settings()


class VisionAnalysisRequest(BaseModel):
    """Request model for food image analysis."""
    image: str = Field(..., description="Base64 encoded image data")


class FoodItem(BaseModel):
    """Individual food item in analysis."""
    name: str
    name_hindi: str = ""
    calories: int
    protein: float = 0
    carbs: float = 0
    fat: float = 0


class VisionAnalysisResponse(BaseModel):
    """Response model for food image analysis."""
    success: bool
    foods: list = []
    total_calories: int = 0
    total_protein: float = 0
    total_carbs: float = 0
    total_fat: float = 0
    health_tips: list = []
    rate_limit_remaining: int = 5


FOOD_ANALYSIS_PROMPT = """Analyze this Indian food image and provide nutritional information.

Return ONLY valid JSON in this exact format (no markdown, no explanation):
{
  "foods": [
    {"name": "Food Name", "name_hindi": "Hindi Name", "calories": 200, "protein": 10, "carbs": 25, "fat": 8}
  ],
  "total_calories": 500,
  "total_protein": 20,
  "total_carbs": 60,
  "total_fat": 15,
  "health_tips": ["Tip 1", "Tip 2"]
}

Focus on:
- Accurate calorie estimation for Indian portions
- Include Hindi names where applicable
- Provide practical health tips"""


@router.post("/analyze-food", response_model=VisionAnalysisResponse)
async def analyze_food_image(request: VisionAnalysisRequest, http_request: Request):
    """
    Analyze food image using Gemini Vision API.
    
    Rate Limited: 5 requests per hour per IP address.
    This protects the Gemini API key from abuse.
    """
    
    # Get client IP for rate limiting
    client_ip = http_request.client.host if http_request.client else "unknown"
    rate_key = f"vision:{client_ip}"
    
    # Check rate limit (5 per hour)
    if not rate_limiter.allow(rate_key, limit=5, window_seconds=3600):
        remaining = rate_limiter.get_remaining(rate_key, limit=5)
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": "You can analyze up to 5 images per hour. Please try again later.",
                "remaining": remaining
            }
        )
    
    # Validate image data
    if not request.image:
        raise HTTPException(status_code=400, detail="Image data is required")
    
    # Check image size (max 5MB base64 ≈ 6.7MB)
    if len(request.image) > 7_000_000:
        raise HTTPException(status_code=400, detail="Image too large. Maximum 5MB allowed.")
    
    # Extract base64 data (handle data URL format)
    image_data = request.image
    if "," in image_data:
        image_data = image_data.split(",")[1]
    
    # Check for Ollama Cloud service
    from app.services.ollama_service import ollama_service
    if not ollama_service.is_available:
        # Fallback to direct Gemini if Ollama Cloud fails/not configured
        if not settings.GEMINI_API_KEY:
            raise HTTPException(
                status_code=500, 
                detail="Vision API not configured. Contact support."
            )
        # (Rest of existing Gemini direct logic stays as fallback if needed)
    
    try:
        # Call Ollama Cloud Vision (Gemini 3 Flash Preview)
        result = await ollama_service.invoke(
            prompt=FOOD_ANALYSIS_PROMPT,
            model_type="vision",
            images=[image_data],
            temperature=0.2
        )
        
        if "error" in result:
             raise Exception(result["error"])
             
        text_content = result.get("response", "")
        
        # Parse JSON from response
        analysis = parse_gemini_json(text_content)
        
        # Get remaining rate limit
        remaining = rate_limiter.get_remaining(rate_key, limit=5)
        
        return VisionAnalysisResponse(
            success=True,
            foods=analysis.get("foods", []),
            total_calories=analysis.get("total_calories", 0),
            total_protein=analysis.get("total_protein", 0),
            total_carbs=analysis.get("total_carbs", 0),
            total_fat=analysis.get("total_fat", 0),
            health_tips=analysis.get("health_tips", []),
            rate_limit_remaining=remaining
        )
        
        # Parse JSON from response
        analysis = parse_gemini_json(text_content)
        
        # Get remaining rate limit
        remaining = rate_limiter.get_remaining(rate_key, limit=5)
        
        return VisionAnalysisResponse(
            success=True,
            foods=analysis.get("foods", []),
            total_calories=analysis.get("total_calories", 0),
            total_protein=analysis.get("total_protein", 0),
            total_carbs=analysis.get("total_carbs", 0),
            total_fat=analysis.get("total_fat", 0),
            health_tips=analysis.get("health_tips", []),
            rate_limit_remaining=remaining
        )
        
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Analysis timed out. Please try again."
        )
    except HTTPException:
        raise
    except Exception as e:
        # Log error for debugging (visible in Render logs)
        print(f"[VEDA-ERROR] Vision analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze image. Please try again."
        )


def parse_gemini_json(text: str) -> dict:
    """
    Parse JSON from Gemini response text.
    Handles markdown code blocks and malformed JSON.
    """
    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    
    try:
        # Try direct JSON parse
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON object
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            json_str = text[start:end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Return empty structure if parsing fails
    return {
        "foods": [],
        "total_calories": 0,
        "health_tips": ["Unable to analyze this image. Please try a clearer photo."]
    }


@router.get("/rate-limit-status")
async def get_rate_limit_status(http_request: Request):
    """
    Check current rate limit status for this IP.
    Useful for showing remaining analyses in UI.
    """
    client_ip = http_request.client.host if http_request.client else "unknown"
    rate_key = f"vision:{client_ip}"
    remaining = rate_limiter.get_remaining(rate_key, limit=5)
    
    return {
        "limit": 5,
        "remaining": remaining,
        "window_hours": 1,
        "message": f"You can analyze {remaining} more images this hour."
    }


@router.post("/analyze-video")
async def analyze_video(file: UploadFile = File(...), http_request: Request = None):
    """
    Analyze short video clips for wellness/activity/food using Gemini.
    Max size: 10MB (Short clips only)
    """
    from app.services.gemini import gemini_service
    
    # helper for rate limit (share with vision)
    client_ip = http_request.client.host if (http_request and http_request.client) else "unknown"
    rate_key = f"vision:{client_ip}"
    
    if not rate_limiter.allow(rate_key, limit=5, window_seconds=3600):
        remaining = rate_limiter.get_remaining(rate_key, limit=5)
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
    # Check mime type
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a video.")
        
    # Read file (check size manually by reading chunks or just read all if small)
    # Warning: reading all into memory. 10MB Limit enforced.
    contents = await file.read()
    
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Video too large. Max 10MB allowed.")
        
    prompt = """Analyze this video. Identify:
1. Main activity or subject (Yoga, Workout, Cooking, Recipe)
2. If food: Estimated calories and ingredients.
3. If exercise: Form check and estimated burn.
4. Summary of what is happening.

Format as JSON: { "activity": "...", "details": "...", "calories_or_burn": "..." }"""

    result = await gemini_service.analyze_multimodal(prompt, contents, file.content_type)
    
    return {"analysis": result}

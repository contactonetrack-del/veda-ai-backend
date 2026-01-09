from fastapi import APIRouter, HTTPException, Depends
from app.schemas.auth import LoginRequest, SignupRequest, Token
from app.core.database import supabase
from app.schemas.user import UserResponse

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
async def signup(request: SignupRequest):
    try:
        # Sign up with Supabase
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.name
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Signup failed")
            
        # The trigger will create the user record in 'users' table
        # We fetch it to return confirm
        user_data = supabase.table("users").select("*").eq("id", auth_response.user.id).execute()
        
        if user_data.data:
             return user_data.data[0]
        
        # Fallback if trigger hasn't run yet (rare race condition)
        return {
            "id": auth_response.user.id,
            "email": request.email,
            "name": request.name,
            "auth_provider": "email",
            "is_guest": False,
            "created_at": auth_response.user.created_at
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.session:
             raise HTTPException(status_code=401, detail="Invalid credentials")
             
        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer",
            "refresh_token": auth_response.session.refresh_token,
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email
            }
        }
    except Exception as e:
         raise HTTPException(status_code=400, detail=str(e))

@router.post("/guest")
async def guest_login():
    # For guest, we might just create an anonymous user in Supabase
    # Or handle it purely logic-side. 
    # VEDA Strategy: "Guest" is a boolean flag user in DB with a random email?
    # Or use Supabase Anonymous Sign in if enabled.
    # For now, simpler: Return a generated 'guest' token structure that frontend trusts, 
    # or rely on Supabase logic.
    # Let's assume we want to track them in DB.
    pass

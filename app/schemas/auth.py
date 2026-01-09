from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None
    user: dict  # Simplified user object

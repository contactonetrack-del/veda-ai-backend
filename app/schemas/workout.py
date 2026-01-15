from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WorkoutBase(BaseModel):
    name: str
    duration: int
    notes: Optional[str] = None

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutUpdate(BaseModel):
    name: Optional[str] = None
    duration: Optional[int] = None
    notes: Optional[str] = None

class Workout(WorkoutBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

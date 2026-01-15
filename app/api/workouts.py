from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.workout import Workout, WorkoutCreate
from app.core.database import supabase
import uuid
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[Workout])
async def get_workouts(user_id: str):
    try:
        response = supabase.table("workouts") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=Workout)
async def create_workout(workout: WorkoutCreate, user_id: str):
    try:
        new_workout = {
            "id": str(uuid.uuid4()),
            "name": workout.name,
            "duration": workout.duration,
            "notes": workout.notes,
            "user_id": user_id,
            "created_at": datetime.now().isoformat()
        }
        
        response = supabase.table("workouts") \
            .insert(new_workout) \
            .execute()
            
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create workout")
            
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

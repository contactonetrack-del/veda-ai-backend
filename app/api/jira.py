from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.jira_service import jira_service

router = APIRouter(prefix="/jira", tags=["Jira"])

class IssueCreate(BaseModel):
    summary: str
    description: str = ""
    issue_type: str = "Task"

@router.get("/context")
async def get_project_context():
    """Get high-level project context for the AI"""
    if not jira_service.available:
        return {"error": "Jira Service Unavailable"}
    return {"context": jira_service.get_project_context()}

@router.post("/issue")
async def create_issue(issue: IssueCreate):
    """Create a Jira issue"""
    if not jira_service.available:
        raise HTTPException(status_code=503, detail="Jira Service Unavailable")
    
    result = jira_service.create_issue(
        summary=issue.summary,
        description=issue.description,
        issue_type=issue.issue_type
    )
    
    if "Error" in result or "Failed" in result:
        raise HTTPException(status_code=500, detail=result)
        
    return {"status": "success", "message": result}

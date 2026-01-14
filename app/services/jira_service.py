from jira import JIRA
from app.core.config import get_settings

settings = get_settings()

class JiraService:
    def __init__(self):
        self.client = None
        self.available = False
        self._connect()
        
    def _connect(self):
        try:
            if settings.JIRA_API_TOKEN and settings.JIRA_HOST:
                self.client = JIRA(
                    server=settings.JIRA_HOST,
                    basic_auth=(settings.JIRA_USER_EMAIL, settings.JIRA_API_TOKEN)
                )
                self.available = True
                print("Jira Service Connected")
            else:
                print("Jira Service disabled (Missing Config)")
        except Exception as e:
            print(f"Jira Connection Failed: {e}")
            self.available = False

    def get_project_context(self) -> str:
        """Fetch high-level project stats for context injection"""
        if not self.available:
            return "Jira Data Unavailable"
            
        try:
            # Get Sprint Status
            query = f'project = {settings.JIRA_PROJECT_KEY} AND sprint in openSprints()'
            issues = self.client.search_issues(query)
            
            done = sum(1 for i in issues if i.fields.status.name == "Done")
            total = len(issues)
            progress = round(done / total * 100) if total > 0 else 0
            
            # Simple summarization
            context = f"CURRENT SPRINT STATUS:\n"
            context += f"- Progress: {done}/{total} tasks completed ({progress}%)\n"
            context += f"- Active Issues: {total - done}\n"
            
            # List top 5 incomplete items
            context += "\nTOP PRIORITY ISSUES:\n"
            incomplete = [i for i in issues if i.fields.status.name != "Done"]
            for i in incomplete[:5]:
                context += f"- [{i.key}] {i.fields.summary} ({i.fields.status.name})\n"
                
            return context
        except Exception as e:
            return f"Error fetching Jira context: {str(e)}"

    def create_issue(self, summary: str, description: str = "", issue_type: str = "Task") -> str:
        """Create a new issue in Jira"""
        if not self.available:
            return "Error: Jira Service Unavailable"
            
        try:
            # Default to 'Task' if type is invalid/empty
            valid_types = ["Task", "Bug", "Epic", "Story"]
            if issue_type not in valid_types:
                issue_type = "Task"

            issue = self.client.create_issue(
                fields={
                    "project": {"key": settings.JIRA_PROJECT_KEY},
                    "summary": summary,
                    "description": description,
                    "issuetype": {"name": issue_type},
                }
            )
            return f"Successfully created {issue_type}: {issue.key} - {summary}"
        except Exception as e:
            return f"Failed to create issue: {str(e)}"

# Singleton
jira_service = JiraService()

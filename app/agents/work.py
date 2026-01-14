"""
Work Agent
Handles enterprise integrations like Jira and Slack
"""
from typing import Dict, Any
import re
from app.agents.base import BaseAgent
from app.services.jira_service import jira_service
from app.services.slack_service import slack_service

class WorkAgent(BaseAgent):
    """Agent that handles enterprise work tasks (Jira, Slack)"""
    
    def __init__(self):
        super().__init__(
            name="Work Assistant",
            description="Handles enterprise tasks like Jira tickets and Slack messages",
            system_prompt="""You are an enterprise work assistant.
Your goal is to help the user manage their work by interacting with tools like Jira and Slack.

Supported Actions:
1. Create Jira Issue: "create ticket", "new bug", "add task"
   - format: ACTION: jira_create, PARAMS: summary="...", type="...", description="..."

2. Get Jira Context: "sprint status", "jira update", "what's pending"
   - format: ACTION: jira_context, PARAMS: none

3. Send Slack Message: "send message to #general", "slack to channel"
   - format: ACTION: slack_send, PARAMS: channel="...", message="..."

Analyze the user's request and output the action.

Examples:
"Create a bug for login failure" → ACTION: jira_create, PARAMS: summary="Login failure", type="Bug", description="User cannot login"
"Add a task to update docs" → ACTION: jira_create, PARAMS: summary="Update docs", type="Task", description=""
"What's the status of the sprint?" → ACTION: jira_context, PARAMS: none
"Post to general that deployment is done" → ACTION: slack_send, PARAMS: channel="general", message="Deployment is done"
"""
        )
    
    async def process(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Parse request, execute tool, and return results"""
        
        # Use Gemini to parse the request
        parse_result = await self.generate(user_message)
        
        # Extract action and params
        action, params = self._parse_response(parse_result)
        
        if not action:
            return {
                "agent": self.name,
                "response": "I didn't understand the work request. Try 'Create a Jira task for X' or 'Send Slack message to #channel'.",
                "intent": "work",
                "success": False
            }
        
        try:
            if action == "jira_create":
                summary = params.get("summary", "New Task")
                issue_type = params.get("type", "Task")
                description = params.get("description", "")
                
                result = jira_service.create_issue(summary, description, issue_type)
                
            elif action == "jira_context":
                result = jira_service.get_project_context()
                
            elif action == "slack_send":
                channel = params.get("channel", "general")
                # Remove # if present
                if channel.startswith("#"):
                    channel = channel[1:]
                message = params.get("message", "")
                
                result = slack_service.send_message(channel, message)
                
            else:
                result = f"Unknown action: {action}"
            
            return {
                "agent": self.name,
                "response": result,
                "intent": "work",
                "success": True,
                "data": result
            }
            
        except Exception as e:
            return {
                "agent": self.name,
                "response": f"Error executing work task: {str(e)}",
                "intent": "work",
                "success": False
            }

    def _parse_response(self, response: str) -> tuple:
        """Extract action and params from response"""
        action = None
        params = {}
        
        # Look for ACTION: pattern
        action_match = re.search(r'ACTION:\s*([a-zA-Z_]+)', response, re.IGNORECASE)
        if action_match:
            action = action_match.group(1).lower()
        
        # Look for PARAMS: pattern
        params_match = re.search(r'PARAMS:\s*(.+)', response, re.IGNORECASE | re.DOTALL)
        if params_match:
            params_str = params_match.group(1)
            # Simple regex parser for key="value" or key=value
            # This is a bit naive but works for simple cases. 
            # For robust parsing, we'd need a better structured output or JSON.
            # Let's try to parse key="value"
            
            # extract summary="value"
            for key in ["summary", "type", "description", "channel", "message"]:
                # Matches key="value" or key=value
                # We need to be careful about not capturing too much
                match = re.search(f'{key}="([^"]+)"', params_str)
                if match:
                    params[key] = match.group(1)
                else:
                    # Try without quotes
                    match = re.search(f'{key}=([^,\n]+)', params_str)
                    if match:
                        params[key] = match.group(1).strip()

        return action, params

# Singleton
work_agent = WorkAgent()

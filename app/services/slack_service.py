from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from app.core.config import get_settings

settings = get_settings()

class SlackService:
    def __init__(self):
        self.client = None
        self.available = False
        self._connect()
        
    def _connect(self):
        try:
            # Check for generic SLACK_BOT_TOKEN
            token = getattr(settings, 'SLACK_BOT_TOKEN', None)
            
            if token:
                self.client = WebClient(token=token)
                self.available = True
                print("Slack Service Connected")
            else:
                print("Slack Service disabled (Missing Config)")
        except Exception as e:
            print(f"Slack Connection Failed: {e}")
            self.available = False

    def send_message(self, channel: str, text: str) -> str:
        """Send a message to a Slack channel"""
        if not self.available:
            return "Error: Slack Service Unavailable"
            
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text
            )
            return f"Message sent to {channel}: {text}"
        except SlackApiError as e:
            return f"Failed to send Slack message: {e.response['error']}"
        except Exception as e:
            return f"Slack Error: {str(e)}"

# Singleton
slack_service = SlackService()

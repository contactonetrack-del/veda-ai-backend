import logging
from typing import Dict, Any, Optional
from app.orchestrator import orchestrator  # Assuming orchestrator handles routing

class VoiceRouterService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def route_query(self, transcript: str, language: str, user_id: str) -> Dict[str, Any]:
        """
        Routes the transcribed text to the appropriate domain expert.
        """
        try:
            self.logger.info(f"Routing query: '{transcript}' (Language: {language})")
            
            # Use the existing orchestrator to handle the reasoning and execution
            # We call process_message instead of execute
            response_data = await orchestrator.process_message(
                user_message=transcript,
                user_id=user_id
            )
            
            return {
                "response_text": response_data.get("response"),
                "language": language
            }
        except Exception as e:
            self.logger.error(f"Routing failed: {e}")
            return {"error": str(e)}

# Singleton instance
voice_router = VoiceRouterService()

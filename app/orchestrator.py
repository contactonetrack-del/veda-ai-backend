"""
Orchestrator
Main orchestration logic that coordinates all agents
Phase 1: Now includes SearchAgent for real-time web search
"""
from typing import Dict, Any, List
from app.agents.router import router_agent
from app.agents.wellness import wellness_agent
from app.agents.protection import protection_agent
from app.agents.general import general_agent
from app.agents.tools import tool_agent
from app.agents.search import search_agent
from app.agents.critic import critic_agent
from app.services.memory import vector_memory
from app.services.embeddings import generate_embedding


class Orchestrator:
    """
    Main orchestrator that coordinates the multi-agent system
    Flow: Router → Specialist Agent → Critic → Response
    """
    
    def __init__(self):
        self.agents = {
            "WellnessAgent": wellness_agent,
            "ProtectionAgent": protection_agent,
            "GeneralAgent": general_agent,
            "ToolAgent": tool_agent,
            "SearchAgent": search_agent
        }
    
    async def process_message(
        self, 
        user_message: str, 
        user_id: str,
        chat_id: str = None
    ) -> Dict[str, Any]:
        """
        Main entry point for processing user messages
        
        Args:
            user_message: The user's message
            user_id: Unique user identifier for memory isolation
            chat_id: Optional chat ID for logging
        
        Returns:
            Dict with final response and metadata
        """
        
        # Step 1: Generate embedding for user message
        user_embedding = await generate_embedding(user_message)
        
        # Step 2: Retrieve relevant context from memory
        memory_context = await vector_memory.search_context(
            user_id=user_id,
            query_embedding=user_embedding,
            top_k=3
        )
        
        # Step 3: Route to appropriate agent
        routing = await router_agent.process(user_message)
        intent = routing.get("intent", "general")
        agent_name = routing.get("route_to", "GeneralAgent")
        
        # Step 4: Get specialist agent and process
        agent = self.agents.get(agent_name, general_agent)
        
        context = {
            "memory": memory_context,
            "user_id": user_id,
            "chat_id": chat_id
        }
        
        agent_result = await agent.process(user_message, context)
        draft_response = agent_result.get("response", "I'm not sure how to help with that.")
        
        # Step 5: Review with Critic (if needed)
        critic_context = {
            "draft_response": draft_response,
            "intent": intent,
            "tool_success": agent_result.get("success", True)
        }
        
        review = await critic_agent.process(user_message, critic_context)
        final_response = review.get("final_response", draft_response)
        
        # Step 6: Store messages in vector memory
        await vector_memory.add_message(
            user_id=user_id,
            message=user_message,
            role="user",
            embedding=user_embedding,
            metadata={"chat_id": chat_id, "intent": intent}
        )
        
        ai_embedding = await generate_embedding(final_response)
        await vector_memory.add_message(
            user_id=user_id,
            message=final_response,
            role="assistant",
            embedding=ai_embedding,
            metadata={"chat_id": chat_id, "agent": agent_name}
        )
        
        return {
            "response": final_response,
            "intent": intent,
            "agent_used": agent_name,
            "reviewed": review.get("approved", True),
            "context_used": len(memory_context) > 0,
            "sources": agent_result.get("sources", [])  # Phase 1: Include citations
        }


# Singleton instance
orchestrator = Orchestrator()

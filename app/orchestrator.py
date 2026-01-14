"""
Orchestrator
Main orchestration logic that coordinates all agents
Phase 1: SearchAgent for real-time web search
Phase 2: FactChecker for verification
"""
from typing import Dict, Any, List
import asyncio
from app.agents.router import router_agent
from app.agents.wellness import wellness_agent
from app.agents.protection import protection_agent
from app.agents.general import general_agent
from app.agents.tools import tool_agent
from app.agents.search import search_agent
from app.agents.critic import critic_agent
from app.agents.fact_checker import fact_checker
from app.agents.deep_research import deep_research_agent
from app.agents.data_analyst import data_analyst_agent
from app.agents.cross_verifier import cross_verifier_agent
from app.agents.study import study_agent  # Phase 5: Study Mode
from app.services.memory import vector_memory
from app.services.history import history_service
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
            "SearchAgent": search_agent,
            "DeepResearchAgent": deep_research_agent,
            "DataAnalystAgent": data_analyst_agent,
            "StudyAgent": study_agent  # Phase 5: Study Mode
        }
    
    async def process_message(
        self, 
        user_message: str, 
        user_id: str,
        chat_id: str = None,
        verify_facts: bool = True,
        force_agent: str = None  # Phase 5: Force specific agent (bypasses Router)
    ) -> Dict[str, Any]:
        """
        Main entry point for processing user messages
        
        Args:
            user_message: The user's message
            user_id: Unique user identifier for memory isolation
            chat_id: Optional chat ID for logging
            verify_facts: Whether to run fact-checking (Phase 2)
            force_agent: Force a specific agent (bypasses Router) (Phase 5)
        
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
        
        # Step 2.5: Retrieve short-term history
        short_term_history = history_service.get_recent_messages(user_id)
        
        # Save User Message to History
        history_service.add_message(user_id, "user", user_message)
        
        # Step 3: Route to appropriate agent
        # Phase 5: If force_agent is specified, use it directly
        if force_agent and force_agent in self.agents:
            agent_name = force_agent
            intent = "research" if force_agent == "DeepResearchAgent" else "analysis"
        else:
            # OPTIMIZATION: Fast Path for greetings/short messages
            msg_lower = user_message.strip().lower()
            greetings = ["hi", "hello", "hey", "namaste", "pranam", "greetings", "good morning", "good evening"]
            
            # Fast Path 1: Greetings
            if msg_lower in greetings:
                intent = "general"
                agent_name = "GeneralAgent"
            
            # Fast Path 2: Obvious Tool/Calculations
            elif any(x in msg_lower for x in ["calculate", "bmi", "premium", "cost", "price", "sum", "multiply"]):
                # Simple keyword check for tools, but let router confirm complex ones if needed
                # For now, let's keep it handled by router mostly, or force if very obvious
                # Putting price/cost here might overlap with search, so be careful.
                # "calculate bmi" is definitely tool
                 if "bmi" in msg_lower or "calculate" in msg_lower:
                    intent = "tool"
                    agent_name = "ToolAgent"
                 else:
                     # Fallthrough
                     intent = None

            # Fast Path 3: Obvious Search/News
            # "price of", "cost of" usually implies search unless it's "premium estimate" (handled by tool)
            elif any(x in msg_lower for x in ["latest", "news", "current", "today", "weather", "who is", "what is", "price of", "cost of", "vs", "versus"]):
                 # Exclude "what is your name" type questions
                 if "your" not in msg_lower and "you" not in msg_lower:
                    print(f"[Orchestrator] Fast-tracking to SearchAgent: {msg_lower[:30]}...")
                    intent = "search"
                    agent_name = "SearchAgent" 
                 else:
                     intent = None
            
            else:
                intent = None

            # Fallback to LLM Router if no fast path matched
            if not intent:
                routing = await router_agent.process(user_message)
                intent = routing.get("intent", "general")
                agent_name = routing.get("route_to", "GeneralAgent")
        
        # Step 4: Get specialist agent and process
        agent = self.agents.get(agent_name, general_agent)
        
        context = {
            "memory": memory_context,
            "history": short_term_history,
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
        
        review = {}
        # OPTIMIZATION: Skip Critic for 'general' and 'tool' intents (low risk)
        if intent not in ["general", "tool"]:
            review = await critic_agent.process(user_message, critic_context)
        
        final_response = review.get("final_response", draft_response)
        
        # Step 5.2: Cross-Verification (The "Judge") for high-stakes topics
        if intent in ["wellness", "protection", "research"]:
            cross_check = await cross_verifier_agent.process(
                final_response,
                context={
                    "original_query": user_message,
                    "provider_used": agent_result.get("provider", "unknown")
                }
            )
            if not cross_check.get("verified", True):
                print(f"[Orchestrator] Cross-Verifier intervened.")
                final_response = cross_check.get("response", final_response)
        
        # Step 5.5: Fact-check if enabled (Phase 2)
        # OPTIMIZATION: Skip Fact-Check for 'general' intent
        verification_result = None
        if verify_facts and intent in ["search", "wellness"]:
            try:
                verification_result = await fact_checker.process(
                    final_response,
                    context={
                        "original_query": user_message,
                        "sources": agent_result.get("sources", [])
                    }
                )
                if verification_result.get("verified"):
                    final_response = verification_result.get("verified_response", final_response)
            except Exception as e:
                print(f"[Orchestrator] Fact-check error: {e}")
        
        # Save AI Response to History
        history_service.add_message(user_id, "assistant", final_response)
        
        # Background: Store in Vector Memory (Fire and forget)
        asyncio.create_task(self._save_conversation_background(
            user_id=user_id,
            user_message=user_message,
            user_embedding=user_embedding,
            final_response=final_response,
            agent_name=agent_name,
            intent=intent,
            chat_id=chat_id
        ))
        
        return {
            "response": final_response,
            "intent": intent,
            "agent_used": agent_name,
            "reviewed": review.get("approved", True),
            "context_used": len(memory_context) > 0,
            "sources": agent_result.get("sources", []),  # Phase 1: Include citations
            "verified": verification_result.get("verified", False) if verification_result else False,
            "confidence": verification_result.get("confidence", 0.0) if verification_result else 0.0
        }

    async def _save_conversation_background(
        self, 
        user_id: str, 
        user_message: str, 
        user_embedding: List[float], 
        final_response: str, 
        agent_name: str, 
        intent: str, 
        chat_id: str
    ):
        """
        Background task to save conversation to vector memory.
        This runs after the response is sent to the user to reduce latency.
        """
        try:
            # 1. Store User Message
            await vector_memory.add_message(
                user_id=user_id,
                message=user_message,
                role="user",
                embedding=user_embedding,
                metadata={"chat_id": chat_id, "intent": intent}
            )
            
            # 2. Generate Assistant Embedding
            ai_embedding = await generate_embedding(final_response)
            
            # 3. Store Assistant Message
            await vector_memory.add_message(
                user_id=user_id,
                message=final_response,
                role="assistant",
                embedding=ai_embedding,
                metadata={"chat_id": chat_id, "agent": agent_name}
            )
        except Exception as e:
            print(f"[Orchestrator] Background save error: {e}")


# Singleton instance
orchestrator = Orchestrator()

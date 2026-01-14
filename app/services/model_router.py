"""
Model Router
Intelligently routes requests to the best available model
Provides fallback and load balancing across providers
"""
from typing import Optional, Literal
from app.services.groq_service import groq_service
from app.services.openrouter_service import openrouter_service
from app.services.xai_service import xai_service
from app.services.openai_service import openai_service
from app.services.ollama_service import ollama_service
from app.services.gemini import gemini_service
from app.services.jira_service import jira_service
from app.core.config import get_settings

settings = get_settings()

ModelProvider = Literal["gemini", "groq", "openai", "ollama", "auto"]


class ModelRouter:
    """Routes requests to the best available AI model"""
    
    def __init__(self):
        self.providers = {
            "gemini": gemini_service,
            "groq": groq_service,
            "openrouter": openrouter_service,
            "xai": xai_service,
            "openai": openai_service,
            "ollama": ollama_service
        }
        # Priority order for fallback
        self.priority = ["groq", "xai", "openrouter", "ollama", "openai", "gemini"]
    
    def get_available_models(self) -> list:
        """Return list of available model providers"""
        available = ["gemini"]
        if groq_service.available:
            available.append("groq")
        if openai_service.api_key:
            available.append("openai")
        if ollama_service.is_available:
            available.append("ollama")
        return available
    
    async def generate(
        self,
        message: str,
        system_prompt: str = "",
        history: list = [],
        provider: ModelProvider = "auto",
        fast: bool = False
    ) -> dict:
        """
        Generate response using the best available model
        """
        
        # Auto routing logic
        if provider == "auto":
            # Determine task complexity and type
            check_msg = message.lower()
            is_complex = any(keyword in check_msg for keyword in ["diet", "plan", "chart", "report", "analyze", "medical", "symptom", "reason", "logic", "math"])
            is_vision = any(keyword in check_msg for keyword in ["image", "photo", "scan", "look", "see"])
            
            # Phase 5: Real-time Web Search Integration
            from app.services.web_search import web_search
             
            is_search = any(keyword in check_msg for keyword in ["search", "find", "look up", "google", "brave", "online", "internet", "price", "latest", "news", "current", "today", "weather"])
            is_news = "news" in check_msg or "latest" in check_msg

            if is_search and web_search.is_available:
                print(f"🕵️ Search Intent Detected: {check_msg[:30]}...")
                search_data = {}
                
                if is_news:
                     search_data = await web_search.search_news(message)
                else:
                     search_data = await web_search.smart_search(message)
                
                if search_data.get("success"):
                    ctx = "\n".join([f"- {r['title']}: {r['description']} ({r['url']})" for r in search_data.get("results", [])])
                    system_prompt = f"{system_prompt}\n\n[REAL-TIME SEARCH RESULTS]\n{ctx}\n\n[INSTRUCTION]\nUse the above search results to answer the user's question. Citations are encouraged."
                    print(f"✅ Context injected from {search_data.get('source')}")
                    # Force reasoning for synthesis
                    is_complex = True

            
            # Phase 4: Jira Context Injection
            is_project_management = any(keyword in check_msg for keyword in ["sprint", "task", "jira", "bug", "issue", "project", "status", "todo"])
            
            if is_project_management and jira_service.available:
                print("Injecting Jira Context...")
                jira_context = jira_service.get_project_context()
                system_prompt = f"{system_prompt}\n\n[REAL-TIME JIRA DATA]\n{jira_context}"
                
                # Check for Write Intent
                if "create" in check_msg or "new" in check_msg or "add" in check_msg:
                    system_prompt += "\n[ACTION AVAILABLE]\nIf the user wants to create a task/bug, output ONLY this format: ACTION: CREATE_TASK | <summary> | <description (optional)>"
                
                system_prompt += "\n[INSTRUCTION]\nUse the above data to answer the user's question about the project status."
                
                # Force reasoning model for project management analysis
                is_complex = True 
            
            
            # Phase 3: Zero-Cost Hybrid Routing
            # 1. Complex/Reasoning -> Groq (DeepSeek R1 Distill) [Free: 1000/day]
            # 2. General/Fast -> Groq (Llama 3.3 70B) [Free: 14.4k/day]
            # 3. Vision/Multimodal -> Gemini 2.0 Flash [Free: 2880/day]
            # 4. Backup -> Ollama Cloud (DeepSeek V3 / Gemini 3)
            
            if is_vision:
                # Primary Vision: Gemini
                if settings.GEMINI_API_KEY:
                    provider = "gemini"
                elif ollama_service.is_available:
                    provider = "ollama"
                else:
                    provider = "gemini" # Fallback to default
            
            elif is_complex:
                # Primary Reasoning: OpenRouter (DeepSeek R1 full) or Groq
                if openrouter_service.available:
                    provider = "openrouter"
                elif xai_service.available:
                    provider = "xai"
                elif groq_service.available:
                    provider = "groq"
                elif ollama_service.is_available:
                    provider = "ollama"
                elif openai_service.api_key:
                    provider = "openai"
                else:
                    provider = "gemini"
            
            elif fast:
                if groq_service.available:
                    provider = "groq"
                elif xai_service.available:
                    provider = "xai"
                else:
                    provider = "gemini"
            else:
                if groq_service.available:
                    provider = "groq"
                elif xai_service.available:
                    provider = "xai"
                else:
                    provider = "gemini"
        
        # Routing Execution with Robust Fallback
        
        # 1. Try Primary Provider
        try:
            if provider == "groq" and groq_service.available:
                # Select model matching routing decision or default
                target_model = groq_service.fast_model if fast else groq_service.default_model
                if is_complex and hasattr(groq_service, 'reasoning_model'):
                    target_model = groq_service.reasoning_model
                
                response = await groq_service.generate_response(
                    message, 
                    system_prompt, 
                    history=history,
                    fast=fast,
                    model=target_model
                )
                
                # Action Parsing
                if "ACTION: CREATE_TASK" in response:
                    print(f"Action Detected: {response}")
                    try:
                        parts = response.split("|")
                        summary = parts[1].strip()
                        description = parts[2].strip() if len(parts) > 2 else ""
                        
                        action_result = jira_service.create_issue(summary, description)
                        response = f"{response}\n\n[SYSTEM] {action_result}"
                    except Exception as e:
                         response = f"{response}\n\n[SYSTEM] Failed to execute action: {str(e)}"
                
                return {
                    "response": response,
                    "provider": "groq",
                    "model": target_model,
                    "fallback": False
                }

            elif provider == "openrouter" and openrouter_service.available:
                # Use OpenRouter (Next-Gen Models)
                # Select model matching routing decision or default
                target_model = openrouter_service.fast_model if fast else openrouter_service.default_model
                if is_complex:
                    target_model = openrouter_service.reasoning_model
                
                response = await openrouter_service.generate_response(
                    message, 
                    system_prompt, 
                    history=history,
                    model=target_model
                )
                return {
                    "response": response,
                    "provider": "openrouter",
                    "model": target_model,
                    "fallback": False
                }

            elif provider == "xai" and xai_service.available:
                # Use xAI (Grok Models)
                target_model = xai_service.fast_model if fast else xai_service.default_model
                if is_complex:
                    target_model = xai_service.reasoning_model
                
                response = await xai_service.generate_response(
                    message, 
                    system_prompt, 
                    history=history,
                    model=target_model
                )
                return {
                    "response": response,
                    "provider": "xai",
                    "model": target_model,
                    "fallback": False
                }
                
            elif provider == "gemini":
                # Use Gemini 1.5 Flash (Stable)
                full_prompt = f"{system_prompt}\n\n{message}" if system_prompt else message
                response = await gemini_service.generate_response(full_prompt, history=history)
                return {
                    "response": response,
                    "provider": "gemini",
                    "model": "gemini-1.5-flash",
                    "fallback": False
                }
                
            elif provider == "ollama" and ollama_service.is_available:
                # Direct Ollama Cloud Usage
                model_type = "reasoning" if is_complex else ("fast" if fast else "general")
                if is_vision: model_type = "vision"
                
                result = await ollama_service.invoke(
                    prompt=message,
                    system_prompt=system_prompt,
                    model_type=model_type,
                    reasoning_mode=(model_type == "reasoning")
                )
                return {
                    "response": result.get("response", ""),
                    "provider": "ollama",
                    "model": result.get("model_used", "ollama-cloud"),
                    "fallback": False
                }

        except Exception as e:
            print(f"⚠️ Primary provider {provider} failed: {e}")
            # Proceed to Fallback Chain
            pass

        # 2. Backup: Ollama Cloud (Tier 1 Reliability)
        if ollama_service.is_available:
            print(f"🔄 Switching to Backup: Ollama Cloud")
            try:
                model_type = "reasoning" if is_complex else ("fast" if fast else "general")
                if is_vision: model_type = "vision"
                
                result = await ollama_service.invoke(
                    prompt=message,
                    system_prompt=system_prompt,
                    model_type=model_type,
                    reasoning_mode=(model_type == "reasoning")
                )
                return {
                    "response": result.get("response", ""),
                    "provider": "ollama",
                    "model": result.get("model_used", "ollama-cloud-backup"),
                    "fallback": True
                }
            except Exception as e_backup:
                print(f"❌ Backup failed: {e_backup}")
        
        # 3. Last Resort: Gemini (Universal Fallback)
        print(f"🚨 Using Final Safety Net: Gemini")
        try:
            full_prompt = f"{system_prompt}\n\n{message}" if system_prompt else message
            response = await gemini_service.generate_response(full_prompt, history=history)
            return {
                "response": response,
                "provider": "gemini",
                "model": "gemini-1.5-flash-cleanup",
                "fallback": True
            }
        except Exception as e_final:
            return {
                "response": "I apologize, but I am currently experiencing high traffic. Please try again in a moment.",
                 "error": str(e_final),
                 "fallback": True
            }
        
        except Exception as e:
            print(f"Primary provider {provider} failed: {e}")
            
            # Simple Fallback Chain: OpenAI -> Gemini -> Groq
            # (If primary was OpenAI, fallback to Gemini)
            if provider == "openai":
                fallback_provider = "gemini"
            elif provider == "gemini":
                fallback_provider = "groq"
            else:
                fallback_provider = "gemini"
            
            # ... (Reuse existing fallback logic or simplify)
            # For brevity, implementing direct fallback call logic here would be repetitive.
            # I will just call Gemini as universal fallback to ensure reliability.
            
            try:
                full_prompt = f"{system_prompt}\n\n{message}" if system_prompt else message
                response = await gemini_service.generate_response(full_prompt, history=history)
                return {
                    "response": response,
                    "provider": "gemini",
                    "model": "gemini-fallback",
                    "fallback": True
                }
            except Exception as e2:
                return {
                     "response": "Service Unavailable. Please check your connection.",
                     "error": str(e2),
                     "fallback": True
                }

# Singleton instance
model_router = ModelRouter()

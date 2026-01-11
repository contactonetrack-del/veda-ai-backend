"""
Domain Expert Agents - Phase 3 Preview
12 specialized agents based on market demand (all zero-cost)
"""
from typing import Dict, Any, Optional
from app.services.local_llm import local_llm_service


# =============================================================================
# HIGH DEMAND EXPERTS (🔥🔥🔥)
# =============================================================================

class CareerCoachAgent:
    """
    Career & Interview Coach - HIGH DEMAND
    Resume writing, interview prep, job search strategy
    """
    
    name = "Career Coach"
    description = "Expert career advisor for job search, interviews, and professional growth"
    
    system_prompt = """You are an expert Career Coach with 15+ years experience in:
- Resume optimization (ATS-friendly formats)
- Interview preparation (behavioral, technical, case studies)
- Salary negotiation strategies
- Career transition planning
- LinkedIn profile optimization
- Job market trends and in-demand skills

Provide specific, actionable advice. Use the STAR method for interview answers.
Include industry-specific insights when relevant."""
    
    @classmethod
    async def process(cls, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        result = await local_llm_service.invoke(
            prompt=query,
            model_type="reasoning",
            system_prompt=cls.system_prompt,
            max_tokens=1500
        )
        return {
            "agent": cls.name,
            "response": result.get("response"),
            "intent": "career",
            "local": True
        }


class MentalHealthAgent:
    """
    Mental Health Support - HIGH DEMAND
    Mindfulness, stress management, emotional support
    """
    
    name = "Mental Wellness Guide"
    description = "Supportive guide for mental wellness, stress, and mindfulness"
    
    system_prompt = """You are a compassionate Mental Wellness Guide specializing in:
- Stress management techniques
- Mindfulness and meditation practices
- Anxiety coping strategies
- Sleep hygiene and relaxation
- Emotional regulation
- Work-life balance
- Positive psychology techniques

IMPORTANT: You are NOT a therapist. For serious mental health concerns, recommend professional help.
Always be warm, empathetic, and non-judgmental. Provide practical techniques.
Include: "This is general wellness guidance. For persistent mental health concerns, please consult a licensed professional."
"""
    
    @classmethod
    async def process(cls, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        result = await local_llm_service.invoke(
            prompt=query,
            model_type="reasoning",
            system_prompt=cls.system_prompt,
            max_tokens=1500
        )
        return {
            "agent": cls.name,
            "response": result.get("response"),
            "intent": "mental_health",
            "local": True
        }


class StudyTutorAgent:
    """
    Study/Learning Tutor - HIGH DEMAND
    Critical thinking, exam prep, concept clarity
    Already implemented as StudyAgent - this extends it
    """
    
    name = "Study Tutor"
    description = "Expert tutor for critical thinking and concept mastery"
    
    system_prompt = """You are a Socratic Study Tutor who builds deep understanding.

Teaching Philosophy:
- **Clarity First**: Break complex topics into digestible pieces
- **Socratic Method**: Guide through questions, don't just give answers
- **Multiple Perspectives**: Explain from different angles
- **Real-World Connections**: Link abstract to practical

For Problem Solving:
1. Understand: What is given? What is asked?
2. Break Down: Divide into smaller steps
3. Show Reasoning: Explain the "why"
4. Verify: Check if solution makes sense
5. Generalize: What applies to similar problems?

Response Format for complex problems:
🎯 **Problem**: [Clear statement]
📝 **Key Concepts**: [Prerequisites]
🔍 **Step-by-Step**: [Numbered steps with explanation]
✅ **Answer**: [Final result]
💡 **Key Insight**: [What to remember]

End with: "Does this make sense? What would you like me to clarify?"
"""
    
    @classmethod
    async def process(cls, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        result = await local_llm_service.invoke(
            prompt=query,
            model_type="reasoning",
            system_prompt=cls.system_prompt,
            max_tokens=2000,
            reasoning_mode=True  # Extended thinking for complex problems
        )
        return {
            "agent": cls.name,
            "response": result.get("response"),
            "intent": "study",
            "local": True
        }


# =============================================================================
# MEDIUM-HIGH DEMAND EXPERTS (🔥🔥)
# =============================================================================

class LegalAdvisorAgent:
    """
    Legal Advisor - MEDIUM-HIGH DEMAND
    Basic legal info, contract understanding, rights awareness
    """
    
    name = "Legal Advisor"
    description = "Basic legal information and contract understanding"
    
    system_prompt = """You are a Legal Information Guide specializing in:
- Contract basics and common terms
- Consumer rights and protections
- Employment law fundamentals
- Tenant/landlord rights
- Basic business law

CRITICAL DISCLAIMER: You provide general legal INFORMATION only, NOT legal advice.
Always include: "This is general legal information, not legal advice. For specific legal matters, consult a licensed attorney."

Focus on:
- Explaining legal terms in simple language
- Highlighting common pitfalls
- Suggesting when to seek professional help
- Providing actionable general guidance
"""
    
    @classmethod
    async def process(cls, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        result = await local_llm_service.invoke(
            prompt=query,
            model_type="reasoning",
            system_prompt=cls.system_prompt,
            max_tokens=1500
        )
        return {
            "agent": cls.name,
            "response": result.get("response"),
            "intent": "legal",
            "local": True
        }


class FinanceAdvisorAgent:
    """
    Finance Advisor - MEDIUM-HIGH DEMAND
    Personal finance, budgeting, tax basics, investment fundamentals
    """
    
    name = "Finance Advisor"
    description = "Personal finance, budgeting, and investment basics"
    
    system_prompt = """You are a Personal Finance Advisor specializing in:
- Budgeting and expense tracking (50/30/20 rule, etc.)
- Emergency fund planning
- Debt management strategies
- Tax saving options (80C, 80D, HRA, etc. for India)
- Investment fundamentals (SIP, mutual funds, FDs)
- Retirement planning basics
- Insurance needs assessment

Provide India-specific advice when relevant (PPF, NPS, ELSS, etc.).
Include disclaimers about market risk for investments.
Focus on actionable, beginner-friendly guidance.

DISCLAIMER: "This is general financial information, not personalized financial advice. Consult a certified financial planner for personalized recommendations."
"""
    
    @classmethod
    async def process(cls, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        result = await local_llm_service.invoke(
            prompt=query,
            model_type="reasoning",
            system_prompt=cls.system_prompt,
            max_tokens=1500
        )
        return {
            "agent": cls.name,
            "response": result.get("response"),
            "intent": "finance",
            "local": True
        }


class ContentWriterAgent:
    """
    Content Writer - MEDIUM-HIGH DEMAND
    Creative writing, marketing copy, social media content
    """
    
    name = "Content Writer"
    description = "Creative writing, marketing copy, and content creation"
    
    system_prompt = """You are an expert Content Writer specializing in:
- Marketing copy (headlines, ad copy, CTAs)
- Social media content (captions, hashtags, threads)
- Blog posts and articles
- Email marketing
- Product descriptions
- Creative storytelling
- SEO-optimized content

Writing principles:
- Hook readers in the first line
- Use clear, concise language
- Include emotional triggers
- End with clear calls-to-action
- Tailor tone to platform/audience

When creating content, ask about:
- Target audience
- Platform/medium
- Desired tone (professional, casual, witty)
- Key message/goal
"""
    
    @classmethod
    async def process(cls, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        result = await local_llm_service.invoke(
            prompt=query,
            model_type="reasoning",
            system_prompt=cls.system_prompt,
            max_tokens=1500
        )
        return {
            "agent": cls.name,
            "response": result.get("response"),
            "intent": "content",
            "local": True
        }


class CodeAssistantAgent:
    """
    Code Assistant - MEDIUM-HIGH DEMAND
    Code review, debugging, best practices
    """
    
    name = "Code Assistant"
    description = "Code review, debugging, and programming help"
    
    system_prompt = """You are a Senior Software Engineer with 15+ years experience.

Expertise:
- Python, JavaScript/TypeScript, React, Node.js
- Code review and best practices
- Debugging and error resolution
- Architecture and design patterns
- Performance optimization
- Security best practices

When reviewing code:
1. Identify potential bugs/issues
2. Suggest improvements (readability, performance)
3. Explain the "why" behind suggestions
4. Provide corrected code snippets
5. Mention relevant best practices

For debugging:
1. Analyze error message carefully
2. Identify root cause
3. Provide step-by-step fix
4. Suggest prevention strategies
"""
    
    @classmethod
    async def process(cls, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        result = await local_llm_service.invoke(
            prompt=query,
            model_type="coding",  # Use coding-specialized model
            system_prompt=cls.system_prompt,
            max_tokens=2000
        )
        return {
            "agent": cls.name,
            "response": result.get("response"),
            "intent": "code",
            "local": True
        }


# =============================================================================
# MEDIUM DEMAND EXPERTS (🔥)
# =============================================================================

class TravelPlannerAgent:
    """
    Travel Planner - MEDIUM DEMAND
    Trip planning, itineraries, budget travel
    """
    
    name = "Travel Planner"
    description = "Trip planning, itineraries, and travel tips"
    
    system_prompt = """You are an experienced Travel Planner specializing in:
- Destination recommendations
- Day-by-day itinerary planning
- Budget optimization
- Local experiences and hidden gems
- Visa and documentation requirements
- Safety tips and travel advisories
- Seasonal travel recommendations

When planning trips:
1. Consider budget, duration, and interests
2. Balance popular attractions with local experiences
3. Include practical logistics (transport, timing)
4. Suggest alternatives for different budgets
5. Mention must-try local food

Focus on India travel expertise while being knowledgeable globally.
"""
    
    @classmethod
    async def process(cls, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        result = await local_llm_service.invoke(
            prompt=query,
            model_type="fast",  # Travel doesn't need deep reasoning
            system_prompt=cls.system_prompt,
            max_tokens=1500
        )
        return {
            "agent": cls.name,
            "response": result.get("response"),
            "intent": "travel",
            "local": True
        }


class ParentingCoachAgent:
    """
    Parenting Coach - MEDIUM DEMAND
    Childcare, education, family dynamics
    """
    
    name = "Parenting Coach"
    description = "Parenting guidance, child development, and education"
    
    system_prompt = """You are a supportive Parenting Coach specializing in:
- Child development milestones
- Positive parenting techniques
- Education and learning support
- Discipline strategies (non-punitive)
- Screen time and digital wellness
- Nutrition for children
- Emotional support for parents

Approach:
- Non-judgmental and supportive
- Evidence-based recommendations
- Age-appropriate guidance
- Cultural sensitivity (Indian family context)
- Work-life balance for parents

Remember: Every child is different. Encourage flexibility and self-compassion for parents.
"""
    
    @classmethod
    async def process(cls, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        result = await local_llm_service.invoke(
            prompt=query,
            model_type="reasoning",
            system_prompt=cls.system_prompt,
            max_tokens=1500
        )
        return {
            "agent": cls.name,
            "response": result.get("response"),
            "intent": "parenting",
            "local": True
        }


class RelationshipCoachAgent:
    """
    Relationship Coach - MEDIUM DEMAND
    Communication, conflict resolution, relationship wellness
    """
    
    name = "Relationship Guide"
    description = "Relationship advice, communication, and conflict resolution"
    
    system_prompt = """You are a Relationship Guide specializing in:
- Communication improvement
- Conflict resolution techniques
- Building trust and intimacy
- Setting healthy boundaries
- Dating and relationship advice
- Family dynamics
- Long-distance relationship support

Principles:
- Non-judgmental and inclusive
- Focus on healthy communication patterns
- Encourage self-reflection
- Respect individual choices
- Cultural sensitivity

IMPORTANT: For serious relationship issues (abuse, severe conflict), recommend professional counseling.
"""
    
    @classmethod
    async def process(cls, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        result = await local_llm_service.invoke(
            prompt=query,
            model_type="reasoning",
            system_prompt=cls.system_prompt,
            max_tokens=1500
        )
        return {
            "agent": cls.name,
            "response": result.get("response"),
            "intent": "relationship",
            "local": True
        }


# =============================================================================
# AGENT REGISTRY
# =============================================================================

DOMAIN_EXPERTS = {
    # High Demand
    "career": CareerCoachAgent,
    "mental_health": MentalHealthAgent,
    "study": StudyTutorAgent,
    
    # Medium-High Demand
    "legal": LegalAdvisorAgent,
    "finance": FinanceAdvisorAgent,
    "content": ContentWriterAgent,
    "code": CodeAssistantAgent,
    
    # Medium Demand
    "travel": TravelPlannerAgent,
    "parenting": ParentingCoachAgent,
    "relationship": RelationshipCoachAgent,
}


async def get_expert_response(intent: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get response from appropriate domain expert"""
    
    agent_class = DOMAIN_EXPERTS.get(intent)
    
    if agent_class:
        return await agent_class.process(query, context)
    else:
        # Fallback to general response
        result = await local_llm_service.invoke(
            prompt=query,
            model_type="reasoning",
            max_tokens=1500
        )
        return {
            "agent": "General",
            "response": result.get("response"),
            "intent": intent,
            "local": True
        }

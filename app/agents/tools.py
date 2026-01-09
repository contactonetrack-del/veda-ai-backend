"""
Tool Agent
Executes calculations and returns structured results
"""
from typing import Dict, Any
import re
from app.agents.base import BaseAgent
from app.tools.calculator import calculate_calories, calculate_bmi
from app.tools.premium import estimate_premium


class ToolAgent(BaseAgent):
    """Agent that executes calculation tools"""
    
    def __init__(self):
        super().__init__(
            name="Tool Executor",
            description="Executes calculations for calories, BMI, and insurance",
            system_prompt="""You are a tool execution assistant. 
Parse the user's request and identify:
1. Which tool to use: "calories", "bmi", or "premium"
2. The parameters needed

Respond in this format:
TOOL: <tool_name>
PARAMS: <param1>=<value1>, <param2>=<value2>

Examples:
"Calculate calories in 2 dosas" → TOOL: calories, PARAMS: food=dosa, quantity=2
"My BMI for 170cm and 70kg" → TOOL: bmi, PARAMS: height=170, weight=70
"Premium for 10L cover age 35 family" → TOOL: premium, PARAMS: age=35, sum=10, type=family"""
        )
        
        # Available tools
        self.tools = {
            "calories": calculate_calories,
            "bmi": calculate_bmi,
            "premium": estimate_premium
        }
    
    async def process(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Parse request, execute tool, and return results"""
        
        # Use Gemini to parse the request
        parse_result = await self.generate(user_message)
        
        # Extract tool and params from response
        tool_name, params = self._parse_tool_response(parse_result)
        
        if not tool_name:
            return {
                "agent": self.name,
                "response": "I couldn't understand what calculation you need. Try asking about calories (e.g., 'calories in dosa'), BMI (e.g., 'calculate BMI for 170cm 70kg'), or insurance premium (e.g., 'premium for 10 lakh family plan').",
                "intent": "tool",
                "success": False
            }
        
        # Execute the tool
        try:
            if tool_name == "calories":
                result = calculate_calories(
                    params.get("food", ""),
                    float(params.get("quantity", 1))
                )
            elif tool_name == "bmi":
                result = calculate_bmi(
                    float(params.get("height", 0)),
                    float(params.get("weight", 0))
                )
            elif tool_name == "premium":
                result = estimate_premium(
                    int(params.get("age", 30)),
                    float(params.get("sum", 5)),
                    params.get("type", "individual")
                )
            else:
                result = {"success": False, "message": f"Unknown tool: {tool_name}"}
            
            # Format result as readable response
            response = self._format_result(tool_name, result)
            
            return {
                "agent": self.name,
                "response": response,
                "intent": "tool",
                "success": result.get("success", False),
                "data": result
            }
            
        except Exception as e:
            return {
                "agent": self.name,
                "response": f"Error executing calculation: {str(e)}",
                "intent": "tool",
                "success": False
            }
    
    def _parse_tool_response(self, response: str) -> tuple:
        """Extract tool name and params from Gemini response"""
        tool_name = None
        params = {}
        
        # Look for TOOL: pattern
        tool_match = re.search(r'TOOL:\s*(\w+)', response, re.IGNORECASE)
        if tool_match:
            tool_name = tool_match.group(1).lower()
        
        # Look for PARAMS: pattern
        params_match = re.search(r'PARAMS:\s*(.+)', response, re.IGNORECASE)
        if params_match:
            params_str = params_match.group(1)
            # Parse key=value pairs
            for pair in params_str.split(','):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    params[key.strip().lower()] = value.strip()
        
        return tool_name, params
    
    def _format_result(self, tool_name: str, result: Dict) -> str:
        """Format tool result as readable text"""
        
        if not result.get("success", False):
            return result.get("message", "Calculation failed")
        
        if tool_name == "calories":
            return f"""🍽️ **Calorie Information: {result['food'].title()}**

📊 **Per {result['serving_size']}** (x{result['quantity']}):
- Calories: **{result['calories']} kcal**
- Protein: {result['protein']}g
- Carbs: {result['carbs']}g
- Fat: {result['fat']}g

_Source: {result['source']}_"""
        
        elif tool_name == "bmi":
            return f"""📏 **Your BMI Analysis**

📊 **Results:**
- BMI: **{result['bmi']}** ({result['category']})
- Height: {result['height_cm']} cm
- Weight: {result['weight_kg']} kg
- Healthy Range: {result['healthy_weight_range']}

💡 **Recommendation:**
{result['recommendation']}

_Note: {result['note']}_"""
        
        elif tool_name == "premium":
            est = result['estimated_premium']
            return f"""🛡️ **Health Insurance Premium Estimate**

📋 **Coverage Details:**
- Sum Insured: {result['sum_insured']}
- Policy Type: {result['family_type']}
- Age: {result['age']} years

💰 **Estimated Annual Premium:**
- Low: {est['low']}
- Mid: {est['mid']}
- High: {est['high']}
_{est['note']}_

✨ **Typical Features at This Coverage:**
{chr(10).join('• ' + f for f in result['typical_features'])}

💡 **Recommendations:**
{chr(10).join('• ' + r for r in result['recommendations'])}

⚠️ _{result['disclaimer']}_"""
        
        return str(result)


# Singleton instance
tool_agent = ToolAgent()

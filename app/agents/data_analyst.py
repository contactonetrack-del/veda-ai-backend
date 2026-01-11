"""
Data Analyst Agent
Phase 3: Multi-Brain Architecture

Capabilities:
- Statistical analysis of health data
- Trend prediction
- Complex calculations beyond simple tools
- Python code generation and execution (Restricted)
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import io
import contextlib
from app.agents.base import BaseAgent
from app.services.groq_service import groq_service

class DataAnalystAgent(BaseAgent):
    """
    Agent that performs data analysis and statistical modeling.
    Uses LLM to generate Python code, then executes it in a restricted environment.
    """
    
    def __init__(self):
        super().__init__(
            name="DataAnalystAgent",
            description="Performs statistical analysis and data visualization",
            system_prompt="""You are an expert Data Analyst and Health Statistician.
Your goal is to analyze health data, find trends, and provide data-driven insights.
You are precise, mathematical, and logical."""
        )
    
    async def process(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze data request.
        1. Understand the data provided (or ask for it).
        2. Generate Python code to analyze it.
        3. Execute code.
        4. Explain results.
        """
        
        # Step 1: Analyze Request & Data
        # For now, we assume data is in the message or context.
        # Capability: Can generate mock data for demonstration if requested.
        
        analysis_plan = await self._plan_analysis(user_message)
        
        # Step 2: Generate Code
        code = await self._generate_code(user_message, analysis_plan)
        
        # Step 3: Execute Code (Safe Sandbox)
        execution_result = self._execute_code(code)
        
        # Step 4: Interpret Results
        final_response = await self._interpret_results(user_message, execution_result)
        
        return {
            "response": final_response,
            "success": execution_result.get("success", False),
            "agent": "DataAnalystAgent",
            "intent": "analysis",
            "data": execution_result.get("output")
        }

    async def _plan_analysis(self, query: str) -> str:
        prompt = f"Plan the statistical analysis for: {query}\nKeep it brief."
        return await groq_service.generate_response(prompt, fast=True)

    async def _generate_code(self, query: str, plan: str) -> str:
        prompt = f"""Write Python code to analyze: {query}
        Plan: {plan}
        
        RESTRICTIONS:
        - Use only pandas, numpy, math
        - Define a function analyze()
        - Return results as a string/dict
        - DO NOT use external files or network
        - Provide ONLY the python code, no markdown.
        """
        code = await groq_service.generate_response(prompt, system_prompt="You are a Python coding expert.")
        # Clean code block formatting
        code = code.replace("```python", "").replace("```", "").strip()
        return code

    def _execute_code(self, code: str) -> Dict:
        """Execute generated code in restricted scope"""
        output_buffer = io.StringIO()
        
        # Restricted globals
        safe_globals = {
            "pd": pd,
            "np": np,
            "math": __import__("math"),
            "print": lambda *args: output_buffer.write(" ".join(map(str, args)) + "\n")
        }
        
        try:
            # Capture stdout
            with contextlib.redirect_stdout(output_buffer):
                exec(code, safe_globals)
                
                # If analyze function exists, run it
                if "analyze" in safe_globals:
                    result = safe_globals["analyze"]()
                    if result:
                        print(result)
                        
            return {
                "success": True,
                "output": output_buffer.getvalue()
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"Error: {str(e)}"
            }

    async def _interpret_results(self, query: str, exec_result: Dict) -> str:
        prompt = f"""Interpret these analysis results for the user.
        
        User Query: {query}
        Analysis Output:
        {exec_result['output']}
        
        Provide a clear, data-driven answer."""
        return await groq_service.generate_response(prompt, system_prompt=self.system_prompt)

# Singleton
data_analyst_agent = DataAnalystAgent()

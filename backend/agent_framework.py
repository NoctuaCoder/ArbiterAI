"""
Agent Framework for Code Generation using Ollama LLM
Provides SimpleAgent class with planning and execution capabilities.
"""

import requests
import json
import os
from typing import List, Dict, Any, Optional
import time


class SimpleAgent:
    """
    A simple agent that uses Ollama LLM for planning and simulates code execution.
    
    Docker Networking Note:
    - When running in Docker, use 'host.docker.internal' to reach Ollama on the host
    - For Linux Docker, you may need to use '172.17.0.1' (Docker gateway IP)
    - Set OLLAMA_URL environment variable to override default
    """
    
    def __init__(self, ollama_url: str = None, model: str = "llama2"):
        """
        Initialize the SimpleAgent.
        
        Args:
            ollama_url: URL of the Ollama API endpoint. If None, will try:
                       1. OLLAMA_URL environment variable
                       2. host.docker.internal:11434 (for Docker)
                       3. localhost:11434 (fallback)
            model: Name of the Ollama model to use
        """
        # Determine Ollama URL with intelligent defaults
        if ollama_url is None:
            ollama_url = os.getenv('OLLAMA_URL')
            if ollama_url is None:
                # Try host.docker.internal first (works in Docker Desktop)
                # Falls back to localhost for non-Docker environments
                try:
                    # Test if we can resolve host.docker.internal
                    import socket
                    socket.gethostbyname('host.docker.internal')
                    ollama_url = "http://host.docker.internal:11434/api/generate"
                except (socket.gaierror, OSError):
                    # Fallback to localhost (native execution)
                    ollama_url = "http://localhost:11434/api/generate"
        
        self.ollama_url = ollama_url
        self.model = model
        self.session = requests.Session()
        print(f"🦉 SimpleAgent initialized with Ollama URL: {self.ollama_url}")
        
    def _call_ollama(self, prompt: str, stream: bool = False) -> str:
        """
        Make a request to the Ollama API.
        
        Args:
            prompt: The prompt to send to the LLM
            stream: Whether to stream the response
            
        Returns:
            The generated text response
            
        Raises:
            Exception: If the API call fails
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream
        }
        
        try:
            response = self.session.post(
                self.ollama_url,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            if stream:
                # Handle streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            full_response += data["response"]
                        if data.get("done", False):
                            break
                return full_response
            else:
                # Handle non-streaming response
                data = response.json()
                return data.get("response", "")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to call Ollama API: {str(e)}")
    
    def plan(self, task: str) -> List[str]:
        """
        Generate a detailed plan for the given task using the LLM.
        
        Args:
            task: The task description to plan for
            
        Returns:
            A list of step descriptions (strings) that form the plan
        """
        planning_prompt = f"""You are a coding assistant. Given a task, create a detailed step-by-step plan to accomplish it.
Each step should be clear, actionable, and focused on a single action.
Format your response as a numbered list, with each step on a new line.

Task: {task}

Plan (provide 3-7 specific steps):"""

        try:
            response = self._call_ollama(planning_prompt, stream=False)
            
            # Parse the response into individual steps
            lines = response.strip().split('\n')
            steps = []
            
            for line in lines:
                line = line.strip()
                # Remove numbering (1., 2., etc.) and clean up
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                    # Remove common list markers
                    cleaned = line.lstrip('0123456789.-*) \t')
                    if cleaned:
                        steps.append(cleaned)
            
            # If parsing failed, create a basic plan
            if not steps:
                steps = [
                    f"Analyze the requirements for: {task}",
                    "Design the solution architecture",
                    "Implement core functionality",
                    "Add error handling and validation",
                    "Test the implementation",
                    "Document the code"
                ]
            
            return steps[:7]  # Limit to 7 steps maximum
            
        except Exception as e:
            # Fallback plan if LLM fails
            print(f"Warning: LLM planning failed ({str(e)}), using fallback plan")
            return [
                f"Initialize project structure for: {task}",
                "Implement main logic",
                "Add error handling",
                "Write tests",
                "Complete implementation"
            ]
    
    def execute_step(self, step: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Simulate execution of a plan step.
        
        Args:
            step: The step description to execute
            context: Optional context from previous steps
            
        Returns:
            A dictionary containing:
                - status: 'success' or 'error'
                - output: The simulated output/result
                - code: Optional code snippet generated
                - context: Updated context for next steps
        """
        if context is None:
            context = {}
        
        # Simulate execution time
        time.sleep(0.5)
        
        # Generate simulated output based on the step
        step_lower = step.lower()
        
        result = {
            "status": "success",
            "output": "",
            "code": None,
            "context": context.copy()
        }
        
        # Simulate different types of steps
        if "analyze" in step_lower or "design" in step_lower:
            result["output"] = f"✓ Completed: {step}\n  → Analysis complete, ready for implementation"
            result["context"]["analyzed"] = True
            
        elif "implement" in step_lower or "create" in step_lower or "write" in step_lower:
            # Generate a simple code snippet
            result["code"] = """def example_function(param):
    \"\"\"Generated function based on requirements.\"\"\"
    try:
        # Implementation logic here
        result = process(param)
        return result
    except Exception as e:
        raise ValueError(f"Error processing: {e}")"""
            result["output"] = f"✓ Completed: {step}\n  → Code generated successfully"
            result["context"]["implemented"] = True
            
        elif "test" in step_lower:
            result["output"] = f"✓ Completed: {step}\n  → All tests passed (5/5)\n  → Coverage: 95%"
            result["context"]["tested"] = True
            
        elif "document" in step_lower:
            result["output"] = f"✓ Completed: {step}\n  → Documentation generated\n  → README.md updated"
            result["context"]["documented"] = True
            
        elif "error" in step_lower or "handling" in step_lower:
            result["output"] = f"✓ Completed: {step}\n  → Error handling added\n  → Validation implemented"
            result["context"]["error_handling"] = True
            
        else:
            result["output"] = f"✓ Completed: {step}\n  → Step executed successfully"
        
        # Simulate occasional warnings (10% chance)
        import random
        if random.random() < 0.1:
            result["output"] += "\n  ⚠ Warning: Consider adding additional validation"
        
        return result


# Example usage
if __name__ == "__main__":
    agent = SimpleAgent()
    
    # Test planning
    task = "Create a Python function to calculate fibonacci numbers"
    print(f"Task: {task}\n")
    
    plan = agent.plan(task)
    print("Plan:")
    for i, step in enumerate(plan, 1):
        print(f"  {i}. {step}")
    
    print("\nExecution:")
    context = {}
    for i, step in enumerate(plan, 1):
        print(f"\n[Step {i}] {step}")
        result = agent.execute_step(step, context)
        print(result["output"])
        if result["code"]:
            print(f"\nGenerated code:\n{result['code']}")
        context = result["context"]

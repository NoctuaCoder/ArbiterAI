"""
ArbiterAI 2.0 - Enhanced Agent Framework
Autonomous code executor with real tool execution, reflection, and memory.
"""

import requests
import json
import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from toolbox import Toolbox, ToolExecutionResult


class AutonomousAgent:
    """
    Autonomous agent that executes real tasks using tools, reflects on errors,
    and maintains project context.
    """
    
    def __init__(self, 
                 ollama_url: str = None,
                 model: str = "deepseek-coder",
                 workspace: str = "/tmp/arbiter_workspace"):
        """
        Initialize the Autonomous Agent.
        
        Args:
            ollama_url: URL of Ollama API (auto-detected if None)
            model: LLM model to use (deepseek-coder recommended for code tasks)
            workspace: Directory for file operations and command execution
        """
        # Determine Ollama URL
        if ollama_url is None:
            ollama_url = os.getenv('OLLAMA_URL')
            if ollama_url is None:
                try:
                    import socket
                    socket.gethostbyname('host.docker.internal')
                    ollama_url = "http://host.docker.internal:11434/api/generate"
                except (socket.gaierror, OSError):
                    ollama_url = "http://localhost:11434/api/generate"
        
        self.ollama_url = ollama_url
        self.model = model
        self.workspace = workspace
        self.session = requests.Session()
        self.toolbox = Toolbox(workspace=workspace)
        
        print(f"🦉 AutonomousAgent initialized")
        print(f"   Model: {self.model}")
        print(f"   Ollama: {self.ollama_url}")
        print(f"   Workspace: {self.workspace}")
    
    def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call Ollama LLM with a prompt."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = self.session.post(
                self.ollama_url,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            raise Exception(f"Ollama API call failed: {str(e)}")
    
    def plan(self, task: str, context: Optional[Dict] = None) -> List[str]:
        """
        Generate a detailed execution plan for the task.
        
        Args:
            task: Task description
            context: Optional project context
            
        Returns:
            List of executable steps
        """
        context_info = ""
        if context and context.get('files'):
            context_info = f"\n\nCurrent project files:\n{json.dumps(list(context['files'].keys()), indent=2)}"
        
        system_prompt = """You are an expert coding assistant. Create detailed, executable plans.
Each step should be specific and actionable. Focus on concrete actions like:
- "Create file X with content Y"
- "Run command Z"
- "Install package A"
Keep steps clear and sequential."""
        
        prompt = f"""Task: {task}{context_info}

Create a step-by-step plan (3-7 steps). Each step should be ONE specific action.
Format as a numbered list."""
        
        try:
            response = self._call_ollama(prompt, system_prompt)
            steps = self._parse_plan(response)
            return steps if steps else self._fallback_plan(task)
        except Exception as e:
            print(f"⚠️ Planning failed: {e}")
            return self._fallback_plan(task)
    
    def _parse_plan(self, response: str) -> List[str]:
        """Parse LLM response into list of steps."""
        steps = []
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
            # Remove numbering
            cleaned = re.sub(r'^(\d+[\.\):]?\s*|Step\s+\d+[\.\):]?\s*|-\s*|\*\s*)', '', line, flags=re.IGNORECASE)
            if cleaned:
                steps.append(cleaned)
        return steps[:7]
    
    def _fallback_plan(self, task: str) -> List[str]:
        """Generate fallback plan if LLM fails."""
        return [
            f"Analyze requirements for: {task}",
            "Create project structure",
            "Implement core functionality",
            "Test implementation",
            "Complete task"
        ]
    
    def select_tool(self, step: str, context: Dict) -> Dict[str, Any]:
        """
        Use LLM to select appropriate tool and extract arguments.
        
        Args:
            step: Step description
            context: Current project context
            
        Returns:
            {tool: "tool_name", args: {arg1: val1, ...}}
        """
        files_info = ""
        if context.get('files'):
            files_info = f"\nCurrent files:\n{json.dumps(list(context['files'].keys()), indent=2)}"
        
        system_prompt = """You are a tool selector. Analyze the step and choose the right tool.

Available tools:
- shell: Execute shell commands (args: command)
- write_file: Create/update files (args: filepath, content)
- read_file: Read file contents (args: filepath)
- delete_file: Delete a file (args: filepath)
- list_files: List directory contents (args: directory)
- web_fetch: HTTP request (args: url, method, data)

Respond ONLY with JSON: {"tool": "tool_name", "args": {...}}"""
        
        prompt = f"""Step: {step}{files_info}

Which tool should be used? Provide JSON response."""
        
        try:
            response = self._call_ollama(prompt, system_prompt)
            # Extract JSON from response
            json_match = re.search(r'\{[^{}]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            # Fallback: guess based on keywords
            return self._guess_tool(step)
        except Exception as e:
            print(f"⚠️ Tool selection failed: {e}")
            return self._guess_tool(step)
    
    def _guess_tool(self, step: str) -> Dict[str, Any]:
        """Fallback tool selection based on keywords."""
        step_lower = step.lower()
        
        if any(word in step_lower for word in ['create file', 'write file', 'save']):
            return {"tool": "write_file", "args": {"filepath": "output.txt", "content": "# TODO"}}
        elif any(word in step_lower for word in ['run', 'execute', 'install', 'npm', 'pip', 'python']):
            # Extract command
            cmd = step.split('run')[-1].strip() if 'run' in step_lower else step
            return {"tool": "shell", "args": {"command": cmd}}
        elif 'read' in step_lower or 'check' in step_lower:
            return {"tool": "list_files", "args": {"directory": "."}}
        else:
            return {"tool": "shell", "args": {"command": "echo 'Step: " + step + "'"}}
    
    def execute_step(self, step: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step using real tools.
        
        Args:
            step: Step description
            context: Project context
            
        Returns:
            {success: bool, output: str, error: str, context: dict, tool_used: str}
        """
        # Select tool
        tool_selection = self.select_tool(step, context)
        tool_name = tool_selection.get('tool', 'shell')
        tool_args = tool_selection.get('args', {})
        
        print(f"🔧 Tool: {tool_name} | Args: {tool_args}")
        
        # Execute tool
        result: ToolExecutionResult = self.toolbox.execute_tool(tool_name, **tool_args)
        
        # Update context with file changes
        if tool_name in ['write_file', 'delete_file']:
            context['files'] = self._scan_workspace()
        
        # Track execution history
        if 'history' not in context:
            context['history'] = []
        context['history'].append({
            "step": step,
            "tool": tool_name,
            "success": result.success,
            "error": result.error
        })
        
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "context": context,
            "tool_used": tool_name,
            "tool_args": tool_args
        }
    
    def _scan_workspace(self) -> Dict[str, str]:
        """Scan workspace and read all files into context."""
        files = {}
        workspace_path = Path(self.workspace)
        
        if not workspace_path.exists():
            return files
        
        for filepath in workspace_path.rglob('*'):
            if filepath.is_file():
                try:
                    relative_path = filepath.relative_to(workspace_path)
                    content = filepath.read_text()
                    files[str(relative_path)] = content
                except Exception:
                    pass  # Skip unreadable files
        
        return files
    
    def reflect_on_error(self, 
                        original_task: str,
                        failed_step: str,
                        error: str,
                        context: Dict) -> List[str]:
        """
        Reflect on error and generate correction plan.
        
        Args:
            original_task: The original task
            failed_step: The step that failed
            error: Error message
            context: Current context
            
        Returns:
            New plan to fix the error and continue
        """
        files_info = ""
        if context.get('files'):
            files_info = f"\nCurrent files:\n" + "\n".join(context['files'].keys())
        
        history_info = ""
        if context.get('history'):
            recent = context['history'][-3:]  # Last 3 steps
            history_info = "\nRecent steps:\n" + "\n".join([
                f"- {h['step']} ({'✓' if h['success'] else '✗'})"
                for h in recent
            ])
        
        system_prompt = """You are an expert debugger. Analyze errors and create correction plans.
Focus on fixing the root cause, not just symptoms."""
        
        prompt = f"""Original Task: {original_task}

Failed Step: {failed_step}
Error: {error}{files_info}{history_info}

Analyze the error and create a NEW plan to:
1. Fix the error
2. Continue with the original task

Provide 2-5 corrective steps as a numbered list."""
        
        try:
            response = self._call_ollama(prompt, system_prompt)
            correction_plan = self._parse_plan(response)
            return correction_plan if correction_plan else [
                "Investigate error cause",
                "Apply fix",
                "Retry failed step"
            ]
        except Exception as e:
            print(f"⚠️ Reflection failed: {e}")
            return ["Retry with different approach", "Continue task"]
    
    def initialize_context(self, task: str) -> Dict[str, Any]:
        """Initialize execution context."""
        return {
            "task": task,
            "files": self._scan_workspace(),
            "history": [],
            "workspace": self.workspace
        }


# Example usage
if __name__ == "__main__":
    agent = AutonomousAgent()
    
    task = "Create a Python hello world script"
    print(f"\n📋 Task: {task}\n")
    
    # Initialize context
    context = agent.initialize_context(task)
    
    # Generate plan
    plan = agent.plan(task, context)
    print("📝 Plan:")
    for i, step in enumerate(plan, 1):
        print(f"  {i}. {step}")
    
    # Execute plan
    print("\n⚙️ Execution:")
    for i, step in enumerate(plan, 1):
        print(f"\n[Step {i}/{len(plan)}] {step}")
        result = agent.execute_step(step, context)
        
        if result['success']:
            print(f"✅ {result['output']}")
        else:
            print(f"❌ Error: {result['error']}")
            # Reflect on error
            correction = agent.reflect_on_error(task, step, result['error'], context)
            print(f"🤔 Correction plan: {correction}")
        
        context = result['context']
    
    print(f"\n📁 Files created: {list(context.get('files', {}).keys())}")

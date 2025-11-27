"""
Toolbox - Real Execution Capabilities for ArbiterAI

Provides safe execution of shell commands, file operations, and web requests.
Each tool includes error handling, sanitization, and result capture.
"""

import subprocess
import os
import json
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path
import shlex


class ToolExecutionResult:
    """Result of a tool execution."""
    
    def __init__(self, success: bool, output: str, error: Optional[str] = None, data: Optional[Dict] = None):
        self.success = success
        self.output = output
        self.error = error
        self.data = data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "data": self.data
        }


class ShellExecutor:
    """
    Executes shell commands with safety restrictions.
    
    SECURITY WARNING: This can execute arbitrary commands.
    Use with caution and implement proper restrictions in production.
    """
    
    # Commands that are explicitly blocked
    BLACKLIST = [
        'rm -rf /',
        'dd if=',
        'mkfs',
        'format',
        ':(){ :|:& };:',  # Fork bomb
    ]
    
    # Commands that are allowed (whitelist mode - more secure)
    WHITELIST = [
        'npm', 'node', 'python', 'python3', 'pip', 'pip3',
        'git', 'ls', 'cat', 'echo', 'mkdir', 'touch',
        'curl', 'wget', 'grep', 'find', 'cd', 'pwd',
        'docker', 'docker-compose'
    ]
    
    def __init__(self, workspace: str = "/tmp/arbiter_workspace", use_whitelist: bool = True):
        """
        Initialize ShellExecutor.
        
        Args:
            workspace: Directory where commands will be executed
            use_whitelist: If True, only whitelisted commands are allowed
        """
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.use_whitelist = use_whitelist
    
    def _is_safe_command(self, command: str) -> tuple[bool, str]:
        """
        Check if command is safe to execute.
        
        Returns:
            (is_safe, reason)
        """
        # Check blacklist
        for blocked in self.BLACKLIST:
            if blocked in command:
                return False, f"Command contains blocked pattern: {blocked}"
        
        # Check whitelist if enabled
        if self.use_whitelist:
            cmd_parts = shlex.split(command)
            if cmd_parts:
                base_cmd = cmd_parts[0]
                if base_cmd not in self.WHITELIST:
                    return False, f"Command '{base_cmd}' not in whitelist"
        
        return True, "OK"
    
    def execute(self, command: str, timeout: int = 30) -> ToolExecutionResult:
        """
        Execute a shell command.
        
        Args:
            command: Shell command to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            ToolExecutionResult with command output
        """
        # Safety check
        is_safe, reason = self._is_safe_command(command)
        if not is_safe:
            return ToolExecutionResult(
                success=False,
                output="",
                error=f"🚫 Command blocked: {reason}"
            )
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return ToolExecutionResult(
                    success=True,
                    output=result.stdout,
                    data={"exit_code": result.returncode}
                )
            else:
                return ToolExecutionResult(
                    success=False,
                    output=result.stdout,
                    error=result.stderr,
                    data={"exit_code": result.returncode}
                )
                
        except subprocess.TimeoutExpired:
            return ToolExecutionResult(
                success=False,
                output="",
                error=f"⏱️ Command timed out after {timeout} seconds"
            )
        except Exception as e:
            return ToolExecutionResult(
                success=False,
                output="",
                error=f"❌ Execution error: {str(e)}"
            )


class FileManager:
    """
    Manages file operations with path restrictions.
    """
    
    def __init__(self, workspace: str = "/tmp/arbiter_workspace"):
        """
        Initialize FileManager.
        
        Args:
            workspace: Root directory for file operations
        """
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
    
    def _resolve_path(self, filepath: str) -> Optional[Path]:
        """
        Resolve and validate file path.
        
        Returns:
            Resolved path if valid, None if outside workspace
        """
        try:
            full_path = (self.workspace / filepath).resolve()
            # Ensure path is within workspace
            if self.workspace in full_path.parents or full_path == self.workspace:
                return full_path
            return None
        except Exception:
            return None
    
    def read_file(self, filepath: str) -> ToolExecutionResult:
        """Read file contents."""
        path = self._resolve_path(filepath)
        if not path:
            return ToolExecutionResult(
                success=False,
                output="",
                error=f"🚫 Path '{filepath}' is outside workspace"
            )
        
        try:
            if not path.exists():
                return ToolExecutionResult(
                    success=False,
                    output="",
                    error=f"📁 File not found: {filepath}"
                )
            
            content = path.read_text()
            return ToolExecutionResult(
                success=True,
                output=content,
                data={"filepath": str(path), "size": len(content)}
            )
        except Exception as e:
            return ToolExecutionResult(
                success=False,
                output="",
                error=f"❌ Read error: {str(e)}"
            )
    
    def write_file(self, filepath: str, content: str) -> ToolExecutionResult:
        """Write content to file."""
        path = self._resolve_path(filepath)
        if not path:
            return ToolExecutionResult(
                success=False,
                output="",
                error=f"🚫 Path '{filepath}' is outside workspace"
            )
        
        try:
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            
            return ToolExecutionResult(
                success=True,
                output=f"✅ File written: {filepath} ({len(content)} bytes)",
                data={"filepath": str(path), "size": len(content)}
            )
        except Exception as e:
            return ToolExecutionResult(
                success=False,
                output="",
                error=f"❌ Write error: {str(e)}"
            )
    
    def delete_file(self, filepath: str) -> ToolExecutionResult:
        """Delete a file."""
        path = self._resolve_path(filepath)
        if not path:
            return ToolExecutionResult(
                success=False,
                output="",
                error=f"🚫 Path '{filepath}' is outside workspace"
            )
        
        try:
            if not path.exists():
                return ToolExecutionResult(
                    success=False,
                    output="",
                    error=f"📁 File not found: {filepath}"
                )
            
            path.unlink()
            return ToolExecutionResult(
                success=True,
                output=f"🗑️ File deleted: {filepath}"
            )
        except Exception as e:
            return ToolExecutionResult(
                success=False,
                output="",
                error=f"❌ Delete error: {str(e)}"
            )
    
    def list_files(self, directory: str = ".") -> ToolExecutionResult:
        """List files in directory."""
        path = self._resolve_path(directory)
        if not path:
            return ToolExecutionResult(
                success=False,
                output="",
                error=f"🚫 Path '{directory}' is outside workspace"
            )
        
        try:
            if not path.is_dir():
                return ToolExecutionResult(
                    success=False,
                    output="",
                    error=f"📁 Not a directory: {directory}"
                )
            
            files = []
            for item in path.iterdir():
                files.append({
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0
                })
            
            output = "\n".join([f"{'📁' if f['type'] == 'dir' else '📄'} {f['name']}" for f in files])
            
            return ToolExecutionResult(
                success=True,
                output=output,
                data={"files": files, "count": len(files)}
            )
        except Exception as e:
            return ToolExecutionResult(
                success=False,
                output="",
                error=f"❌ List error: {str(e)}"
            )


class WebFetcher:
    """
    Fetches content from web URLs.
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ArbiterAI/2.0'
        })
    
    def fetch(self, url: str, method: str = "GET", data: Optional[Dict] = None) -> ToolExecutionResult:
        """
        Fetch content from URL.
        
        Args:
            url: URL to fetch
            method: HTTP method (GET, POST, etc.)
            data: Optional data for POST requests
        """
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code < 400:
                return ToolExecutionResult(
                    success=True,
                    output=response.text[:1000],  # Limit output
                    data={
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "full_content": response.text
                    }
                )
            else:
                return ToolExecutionResult(
                    success=False,
                    output="",
                    error=f"🌐 HTTP {response.status_code}: {response.reason}",
                    data={"status_code": response.status_code}
                )
                
        except requests.exceptions.Timeout:
            return ToolExecutionResult(
                success=False,
                output="",
                error=f"⏱️ Request timed out after {self.timeout} seconds"
            )
        except Exception as e:
            return ToolExecutionResult(
                success=False,
                output="",
                error=f"❌ Request error: {str(e)}"
            )


class Toolbox:
    """
    Main toolbox that combines all tools.
    """
    
    def __init__(self, workspace: str = "/tmp/arbiter_workspace"):
        self.workspace = workspace
        self.shell = ShellExecutor(workspace)
        self.files = FileManager(workspace)
        self.web = WebFetcher()
    
    def execute_tool(self, tool_name: str, **kwargs) -> ToolExecutionResult:
        """
        Execute a tool by name.
        
        Args:
            tool_name: Name of tool (shell, read_file, write_file, etc.)
            **kwargs: Tool-specific arguments
        """
        tool_map = {
            "shell": lambda: self.shell.execute(kwargs.get("command", "")),
            "read_file": lambda: self.files.read_file(kwargs.get("filepath", "")),
            "write_file": lambda: self.files.write_file(
                kwargs.get("filepath", ""),
                kwargs.get("content", "")
            ),
            "delete_file": lambda: self.files.delete_file(kwargs.get("filepath", "")),
            "list_files": lambda: self.files.list_files(kwargs.get("directory", ".")),
            "web_fetch": lambda: self.web.fetch(
                kwargs.get("url", ""),
                kwargs.get("method", "GET"),
                kwargs.get("data")
            )
        }
        
        if tool_name not in tool_map:
            return ToolExecutionResult(
                success=False,
                output="",
                error=f"❌ Unknown tool: {tool_name}"
            )
        
        return tool_map[tool_name]()


# Example usage
if __name__ == "__main__":
    toolbox = Toolbox()
    
    # Test file operations
    print("=== Testing File Operations ===")
    result = toolbox.execute_tool("write_file", filepath="test.py", content="print('Hello, World!')")
    print(f"Write: {result.output}")
    
    result = toolbox.execute_tool("read_file", filepath="test.py")
    print(f"Read: {result.output}")
    
    result = toolbox.execute_tool("list_files")
    print(f"List:\n{result.output}")
    
    # Test shell execution
    print("\n=== Testing Shell Execution ===")
    result = toolbox.execute_tool("shell", command="python test.py")
    print(f"Shell: {result.output}")

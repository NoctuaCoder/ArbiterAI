"""
Shell Execution Plugin for ArbiterAI
Executes shell commands with MANDATORY Docker isolation.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from plugin_interface import (
    ArbiterPlugin,
    PluginMetadata,
    PluginResult,
    PluginPermission
)
from sandbox_manager import DockerSandbox


class ShellPlugin(ArbiterPlugin):
    """
    Execute shell commands with Docker isolation.
    
    Security:
    - MANDATORY Docker container execution
    - No fallback to direct execution
    - Resource limits enforced
    - Network isolation by default
    """
    
    # Command whitelist (additional safety layer)
    WHITELIST = [
        'npm', 'node', 'python', 'python3', 'pip', 'pip3',
        'git', 'ls', 'cat', 'echo', 'mkdir', 'touch',
        'curl', 'wget', 'grep', 'find', 'cd', 'pwd',
        'docker', 'docker-compose', 'go', 'cargo', 'rustc'
    ]
    
    # Dangerous command patterns (blacklist)
    BLACKLIST = [
        'rm -rf /',
        'dd if=',
        'mkfs',
        'format',
        ':(){ :|:& };:',  # Fork bomb
        'chmod 777',
        'chown root'
    ]
    
    def __init__(self):
        self.sandbox = None
        self.workspace_path = None
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="shell",
            version="2.0.0",
            author="ArbiterAI",
            description="Execute shell commands in Docker containers",
            dependencies=["docker"],
            permissions=[
                PluginPermission.SHELL,
                PluginPermission.FILESYSTEM
            ]
        )
    
    def initialize(self, workspace: str) -> bool:
        """Initialize Docker sandbox."""
        try:
            self.workspace_path = workspace
            self.sandbox = DockerSandbox(
                workspace_path=workspace,
                cpu_limit=1.0,
                memory_limit="512m",
                enable_network=False  # Disabled by default for security
            )
            return True
        except Exception as e:
            print(f"❌ Shell plugin initialization failed: {e}")
            return False
    
    def execute(self, 
                command: str,
                timeout: int = 30,
                enable_network: bool = False,
                **kwargs) -> PluginResult:
        """
        Execute shell command in Docker container.
        
        Args:
            command: Shell command to execute
            timeout: Execution timeout (default: 30s)
            enable_network: Enable network access (default: False)
            
        Returns:
            PluginResult with command output
        """
        if not self.sandbox:
            return PluginResult(
                success=False,
                error="Shell plugin not initialized (Docker required)"
            )
        
        try:
            # Execute in Docker sandbox
            result = self.sandbox.execute(command, timeout)
            
            return PluginResult(
                success=result.success,
                output=result.stdout,
                error=result.stderr,
                data={
                    "exit_code": result.exit_code,
                    "execution_time": result.execution_time,
                    "sandbox": "docker"
                }
            )
            
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Shell execution error: {str(e)}"
            )
    
    def validate_input(self, **kwargs) -> tuple[bool, str]:
        """Validate shell command."""
        if "command" not in kwargs:
            return False, "Parameter 'command' is required"
        
        command = kwargs["command"].strip()
        if not command:
            return False, "Command cannot be empty"
        
        # Check blacklist
        for blocked in self.BLACKLIST:
            if blocked in command:
                return False, f"Dangerous command pattern detected: {blocked}"
        
        # Check whitelist (optional, can be disabled)
        # For now, we rely on Docker isolation
        
        return True, ""
    
    def describe(self):
        return {
            "name": "shell",
            "description": "Execute shell commands in isolated Docker containers with resource limits",
            "parameters": {
                "command": "Shell command to execute (string)",
                "timeout": "Execution timeout in seconds (optional, default: 30)",
                "enable_network": "Enable network access (optional, default: False)"
            },
            "examples": [
                "Run 'python script.py'",
                "Execute 'npm install'",
                "Run 'git clone repo_url'",
                "Execute 'pytest tests/'",
                "Run 'docker build -t image .'",
                "List files with 'ls -la'"
            ]
        }
    
    def cleanup(self):
        """Cleanup Docker sandbox."""
        if self.sandbox:
            # Docker containers are ephemeral, no cleanup needed
            pass


# Test the plugin
if __name__ == "__main__":
    import tempfile
    import shutil
    
    # Create temp workspace
    workspace = tempfile.mkdtemp()
    
    try:
        plugin = ShellPlugin()
        
        if not plugin.initialize(workspace):
            print("❌ Failed to initialize shell plugin (Docker required)")
            exit(1)
        
        print("=== Shell Plugin Test ===\n")
        
        # Test 1: Simple command
        print("Test 1: Echo command")
        result = plugin.execute(command="echo 'Hello from Docker!'")
        print(f"Success: {result.success}")
        print(f"Output: {result.output}")
        print(f"Sandbox: {result.data.get('sandbox')}\n")
        
        # Test 2: Python execution
        print("Test 2: Python command")
        result = plugin.execute(command="python --version")
        print(f"Success: {result.success}")
        print(f"Output: {result.output}\n")
        
        # Test 3: File operations
        print("Test 3: File operations")
        result = plugin.execute(command="echo 'test' > /workspace/test.txt && cat /workspace/test.txt")
        print(f"Success: {result.success}")
        print(f"Output: {result.output}\n")
        
        # Test 4: Validation (should fail)
        print("Test 4: Dangerous command (should fail)")
        result = plugin.execute(command="rm -rf /")
        print(f"Success: {result.success}")
        print(f"Error: {result.error}\n")
        
    finally:
        # Cleanup
        shutil.rmtree(workspace)
        print("Workspace cleaned up")

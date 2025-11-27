"""
ArbiterAI Docker Sandbox Manager
Enterprise-grade container isolation for code execution.
"""

import docker
from docker.errors import DockerException, ContainerError, ImageNotFound
import time
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SandboxExecutionResult:
    """Result of sandbox execution."""
    
    def __init__(self, success: bool, stdout: str = "", stderr: str = "", 
                 exit_code: int = 0, execution_time: float = 0.0):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.execution_time = execution_time
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "execution_time": self.execution_time
        }


class DockerSandbox:
    """
    Docker-based sandbox for secure code execution.
    
    Features:
    - Ephemeral containers (created and destroyed per execution)
    - Resource limits (CPU, memory, disk)
    - Network isolation
    - Non-root execution
    - Automatic cleanup
    """
    
    DEFAULT_IMAGE = "arbiter-sandbox:latest"
    FALLBACK_IMAGE = "python:3.11-slim"
    
    def __init__(self, 
                 workspace_path: str,
                 image: str = None,
                 cpu_limit: float = 1.0,
                 memory_limit: str = "512m",
                 enable_network: bool = False):
        """
        Initialize Docker sandbox.
        
        Args:
            workspace_path: Path to workspace directory
            image: Docker image to use (default: arbiter-sandbox:latest)
            cpu_limit: CPU cores limit (default: 1.0)
            memory_limit: Memory limit (default: 512m)
            enable_network: Enable network access (default: False)
        """
        self.workspace_path = Path(workspace_path).resolve()
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
        self.image = image or self.DEFAULT_IMAGE
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit
        self.enable_network = enable_network
        
        # Initialize Docker client
        try:
            self.client = docker.from_env()
            logger.info(f"🐳 Docker client initialized")
        except DockerException as e:
            raise Exception(f"Failed to connect to Docker: {str(e)}\n"
                          f"Ensure Docker is installed and running.")
        
        # Verify image exists or use fallback
        self._verify_image()
    
    def _verify_image(self):
        """Verify Docker image exists, use fallback if not."""
        try:
            self.client.images.get(self.image)
            logger.info(f"✅ Using image: {self.image}")
        except ImageNotFound:
            logger.warning(f"⚠️ Image {self.image} not found, using fallback: {self.FALLBACK_IMAGE}")
            self.image = self.FALLBACK_IMAGE
            try:
                self.client.images.pull(self.FALLBACK_IMAGE)
                logger.info(f"✅ Pulled fallback image: {self.FALLBACK_IMAGE}")
            except Exception as e:
                raise Exception(f"Failed to pull fallback image: {str(e)}")
    
    def execute(self, 
                command: str,
                timeout: int = 30,
                working_dir: str = "/workspace") -> SandboxExecutionResult:
        """
        Execute command in ephemeral Docker container.
        
        Args:
            command: Command to execute
            timeout: Execution timeout in seconds
            working_dir: Working directory inside container
            
        Returns:
            SandboxExecutionResult with execution details
        """
        container = None
        start_time = time.time()
        
        try:
            # Container configuration
            container_config = {
                "image": self.image,
                "command": ["sh", "-c", command],
                "working_dir": working_dir,
                "detach": True,
                "remove": False,  # We'll remove manually for better error handling
                "volumes": {
                    str(self.workspace_path): {
                        'bind': '/workspace',
                        'mode': 'rw'
                    }
                },
                # Resource limits
                "cpu_quota": int(self.cpu_limit * 100000),
                "cpu_period": 100000,
                "mem_limit": self.memory_limit,
                "memswap_limit": self.memory_limit,  # No swap
                # Security
                "network_mode": "bridge" if self.enable_network else "none",
                "user": "1000:1000",  # Non-root user
                "read_only": False,  # Need write access to /workspace
                "security_opt": ["no-new-privileges"],
            }
            
            logger.info(f"🚀 Executing in container: {command[:50]}...")
            
            # Create and start container
            container = self.client.containers.run(**container_config)
            
            # Wait for completion with timeout
            try:
                result = container.wait(timeout=timeout)
                exit_code = result.get('StatusCode', -1)
            except Exception as e:
                logger.error(f"⏱️ Container timeout or error: {str(e)}")
                container.stop(timeout=1)
                execution_time = time.time() - start_time
                return SandboxExecutionResult(
                    success=False,
                    stdout="",
                    stderr=f"Execution timeout after {timeout}s",
                    exit_code=-1,
                    execution_time=execution_time
                )
            
            # Get logs
            stdout = container.logs(stdout=True, stderr=False).decode('utf-8', errors='replace')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8', errors='replace')
            
            execution_time = time.time() - start_time
            
            success = exit_code == 0
            
            if success:
                logger.info(f"✅ Execution successful ({execution_time:.2f}s)")
            else:
                logger.warning(f"❌ Execution failed with exit code {exit_code}")
            
            return SandboxExecutionResult(
                success=success,
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                execution_time=execution_time
            )
            
        except ContainerError as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Container error: {str(e)}")
            return SandboxExecutionResult(
                success=False,
                stdout="",
                stderr=f"Container error: {str(e)}",
                exit_code=e.exit_status,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Unexpected error: {str(e)}")
            return SandboxExecutionResult(
                success=False,
                stdout="",
                stderr=f"Sandbox error: {str(e)}",
                exit_code=-1,
                execution_time=execution_time
            )
            
        finally:
            # Cleanup container
            if container:
                try:
                    container.remove(force=True)
                    logger.debug("🗑️ Container removed")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to remove container: {str(e)}")
    
    def execute_python(self, code: str, timeout: int = 30) -> SandboxExecutionResult:
        """
        Execute Python code in sandbox.
        
        Args:
            code: Python code to execute
            timeout: Execution timeout
            
        Returns:
            SandboxExecutionResult
        """
        # Write code to temp file
        temp_file = self.workspace_path / "_temp_script.py"
        temp_file.write_text(code)
        
        try:
            result = self.execute(f"python /workspace/_temp_script.py", timeout)
            return result
        finally:
            # Cleanup temp file
            if temp_file.exists():
                temp_file.unlink()
    
    def execute_node(self, code: str, timeout: int = 30) -> SandboxExecutionResult:
        """
        Execute Node.js code in sandbox.
        
        Args:
            code: JavaScript code to execute
            timeout: Execution timeout
            
        Returns:
            SandboxExecutionResult
        """
        # Write code to temp file
        temp_file = self.workspace_path / "_temp_script.js"
        temp_file.write_text(code)
        
        try:
            result = self.execute(f"node /workspace/_temp_script.js", timeout)
            return result
        finally:
            # Cleanup temp file
            if temp_file.exists():
                temp_file.unlink()
    
    def health_check(self) -> bool:
        """
        Check if Docker sandbox is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            result = self.execute("echo 'health check'", timeout=5)
            return result.success and "health check" in result.stdout
        except Exception:
            return False


# Example usage
if __name__ == "__main__":
    # Create sandbox
    sandbox = DockerSandbox(workspace_path="/tmp/sandbox_test")
    
    # Test 1: Simple command
    print("=== Test 1: Simple Command ===")
    result = sandbox.execute("echo 'Hello from Docker!'")
    print(f"Success: {result.success}")
    print(f"Output: {result.stdout}")
    print(f"Time: {result.execution_time:.2f}s\n")
    
    # Test 2: Python execution
    print("=== Test 2: Python Code ===")
    python_code = """
print("Python in Docker!")
import sys
print(f"Python version: {sys.version}")
"""
    result = sandbox.execute_python(python_code)
    print(f"Success: {result.success}")
    print(f"Output: {result.stdout}")
    print(f"Time: {result.execution_time:.2f}s\n")
    
    # Test 3: File operations
    print("=== Test 3: File Operations ===")
    result = sandbox.execute("echo 'test content' > /workspace/test.txt && cat /workspace/test.txt")
    print(f"Success: {result.success}")
    print(f"Output: {result.stdout}")
    
    # Test 4: Health check
    print("\n=== Test 4: Health Check ===")
    healthy = sandbox.health_check()
    print(f"Sandbox healthy: {healthy}")

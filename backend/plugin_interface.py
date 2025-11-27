"""
ArbiterAI Plugin Interface
Base classes and metadata for plugin development.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class PluginPermission(Enum):
    """Plugin permission levels."""
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    DATABASE = "database"
    CLOUD = "cloud"
    SHELL = "shell"


@dataclass
class PluginMetadata:
    """Plugin metadata."""
    name: str
    version: str
    author: str
    description: str
    dependencies: List[str] = None
    permissions: List[PluginPermission] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.permissions is None:
            self.permissions = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "dependencies": self.dependencies,
            "permissions": [p.value for p in self.permissions]
        }


class PluginResult:
    """Standardized plugin execution result."""
    
    def __init__(self, 
                 success: bool,
                 output: str = "",
                 error: Optional[str] = None,
                 data: Optional[Dict[str, Any]] = None):
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


class ArbiterPlugin(ABC):
    """
    Base class for all ArbiterAI plugins.
    
    Plugins extend ArbiterAI's capabilities by providing new tools
    that the agent can use to accomplish tasks.
    
    Example:
        class MyPlugin(ArbiterPlugin):
            @property
            def metadata(self):
                return PluginMetadata(
                    name="my_plugin",
                    version="1.0.0",
                    author="Your Name",
                    description="What it does"
                )
            
            def execute(self, **kwargs):
                # Your logic here
                return PluginResult(
                    success=True,
                    output="Result"
                )
    """
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """
        Plugin metadata.
        
        Returns:
            PluginMetadata with name, version, author, etc.
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> PluginResult:
        """
        Execute plugin action.
        
        Args:
            **kwargs: Plugin-specific parameters
            
        Returns:
            PluginResult with success status, output, and optional data
        """
        pass
    
    def validate_input(self, **kwargs) -> tuple[bool, str]:
        """
        Validate input parameters before execution.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            (is_valid, error_message)
        """
        return True, ""
    
    def describe(self) -> Dict[str, Any]:
        """
        Describe plugin capabilities for LLM tool selection.
        
        This description helps the LLM understand when and how to use
        this plugin.
        
        Returns:
            Dictionary with:
                - name: Plugin name
                - description: What the plugin does
                - parameters: Expected parameters with descriptions
                - examples: Example usage scenarios
        """
        return {
            "name": self.metadata.name,
            "description": self.metadata.description,
            "parameters": {},
            "examples": []
        }
    
    def initialize(self, workspace: str) -> bool:
        """
        Initialize plugin with workspace.
        
        Called once when plugin is loaded.
        
        Args:
            workspace: Path to workspace directory
            
        Returns:
            True if initialization successful
        """
        return True
    
    def cleanup(self) -> None:
        """
        Cleanup plugin resources.
        
        Called when plugin is unloaded or on shutdown.
        """
        pass


class PluginError(Exception):
    """Base exception for plugin errors."""
    pass


class PluginLoadError(PluginError):
    """Raised when plugin fails to load."""
    pass


class PluginExecutionError(PluginError):
    """Raised when plugin execution fails."""
    pass


class PluginValidationError(PluginError):
    """Raised when plugin input validation fails."""
    pass


# Example plugin for reference
class ExamplePlugin(ArbiterPlugin):
    """
    Example plugin demonstrating the plugin interface.
    
    This plugin echoes back the input message.
    """
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="example",
            version="1.0.0",
            author="ArbiterAI",
            description="Example plugin that echoes messages",
            dependencies=[],
            permissions=[]
        )
    
    def execute(self, message: str = "Hello", **kwargs) -> PluginResult:
        """Echo the message."""
        return PluginResult(
            success=True,
            output=f"Echo: {message}",
            data={"original": message}
        )
    
    def validate_input(self, **kwargs) -> tuple[bool, str]:
        """Validate that message is provided."""
        if "message" not in kwargs:
            return False, "Parameter 'message' is required"
        return True, ""
    
    def describe(self) -> Dict[str, Any]:
        return {
            "name": "example",
            "description": "Echoes back the provided message",
            "parameters": {
                "message": "The message to echo (string)"
            },
            "examples": [
                "Echo 'Hello World'",
                "Repeat the message 'Test'"
            ]
        }


if __name__ == "__main__":
    # Test example plugin
    plugin = ExamplePlugin()
    
    print("Plugin Metadata:")
    print(plugin.metadata.to_dict())
    
    print("\nPlugin Description:")
    print(plugin.describe())
    
    print("\nExecuting plugin:")
    result = plugin.execute(message="Hello from ArbiterAI!")
    print(f"Success: {result.success}")
    print(f"Output: {result.output}")
    print(f"Data: {result.data}")

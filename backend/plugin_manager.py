"""
ArbiterAI Plugin Manager
Discovers, loads, and manages plugins.
"""

import os
import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from plugin_interface import (
    ArbiterPlugin, 
    PluginMetadata, 
    PluginResult,
    PluginLoadError,
    PluginExecutionError,
    PluginValidationError
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PluginManager:
    """
    Manages plugin discovery, loading, and execution.
    
    Features:
    - Auto-discovery from plugins/ directory
    - Dynamic loading with importlib
    - Plugin enable/disable
    - Dependency resolution
    - Error handling
    """
    
    def __init__(self, workspace: str, plugins_dir: str = None):
        """
        Initialize plugin manager.
        
        Args:
            workspace: Workspace directory path
            plugins_dir: Custom plugins directory (default: ./plugins)
        """
        self.workspace = workspace
        
        if plugins_dir is None:
            # Default to plugins/ directory next to this file
            base_dir = Path(__file__).parent
            plugins_dir = base_dir / "plugins"
        
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # Loaded plugins: {name: plugin_instance}
        self.plugins: Dict[str, ArbiterPlugin] = {}
        
        # Disabled plugins
        self.disabled_plugins: set = set()
        
        logger.info(f"🔌 PluginManager initialized")
        logger.info(f"   Plugins directory: {self.plugins_dir}")
        logger.info(f"   Workspace: {self.workspace}")
    
    def discover_plugins(self) -> List[str]:
        """
        Discover all plugins in plugins directory.
        
        Returns:
            List of discovered plugin module names
        """
        discovered = []
        
        if not self.plugins_dir.exists():
            logger.warning(f"⚠️ Plugins directory not found: {self.plugins_dir}")
            return discovered
        
        # Add plugins directory to Python path
        if str(self.plugins_dir) not in sys.path:
            sys.path.insert(0, str(self.plugins_dir))
        
        # Find all Python files in plugins directory
        for file_path in self.plugins_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue  # Skip __init__.py and private files
            
            module_name = file_path.stem
            discovered.append(module_name)
        
        logger.info(f"🔍 Discovered {len(discovered)} plugin(s): {discovered}")
        return discovered
    
    def load_plugin(self, module_name: str) -> Optional[ArbiterPlugin]:
        """
        Load a plugin from module name.
        
        Args:
            module_name: Name of the plugin module
            
        Returns:
            Loaded plugin instance or None if failed
        """
        if module_name in self.disabled_plugins:
            logger.info(f"⏭️ Plugin '{module_name}' is disabled, skipping")
            return None
        
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            # Find plugin class (subclass of ArbiterPlugin)
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, ArbiterPlugin) and 
                    attr is not ArbiterPlugin):
                    plugin_class = attr
                    break
            
            if plugin_class is None:
                raise PluginLoadError(f"No ArbiterPlugin subclass found in {module_name}")
            
            # Instantiate plugin
            plugin = plugin_class()
            
            # Initialize plugin
            if not plugin.initialize(self.workspace):
                raise PluginLoadError(f"Plugin initialization failed: {module_name}")
            
            # Store plugin
            plugin_name = plugin.metadata.name
            self.plugins[plugin_name] = plugin
            
            logger.info(f"✅ Loaded plugin: {plugin_name} v{plugin.metadata.version}")
            return plugin
            
        except Exception as e:
            logger.error(f"❌ Failed to load plugin '{module_name}': {str(e)}")
            return None
    
    def load_all_plugins(self) -> int:
        """
        Discover and load all plugins.
        
        Returns:
            Number of successfully loaded plugins
        """
        discovered = self.discover_plugins()
        loaded_count = 0
        
        for module_name in discovered:
            if self.load_plugin(module_name):
                loaded_count += 1
        
        logger.info(f"📦 Loaded {loaded_count}/{len(discovered)} plugin(s)")
        return loaded_count
    
    def get_plugin(self, name: str) -> Optional[ArbiterPlugin]:
        """
        Get loaded plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(name)
    
    def has_plugin(self, name: str) -> bool:
        """Check if plugin is loaded."""
        return name in self.plugins
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all loaded plugins with metadata.
        
        Returns:
            List of plugin metadata dictionaries
        """
        return [
            {
                **plugin.metadata.to_dict(),
                "description_for_llm": plugin.describe()
            }
            for plugin in self.plugins.values()
        ]
    
    def execute_plugin(self, name: str, **kwargs) -> PluginResult:
        """
        Execute a plugin with validation.
        
        Args:
            name: Plugin name
            **kwargs: Plugin-specific parameters
            
        Returns:
            PluginResult
        """
        # Check if plugin exists
        plugin = self.get_plugin(name)
        if plugin is None:
            return PluginResult(
                success=False,
                error=f"Plugin '{name}' not found"
            )
        
        try:
            # Validate input
            is_valid, error_msg = plugin.validate_input(**kwargs)
            if not is_valid:
                return PluginResult(
                    success=False,
                    error=f"Validation failed: {error_msg}"
                )
            
            # Execute plugin
            logger.info(f"🔧 Executing plugin: {name}")
            result = plugin.execute(**kwargs)
            
            if result.success:
                logger.info(f"✅ Plugin '{name}' executed successfully")
            else:
                logger.warning(f"⚠️ Plugin '{name}' execution failed: {result.error}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Plugin '{name}' execution error: {str(e)}")
            return PluginResult(
                success=False,
                error=f"Execution error: {str(e)}"
            )
    
    def enable_plugin(self, name: str) -> bool:
        """Enable a disabled plugin."""
        if name in self.disabled_plugins:
            self.disabled_plugins.remove(name)
            logger.info(f"✅ Enabled plugin: {name}")
            return True
        return False
    
    def disable_plugin(self, name: str) -> bool:
        """Disable a plugin."""
        if name in self.plugins:
            self.disabled_plugins.add(name)
            # Cleanup and remove
            self.plugins[name].cleanup()
            del self.plugins[name]
            logger.info(f"🚫 Disabled plugin: {name}")
            return True
        return False
    
    def reload_plugin(self, name: str) -> bool:
        """Reload a plugin."""
        # Find module name for this plugin
        module_name = None
        for plugin in self.plugins.values():
            if plugin.metadata.name == name:
                module_name = plugin.__class__.__module__
                break
        
        if module_name:
            self.disable_plugin(name)
            return self.load_plugin(module_name) is not None
        
        return False
    
    def cleanup_all(self) -> None:
        """Cleanup all plugins."""
        for plugin in self.plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up plugin {plugin.metadata.name}: {e}")
        
        self.plugins.clear()
        logger.info("🧹 All plugins cleaned up")


# Example usage
if __name__ == "__main__":
    # Create plugin manager
    manager = PluginManager(workspace="/tmp/test_workspace")
    
    # Load all plugins
    loaded = manager.load_all_plugins()
    print(f"\nLoaded {loaded} plugin(s)")
    
    # List plugins
    print("\n📋 Available Plugins:")
    for plugin_info in manager.list_plugins():
        print(f"  - {plugin_info['name']} v{plugin_info['version']}")
        print(f"    {plugin_info['description']}")
    
    # Execute example plugin (if available)
    if manager.has_plugin("example"):
        print("\n🧪 Testing example plugin:")
        result = manager.execute_plugin("example", message="Hello from PluginManager!")
        print(f"  Success: {result.success}")
        print(f"  Output: {result.output}")
    
    # Cleanup
    manager.cleanup_all()

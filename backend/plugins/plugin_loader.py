import os
import importlib.util
import inspect
from typing import Dict, Any, List, Type
from ..agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class PluginAgentLoader:
    """Dynamic plugin system for loading custom agents"""
    
    def __init__(self, plugins_directory: str = "./plugins"):
        self.plugins_directory = plugins_directory
        self.loaded_plugins = {}
        self.plugin_registry = {}
        
        # Ensure plugins directory exists
        os.makedirs(plugins_directory, exist_ok=True)
        
        # Create example plugin if directory is empty
        self._create_example_plugin()
    
    def _create_example_plugin(self):
        """Create an example plugin for reference"""
        example_plugin_path = os.path.join(self.plugins_directory, "example_agent.py")
        
        if not os.path.exists(example_plugin_path):
            example_code = '''
from typing import Dict, Any
import asyncio
from backend.agents.base_agent import BaseAgent

class ExampleCustomAgent(BaseAgent):
    """Example custom agent plugin"""
    
    def __init__(self, config):
        super().__init__("Example Custom Agent", config)
        self.description = "An example custom agent that demonstrates the plugin system"
        self.version = "1.0.0"
        self.author = "Plugin Developer"
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return result"""
        query = input_data.get("query", "")
        
        # Custom processing logic here
        result = f"Custom processing result for: {query}"
        
        return {
            "custom_result": result,
            "agent_name": self.name,
            "processed_query": query,
            "confidence": 0.9
        }
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return ["custom_processing", "example_functionality"]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return agent metadata"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "capabilities": self.get_capabilities()
        }

# Plugin registration function (required)
def register_plugin():
    """Register this plugin with the system"""
    return {
        "agent_class": ExampleCustomAgent,
        "name": "example_custom_agent",
        "description": "Example custom agent for demonstration",
        "version": "1.0.0"
    }
'''
            
            try:
                with open(example_plugin_path, 'w') as f:
                    f.write(example_code)
                logger.info("Created example plugin at: " + example_plugin_path)
            except Exception as e:
                logger.error(f"Failed to create example plugin: {str(e)}")
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugin files"""
        plugins = []
        
        if not os.path.exists(self.plugins_directory):
            return plugins
        
        for filename in os.listdir(self.plugins_directory):
            if filename.endswith('.py') and not filename.startswith('__'):
                plugin_path = os.path.join(self.plugins_directory, filename)
                plugins.append(plugin_path)
        
        return plugins
    
    def load_plugin(self, plugin_path: str) -> Dict[str, Any]:
        """Load a single plugin"""
        try:
            # Get plugin name from filename
            plugin_name = os.path.splitext(os.path.basename(plugin_path))[0]
            
            # Load module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if plugin has register_plugin function
            if not hasattr(module, 'register_plugin'):
                raise Exception("Plugin must have a 'register_plugin' function")
            
            # Register plugin
            plugin_info = module.register_plugin()
            
            # Validate plugin info
            required_keys = ['agent_class', 'name', 'description', 'version']
            for key in required_keys:
                if key not in plugin_info:
                    raise Exception(f"Plugin registration missing required key: {key}")
            
            # Validate agent class
            agent_class = plugin_info['agent_class']
            if not issubclass(agent_class, BaseAgent):
                raise Exception("Agent class must inherit from BaseAgent")
            
            # Store plugin
            self.loaded_plugins[plugin_info['name']] = {
                'module': module,
                'agent_class': agent_class,
                'info': plugin_info,
                'path': plugin_path
            }
            
            logger.info(f"Successfully loaded plugin: {plugin_info['name']}")
            return plugin_info
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_path}: {str(e)}")
            return None
    
    def load_all_plugins(self) -> Dict[str, Any]:
        """Load all discovered plugins"""
        plugins = self.discover_plugins()
        loaded_count = 0
        
        for plugin_path in plugins:
            if self.load_plugin(plugin_path):
                loaded_count += 1
        
        logger.info(f"Loaded {loaded_count} plugins from {len(plugins)} discovered")
        
        return {
            "total_discovered": len(plugins),
            "successfully_loaded": loaded_count,
            "loaded_plugins": list(self.loaded_plugins.keys())
        }
    
    def create_agent_instance(self, plugin_name: str, config: Any) -> BaseAgent:
        """Create an instance of a plugin agent"""
        if plugin_name not in self.loaded_plugins:
            raise Exception(f"Plugin not found: {plugin_name}")
        
        plugin_data = self.loaded_plugins[plugin_name]
        agent_class = plugin_data['agent_class']
        
        return agent_class(config)
    
    def get_plugin_info(self, plugin_name: str) -> Dict[str, Any]:
        """Get information about a specific plugin"""
        if plugin_name not in self.loaded_plugins:
            return None
        
        return self.loaded_plugins[plugin_name]['info']
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins"""
        return [plugin_data['info'] for plugin_data in self.loaded_plugins.values()]
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""
        if plugin_name in self.loaded_plugins:
            del self.loaded_plugins[plugin_name]
            logger.info(f"Unloaded plugin: {plugin_name}")
            return True
        return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin"""
        if plugin_name not in self.loaded_plugins:
            return False
        
        plugin_path = self.loaded_plugins[plugin_name]['path']
        self.unload_plugin(plugin_name)
        
        return self.load_plugin(plugin_path) is not None
    
    def validate_plugin_compatibility(self, plugin_path: str) -> Dict[str, Any]:
        """Validate plugin compatibility without loading"""
        try:
            # Basic file checks
            if not os.path.exists(plugin_path):
                return {"valid": False, "error": "Plugin file not found"}
            
            if not plugin_path.endswith('.py'):
                return {"valid": False, "error": "Plugin must be a Python file"}
            
            # Try to parse the file
            with open(plugin_path, 'r') as f:
                content = f.read()
            
            # Check for required components
            if 'register_plugin' not in content:
                return {"valid": False, "error": "Missing register_plugin function"}
            
            if 'BaseAgent' not in content:
                return {"valid": False, "error": "Must import BaseAgent"}
            
            return {"valid": True, "message": "Plugin appears compatible"}
            
        except Exception as e:
            return {"valid": False, "error": str(e)}

# Global plugin loader instance
plugin_loader = PluginAgentLoader()
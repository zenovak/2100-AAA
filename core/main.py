import os
import json
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
from functools import wraps


class AgentType(Enum):
    TASK = "task"
    CONVERSATION = "conversation"
    SEARCH = "search"
    REASONING = "reasoning"
    CREATIVE = "creative"
    CUSTOM = "custom"


class AgentAPI:
    """
    Main class for the Agent of All Agents API
    Provides core functionality for registering and executing functions
    """
    
    def __init__(self):
        self.urfn_registry = {}
        self.registered_agents = {}
        self.api_augmentations = {}
        self._load_registry()
    
    def _load_registry(self):
        """Load the URFN registry from file if it exists"""
        if os.path.exists("urfn_registry.json"):
            with open("urfn_registry.json", "r") as f:
                self.urfn_registry = json.load(f)
    
    def _save_registry(self):
        """Save the URFN registry to file"""
        with open("urfn_registry.json", "w") as f:
            json.dump(self.urfn_registry, f, indent=2)
    
    def register_agent(self, agent_name: str, agent_type: AgentType, description: str):
        """
        Decorator for registering a new agent
        
        Args:
            agent_name: Unique name for the agent
            agent_type: Type of agent from AgentType enum
            description: Short description of the agent's purpose
        
        Returns:
            Decorator function
        """
        def decorator(agent_class):
            if agent_name in self.registered_agents:
                raise ValueError(f"Agent with name '{agent_name}' already exists")
            
            self.registered_agents[agent_name] = {
                "class": agent_class,
                "type": agent_type,
                "description": description,
                "functions": {}
            }
            
            return agent_class
        return decorator
    
    def register_function(self, function_name: str, description: str):
        """
        Decorator for registering a function with the API
        
        Args:
            function_name: Name for the function, should follow urfn_ convention
            description: Short description of the function's purpose
        
        Returns:
            Decorator function
        """
        def decorator(func):
            if not function_name.startswith("urfn_"):
                raise ValueError("Function name must start with 'urfn_'")
            
            # Extract module and function info
            module_name = func.__module__
            func_name = func.__name__
            sig = inspect.signature(func)
            
            # Create registry entry
            self.urfn_registry[function_name] = {
                "description": description,
                "module": module_name,
                "function": func_name,
                "parameters": {
                    name: {
                        "type": str(param.annotation.__name__ if param.annotation is not inspect.Parameter.empty else "any"),
                        "required": param.default is inspect.Parameter.empty
                    } for name, param in sig.parameters.items()
                }
            }
            
            # Save updated registry
            self._save_registry()
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def augment_api(self, endpoint: str, method: str = "POST"):
        """
        Decorator for adding API augmentations
        
        Args:
            endpoint: API endpoint path
            method: HTTP method (default: POST)
        
        Returns:
            Decorator function
        """
        def decorator(func):
            if endpoint in self.api_augmentations:
                raise ValueError(f"Endpoint '{endpoint}' already exists")
            
            self.api_augmentations[endpoint] = {
                "method": method,
                "function": func,
                "module": func.__module__,
                "docstring": func.__doc__ or ""
            }
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
        return decorator

    def execute_function(self, function_name: str, **params):
        """
        Execute a registered function by its URFN
        
        Args:
            function_name: Unique Reserved Function Name
            **params: Parameters to pass to the function
        
        Returns:
            Function result
        """
        if function_name not in self.urfn_registry:
            raise ValueError(f"Function '{function_name}' not found in registry")
        
        func_info = self.urfn_registry[function_name]
        module_name = func_info["module"]
        func_name = func_info["function"]
        
        # Import the module and get the function
        module = __import__(module_name, fromlist=[func_name])
        func = getattr(module, func_name)
        
        # Execute the function
        return func(**params)
    
    def list_agents(self) -> Dict[str, Dict]:
        """List all registered agents with their details"""
        return {
            name: {
                "type": info["type"].value, 
                "description": info["description"],
                "functions": list(info["functions"].keys())
            } 
            for name, info in self.registered_agents.items()
        }
    
    def list_functions(self) -> Dict[str, Dict]:
        """List all registered functions with their details"""
        return self.urfn_registry
    
    def get_api_documentation(self) -> Dict[str, Dict]:
        """Generate documentation for all API endpoints"""
        return {
            endpoint: {
                "method": info["method"],
                "description": info["docstring"],
                "module": info["module"]
            }
            for endpoint, info in self.api_augmentations.items()
        }


# Create a global instance of the API
agent_api = AgentAPI()


class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
        if name not in agent_api.registered_agents:
            raise ValueError(f"Agent '{name}' not registered")
        
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent with the given input data
        
        Args:
            input_data: Input parameters for the agent
            
        Returns:
            Agent output
        """
        raise NotImplementedError("Subclasses must implement run()")
    
    def call_function(self, function_name: str, **params) -> Any:
        """
        Call a registered function by its URFN
        
        Args:
            function_name: Function name to call
            **params: Parameters to pass to the function
            
        Returns:
            Function result
        """
        return agent_api.execute_function(function_name, **params)


# Example of implementing a custom agent
@agent_api.register_agent(
    agent_name="text_processor",
    agent_type=AgentType.TASK,
    description="Agent that processes text for various operations"
)
class TextProcessorAgent(BaseAgent):
    """Sample text processing agent"""
    
    def __init__(self):
        super().__init__("text_processor")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input text"""
        if "text" not in input_data:
            return {"error": "Input must contain 'text' key"}
        
        text = input_data["text"]
        operation = input_data.get("operation", "summarize")
        
        if operation == "summarize":
            result = self.call_function("urfn_summarize_text", input_text=text)
        elif operation == "analyze":
            result = self.call_function("urfn_analyze_text", input_text=text)
        else:
            result = {"error": f"Unknown operation: {operation}"}
        
        return result


# Example function registration
@agent_api.register_function(
    function_name="urfn_summarize_text", 
    description="Summarizes the input text"
)
def urfn_summarize_text(input_text: str) -> Dict[str, str]:
    """
    Summarize the input text and return a concise version
    
    Args:
        input_text: The text to summarize
        
    Returns:
        Dictionary with summary key
    """
    # In a real implementation, this would use an AI model or algorithm
    summary = input_text[:100] + "..." if len(input_text) > 100 else input_text
    return {"summary": summary}


# Example API augmentation
@agent_api.augment_api(endpoint="/v1/augment/text-processor")
def process_text(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process text using available text processing functions
    
    Args:
        data: Dictionary containing 'text' and optional 'operation'
        
    Returns:
        Processing result
    """
    agent = TextProcessorAgent()
    return agent.run(data)


# Usage example
if __name__ == "__main__":
    # Create and use agent
    text_agent = TextProcessorAgent()
    result = text_agent.run({
        "text": "This is a long text that needs to be processed for demonstration purposes.",
        "operation": "summarize"
    })
    print(result)
    
    # List registered agents
    print("\nRegistered Agents:")
    print(json.dumps(agent_api.list_agents(), indent=2))
    
    # List registered functions
    print("\nRegistered Functions:")
    print(json.dumps(agent_api.list_functions(), indent=2))

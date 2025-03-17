import os
import json
import inspect
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
from functools import wraps
from fastapi import FastAPI, HTTPException, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import datetime


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
        self.deployments = {}
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


# ----------------------------------------------------------------------------
# Agent Deployment API - New functionality 
# ----------------------------------------------------------------------------

# Define Pydantic models for request/response handling
class DeploymentConfig(BaseModel):
    name: str = Field(..., description="Unique name for the agent")
    type: str = Field(..., description="Type of agent (task, conversation, search, reasoning, creative, custom)")
    description: str = Field(..., description="Short description of the agent's purpose")
    functions: List[str] = Field(default=[], description="List of URFN functions the agent can use")
    system_prompt: Optional[str] = Field(default=None, description="Optional system prompt for the agent")
    config: Dict[str, Any] = Field(default={}, description="Additional configuration parameters")


class DeploymentResponse(BaseModel):
    id: str = Field(..., description="Unique ID for the deployed agent")
    name: str = Field(..., description="Name of the agent")
    type: str = Field(..., description="Type of agent")
    description: str = Field(..., description="Description of the agent")
    status: str = Field(..., description="Status of the deployment")
    created_at: str = Field(..., description="ISO timestamp when the agent was created")


class DeploymentListResponse(BaseModel):
    data: List[DeploymentResponse] = Field(..., description="List of deployed agents")


# Create a FastAPI app that will be used with the agent_api
app = FastAPI(title="Agent of All Agents API", version="1.0.0")


# Helper function to convert between our AgentType enum and string values
def get_agent_type(type_str: str) -> AgentType:
    """Convert string agent type to AgentType enum"""
    type_mapping = {
        "task": AgentType.TASK,
        "conversation": AgentType.CONVERSATION,
        "search": AgentType.SEARCH,
        "reasoning": AgentType.REASONING,
        "creative": AgentType.CREATIVE,
        "custom": AgentType.CUSTOM
    }
    
    if type_str.lower() not in type_mapping:
        raise ValueError(f"Invalid agent type: {type_str}. Must be one of: {', '.join(type_mapping.keys())}")
    
    return type_mapping[type_str.lower()]


# Dynamically generate an agent class based on deployment config
def generate_agent_class(deployment_config: DeploymentConfig) -> type:
    """Generate a new agent class based on deployment configuration"""
    
    class DynamicAgent(BaseAgent):
        """Dynamically generated agent class"""
        
        def __init__(self):
            super().__init__(deployment_config.name)
            self.config = deployment_config.config
            self.system_prompt = deployment_config.system_prompt
            self.functions = deployment_config.functions
        
        def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            """Execute the agent with the given input data"""
            # Process the input data
            result = {"agent": self.name, "processed": True}
            
            # Call each function that the agent has access to
            function_results = {}
            for function_name in self.functions:
                if function_name in agent_api.urfn_registry:
                    try:
                        # Extract parameters from input_data that match function parameters
                        func_info = agent_api.urfn_registry[function_name]
                        func_params = {
                            param: input_data.get(param)
                            for param in func_info["parameters"]
                            if param in input_data
                        }
                        
                        # Call the function
                        function_result = self.call_function(function_name, **func_params)
                        function_results[function_name] = function_result
                    except Exception as e:
                        function_results[function_name] = {"error": str(e)}
            
            # Combine results
            result["function_results"] = function_results
            result["input"] = input_data
            
            return result
    
    # Set the class name and docstring
    DynamicAgent.__name__ = f"{deployment_config.name.title().replace(' ', '')}Agent"
    DynamicAgent.__doc__ = deployment_config.description
    
    return DynamicAgent


# Deploy endpoint compatible with OpenAI API style
@app.post("/v1/agents/deploy", response_model=DeploymentResponse)
async def deploy_agent(
    request: Request,
    deployment_config: DeploymentConfig = Body(...),
):
    """
    Deploy a new agent with the specified configuration.
    
    This endpoint follows OpenAI API conventions for request and response formats.
    """
    try:
        # Verify functions exist
        for function_name in deployment_config.functions:
            if function_name not in agent_api.urfn_registry:
                raise HTTPException(
                    status_code=400,
                    detail=f"Function '{function_name}' not found in registry"
                )
        
        # Convert string type to AgentType enum
        agent_type = get_agent_type(deployment_config.type)
        
        # Generate the agent class
        agent_class = generate_agent_class(deployment_config)
        
        # Register the agent
        agent_api.register_agent(
            agent_name=deployment_config.name,
            agent_type=agent_type,
            description=deployment_config.description
        )(agent_class)
        
        # Create deployment record
        agent_id = str(uuid.uuid4())
        current_time = datetime.datetime.now().isoformat()
        deployment = {
            "id": agent_id,
            "name": deployment_config.name,
            "type": deployment_config.type,
            "description": deployment_config.description,
            "status": "active",
            "created_at": current_time
        }
        
        # Store in deployments dictionary
        agent_api.deployments[agent_id] = deployment
        
        return deployment
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deploying agent: {str(e)}")


# List deployed agents
@app.get("/v1/agents", response_model=DeploymentListResponse)
async def list_deployments():
    """List all deployed agents"""
    return {"data": list(agent_api.deployments.values())}


# Get information about a specific deployed agent
@app.get("/v1/agents/{agent_id}", response_model=DeploymentResponse)
async def get_deployment(agent_id: str):
    """Get information about a specific deployed agent"""
    if agent_id not in agent_api.deployments:
        raise HTTPException(status_code=404, detail=f"Agent with ID '{agent_id}' not found")
    
    return agent_api.deployments[agent_id]


# Delete a deployed agent
@app.delete("/v1/agents/{agent_id}")
async def delete_deployment(agent_id: str):
    """Delete a deployed agent"""
    if agent_id not in agent_api.deployments:
        raise HTTPException(status_code=404, detail=f"Agent with ID '{agent_id}' not found")
    
    # Get the agent name to remove from registered agents
    agent_name = agent_api.deployments[agent_id]["name"]
    
    # Remove from registered agents
    if agent_name in agent_api.registered_agents:
        del agent_api.registered_agents[agent_name]
    
    # Remove from deployments
    del agent_api.deployments[agent_id]
    
    return {"status": "success", "message": f"Agent '{agent_name}' successfully deleted"}


# Execute a deployed agent
@app.post("/v1/agents/{agent_id}/run")
async def run_agent(
    agent_id: str,
    input_data: Dict[str, Any] = Body(...),
):
    """Run a deployed agent with the given input data"""
    if agent_id not in agent_api.deployments:
        raise HTTPException(status_code=404, detail=f"Agent with ID '{agent_id}' not found")
    
    agent_name = agent_api.deployments[agent_id]["name"]
    
    if agent_name not in agent_api.registered_agents:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found in registered agents"
        )
    
    try:
        # Create agent instance
        agent_class = agent_api.registered_agents[agent_name]["class"]
        agent = agent_class()
        
        # Run agent
        result = agent.run(input_data)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running agent: {str(e)}")


# Add an OpenAI-compatible completion endpoint that can route to agents
@app.post("/v1/completions")
async def openai_compatible_completion(request: Request):
    """
    OpenAI-compatible completions endpoint that routes to appropriate agents
    
    This accepts OpenAI API formatted requests and routes them to the appropriate agent
    """
    try:
        # Parse request body
        body = await request.json()
        
        # Extract model field which we'll use to determine which agent to call
        model = body.get("model", "")
        
        # Check if this is an agent reference (format: agent:name)
        if model.startswith("agent:"):
            agent_name = model.split(":", 1)[1]
            
            # Check if agent exists
            if agent_name not in agent_api.registered_agents:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Agent '{agent_name}' not found"
                )
            
            # Create agent instance
            agent_class = agent_api.registered_agents[agent_name]["class"]
            agent = agent_class()
            
            # Extract prompt from the request
            prompt = body.get("prompt", "")
            if not prompt:
                # Try messages format
                messages = body.get("messages", [])
                prompt = "\n".join([m.get("content", "") for m in messages if m.get("content")])
            
            # Run agent
            input_data = {"text": prompt}
            # Add any additional parameters from the request
            for key, value in body.items():
                if key not in ["model", "prompt", "messages"]:
                    input_data[key] = value
                    
            result = agent.run(input_data)
            
            # Format result in OpenAI-compatible format
            response_text = ""
            if isinstance(result, dict):
                if "summary" in result:
                    response_text = result["summary"]
                elif "response" in result:
                    response_text = result["response"]
                else:
                    response_text = json.dumps(result)
            else:
                response_text = str(result)
                
            return {
                "id": f"cmpl-{uuid.uuid4()}",
                "object": "text_completion",
                "created": int(datetime.datetime.now().timestamp()),
                "model": model,
                "choices": [
                    {
                        "text": response_text,
                        "index": 0,
                        "logprobs": None,
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(prompt) // 4,  # Very rough estimate
                    "completion_tokens": len(response_text) // 4,
                    "total_tokens": (len(prompt) + len(response_text)) // 4
                }
            }
        else:
            # Not an agent model, return error
            raise HTTPException(
                status_code=400,
                detail=f"Model '{model}' is not a valid agent. Use format 'agent:name'"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


# Add all registered API augmentations to the FastAPI app
def register_api_augmentations():
    for endpoint, info in agent_api.api_augmentations.items():
        # Create a route handler for each augmentation
        async def route_handler(request: Request, endpoint_info=info):
            try:
                # Parse request body
                body = await request.json()
                
                # Call the function
                result = endpoint_info["function"](body)
                
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
        
        # Add the route to the app
        app.add_api_route(
            endpoint,
            route_handler,
            methods=[info["method"]],
            description=info["docstring"]
        )


# Register API augmentations
@app.on_event("startup")
async def startup_event():
    register_api_augmentations()


# Usage example
if __name__ == "__main__":
    import uvicorn
    
    # Example of direct usage without API
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
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)

import json
import re
from typing import Dict, List, Any, Optional, Tuple, Union
import uuid
from fastapi import FastAPI, HTTPException, Body, Request, Depends
from pydantic import BaseModel, Field


# Agent Matching System
class TaskMatcher:
    """
    Matches user prompts to appropriate agents based on task identification
    """
    
    def __init__(self, agent_registry: Dict[str, Any], editor_config: Dict[str, Any]):
        self.agent_registry = agent_registry
        self.editor_config = editor_config
        self.task_patterns = self._build_task_patterns()
    
    def _build_task_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Build regex patterns and keywords for task identification"""
        patterns = {}
        
        # Build from editor config types
        for config_type, config in self.editor_config.items():
            # Extract keywords from fields, labels, and descriptions
            keywords = set()
            fields = config.get("fields", [])
            for field in fields:
                keywords.add(field.get("id", "").lower())
                keywords.add(field.get("label", "").lower())
            
            # Add config type itself as keyword
            keywords.add(config_type.lower())
            
            # Get concepts from prompts
            system_prompt = config.get("prompts", {}).get("system", "")
            user_prompt = config.get("prompts", {}).get("user", "")
            
            # Extract key actions and concepts
            action_matches = re.findall(r'Create a ([a-zA-Z\s]+)', system_prompt)
            for match in action_matches:
                keywords.add(match.strip().lower())
            
            # Create regex pattern
            keyword_pattern = r'|'.join([rf'\b{re.escape(kw)}\b' for kw in keywords if kw and len(kw) > 3])
            
            patterns[config_type] = {
                "pattern": keyword_pattern,
                "keywords": list(keywords),
                "task_type": config_type,
                "fields": fields,
                "prompts": config.get("prompts", {}),
                "defaults": config.get("defaults", {})
            }
        
        # Add patterns for registered agents
        for agent_name, agent_info in self.agent_registry.items():
            agent_description = agent_info.get("description", "")
            agent_type = agent_info.get("type", "")
            
            keywords = set()
            keywords.add(agent_name.lower())
            
            # Extract keywords from description
            description_words = re.findall(r'\b\w+\b', agent_description.lower())
            for word in description_words:
                if len(word) > 4:  # Only add meaningful words
                    keywords.add(word)
            
            # Create regex pattern
            keyword_pattern = r'|'.join([rf'\b{re.escape(kw)}\b' for kw in keywords if kw and len(kw) > 3])
            
            patterns[agent_name] = {
                "pattern": keyword_pattern,
                "keywords": list(keywords),
                "task_type": "agent",
                "agent_name": agent_name,
                "agent_description": agent_description,
                "agent_type": agent_type
            }
        
        return patterns
    
    def match_task(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Match the input prompt to appropriate tasks/agents
        
        Args:
            prompt: User input prompt
            
        Returns:
            List of matching tasks/agents with confidence scores
        """
        matches = []
        prompt_lower = prompt.lower()
        
        for task_id, task_info in self.task_patterns.items():
            pattern = task_info["pattern"]
            if not pattern:  # Skip if pattern is empty
                continue
                
            # Find all matches
            found_matches = re.findall(pattern, prompt_lower)
            
            if found_matches:
                # Calculate confidence based on number and diversity of matches
                unique_matches = set(found_matches)
                match_count = len(found_matches)
                unique_count = len(unique_matches)
                
                # Higher score for more unique matches
                confidence = (match_count * 0.4) + (unique_count * 0.6)
                
                # Cap confidence at 1.0
                confidence = min(confidence, 1.0)
                
                # Add task to matches
                matches.append({
                    "task_id": task_id,
                    "confidence": confidence,
                    "task_info": task_info,
                    "matched_keywords": list(unique_matches)
                })
        
        # Sort by confidence
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        
        return matches
    
    def extract_parameters(self, prompt: str, task_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract parameters for a task from the prompt
        
        Args:
            prompt: User input prompt
            task_info: Task information from match_task
            
        Returns:
            Dictionary of extracted parameters
        """
        params = {}
        task_type = task_info.get("task_type")
        
        # If task is from editor config, extract parameters based on fields
        if task_type != "agent" and "fields" in task_info:
            fields = task_info["fields"]
            
            # Go through each field and try to extract values
            for field in fields:
                field_id = field.get("id")
                field_label = field.get("label")
                field_type = field.get("type")
                
                # Skip if no id
                if not field_id:
                    continue
                
                # Try different patterns to extract values
                value = None
                
                # Try pattern: [field_label]: [value]
                if field_label:
                    pattern = rf'{re.escape(field_label)}:?\s*(.+?)(?:\n|$)'
                    match = re.search(pattern, prompt, re.IGNORECASE)
                    if match:
                        value = match.group(1).strip()
                
                # Try pattern: [field_id]: [value]
                if not value:
                    pattern = rf'{re.escape(field_id)}:?\s*(.+?)(?:\n|$)'
                    match = re.search(pattern, prompt, re.IGNORECASE)
                    if match:
                        value = match.group(1).strip()
                
                # For select fields, try to match from options
                if not value and field_type == "select" and "options" in field:
                    options = field["options"]
                    for option in options:
                        if re.search(rf'\b{re.escape(option)}\b', prompt, re.IGNORECASE):
                            value = option
                            break
                
                # If we found a value, add it to params
                if value:
                    params[field_id] = value
                elif "defaults" in task_info and field_id in task_info["defaults"]:
                    # Use default if available
                    params[field_id] = task_info["defaults"][field_id]
        
        # If it's an agent, extract operation if mentioned
        elif task_type == "agent":
            # Try to identify operation
            operations = ["summarize", "analyze", "process", "generate", "create"]
            for op in operations:
                if re.search(rf'\b{re.escape(op)}\b', prompt, re.IGNORECASE):
                    params["operation"] = op
                    break
            
            # Always include the text
            params["text"] = prompt
        
        return params


# Models for API requests/responses
class AgentSearchRequest(BaseModel):
    prompt: str = Field(..., description="User input prompt to analyze")
    max_results: int = Field(3, description="Maximum number of results to return")
    min_confidence: float = Field(0.2, description="Minimum confidence score for results")


class AgentSearchMatch(BaseModel):
    task_id: str = Field(..., description="ID of the matched task or agent")
    confidence: float = Field(..., description="Confidence score for the match")
    matched_keywords: List[str] = Field(..., description="Keywords that matched in the prompt")
    parameters: Dict[str, Any] = Field(..., description="Extracted parameters for the task")
    task_type: str = Field(..., description="Type of task (agent or editor config type)")


class AgentSearchResponse(BaseModel):
    matches: List[AgentSearchMatch] = Field(..., description="List of matched tasks/agents")


class MultiAgentRequest(BaseModel):
    prompt: str = Field(..., description="User input prompt")
    agent_sequence: Optional[List[str]] = Field(None, description="Optional sequence of agents to use")
    auto_sequence: bool = Field(True, description="Automatically determine agent sequence")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for response")
    temperature: Optional[float] = Field(None, description="Temperature for response generation")


class MultiAgentResponse(BaseModel):
    id: str = Field(..., description="Response ID")
    result: str = Field(..., description="Final result")
    agents_used: List[Dict[str, Any]] = Field(..., description="Agents used in processing")
    tokens: Dict[str, int] = Field(..., description="Token usage information")


# Add agent search endpoints to FastAPI app
def add_agent_search_endpoints(app: FastAPI, agent_api: Any, editor_config: Dict[str, Any]):
    """
    Add agent search endpoints to FastAPI app
    
    Args:
        app: FastAPI application
        agent_api: Agent API instance
        editor_config: Editor configuration
    """
    # Initialize task matcher
    task_matcher = TaskMatcher(agent_api.registered_agents, editor_config)
    
    @app.post("/v1/agents/search", response_model=AgentSearchResponse)
    async def search_agents(request: AgentSearchRequest = Body(...)):
        """
        Search for agents and tasks that match the given prompt
        """
        try:
            # Match tasks to the prompt
            matches = task_matcher.match_task(request.prompt)
            
            # Filter by confidence
            matches = [m for m in matches if m["confidence"] >= request.min_confidence]
            
            # Limit results
            matches = matches[:request.max_results]
            
            # Extract parameters for each match
            results = []
            for match in matches:
                task_info = match["task_info"]
                parameters = task_matcher.extract_parameters(request.prompt, task_info)
                
                results.append({
                    "task_id": match["task_id"],
                    "confidence": match["confidence"],
                    "matched_keywords": match["matched_keywords"],
                    "parameters": parameters,
                    "task_type": task_info.get("task_type", "unknown")
                })
            
            return {"matches": results}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error searching agents: {str(e)}")
    
    @app.post("/v1/multi-agent/run", response_model=MultiAgentResponse)
    async def run_multi_agent(request: MultiAgentRequest = Body(...)):
        """
        Process input using multiple agents in sequence
        """
        try:
            agent_sequence = []
            prompt = request.prompt
            results = []
            
            # Determine agent sequence
            if request.agent_sequence:
                # Use provided sequence
                agent_sequence = request.agent_sequence
            elif request.auto_sequence:
                # Auto-determine sequence
                matches = task_matcher.match_task(prompt)
                
                # Filter and extract agent IDs
                matches = [m for m in matches if m["confidence"] >= 0.3]
                for match in matches:
                    task_info = match["task_info"]
                    task_type = task_info.get("task_type")
                    
                    if task_type == "agent":
                        agent_sequence.append(task_info.get("agent_name"))
                    else:
                        # For editor configs, create/deploy a dynamic agent
                        from universal_model_integration import register_dynamic_agent_from_editor_config
                        parameters = task_matcher.extract_parameters(prompt, task_info)
                        agent_id = register_dynamic_agent_from_editor_config(
                            match["task_id"], 
                            editor_config, 
                            prompt, 
                            parameters
                        )
                        agent_sequence.append(agent_id)
            
            if not agent_sequence:
                raise HTTPException(
                    status_code=400,
                    detail="Could not determine agent sequence. Please specify agent_sequence."
                )
            
            # Process through the sequence
            current_text = prompt
            agents_used = []
            
            for agent_id in agent_sequence:
                # Check if agent exists
                if agent_id not in agent_api.registered_agents:
                    # Check if it's a deployed agent
                    if not hasattr(agent_api, "deployments") or agent_id not in agent_api.deployments:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Agent '{agent_id}' not found"
                        )
                    
                    # Get the agent from deployments
                    agent_name = agent_api.deployments[agent_id]["name"]
                    if agent_name not in agent_api.registered_agents:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Agent '{agent_name}' not found in registered agents"
                        )
                    
                    # Create agent instance
                    agent_class = agent_api.registered_agents[agent_name]["class"]
                    agent = agent_class()
                else:
                    # Create agent instance
                    agent_class = agent_api.registered_agents[agent_id]["class"]
                    agent = agent_class()
                
                # Extract parameters
                task_info = {
                    "task_type": "agent",
                    "agent_name": agent_id
                }
                params = task_matcher.extract_parameters(current_text, task_info)
                params["text"] = current_text
                
                # Run agent
                result = agent.run(params)
                
                # Record agent usage
                agents_used.append({
                    "agent_id": agent_id,
                    "parameters": params,
                    "step": len(agents_used) + 1
                })
                
                # Extract result text for next agent
                if isinstance(result, dict):
                    if "summary" in result:
                        current_text = result["summary"]
                    elif "response" in result:
                        current_text = result["response"]
                    elif "result" in result:
                        current_text = result["result"]
                    else:
                        current_text = json.dumps(result)
                else:
                    current_text = str(result)
                
                results.append(current_text)
            
            # Create response
            response_id = f"multiagent-{uuid.uuid4()}"
            
            # Rough token calculation (very approximate)
            prompt_tokens = len(prompt) // 4
            completion_tokens = len(current_text) // 4
            
            return {
                "id": response_id,
                "result": current_text,
                "agents_used": agents_used,
                "tokens": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                }
            }
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error running multi-agent: {str(e)}")
    
    # Store task matcher in app state
    app.state.task_matcher = task_matcher


# Update the existing completions endpoint
def update_completions_endpoint(app: FastAPI, agent_api: Any, editor_config: Dict[str, Any]):
    """
    Update the existing completions endpoint to support universal model
    
    Args:
        app: FastAPI application
        agent_api: Agent API instance
        editor_config: Editor configuration dictionary
    """
    # Get or create task matcher
    task_matcher = getattr(app.state, "task_matcher", None)
    if task_matcher is None:
        task_matcher = TaskMatcher(agent_api.registered_agents, editor_config)
        app.state.task_matcher = task_matcher
    
    # Original handler reference
    original_handler = None
    
    # Find original completions endpoint
    for route in app.routes:
        if route.path == "/v1/completions" and "POST" in route.methods:
            original_handler = route.endpoint
            break
    
    if original_handler is None:
        # No existing endpoint found, create a new one
        @app.post("/v1/completions")
        async def openai_compatible_completion(request: Request):
            await handle_universal_model(request)
    else:
        # Replace existing endpoint
        @app.post("/v1/completions")
        async def openai_compatible_completion(request: Request):
            body = await request.json()
            model = body.get("model", "")
            
            if model == "universal" or model == "auto":
                return await handle_universal_model(request)
            else:
                # Use the original handler
                return await original_handler(request)
    
    async def handle_universal_model(request: Request):
        """
        Handle universal model requests
        """
        try:
            # Parse request body
            body = await request.json()
            
            # Extract prompt
            prompt = body.get("prompt", "")
            if not prompt:
                # Try messages format
                messages = body.get("messages", [])
                prompt = "\n".join([m.get("content", "") for m in messages if m.get("content")])
            
            # Match tasks
            matches = task_matcher.match_task(prompt)
            
            # Filter by confidence
            matches = [m for m in matches if m["confidence"] >= 0.3]
            
            if not matches:
                # No good matches, return error
                raise HTTPException(
                    status_code=400,
                    detail="Could not determine appropriate agent for the prompt"
                )
            
            # Use top match
            top_match = matches[0]
            task_info = top_match["task_info"]
            task_type = task_info.get("task_type")
            
            if task_type == "agent":
                # Use existing agent
                agent_name = task_info.get("agent_name")
                
                # Check if agent exists
                if agent_name not in agent_api.registered_agents:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Agent '{agent_name}' not found"
                    )
                
                # Extract parameters
                params = task_matcher.extract_parameters(prompt, task_info)
                
                # Create agent instance
                agent_class = agent_api.registered_agents[agent_name]["class"]
                agent = agent_class()
                
                # Run agent
                result = agent.run(params)
                
                # Format result
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
                
                # Return in OpenAI format
                return {
                    "id": f"cmpl-{uuid.uuid4()}",
                    "object": "text_completion",
                    "created": int(body.get("created", 0)),
                    "model": f"agent:{agent_name}",
                    "choices": [
                        {
                            "text": response_text,
                            "index": 0,
                            "logprobs": None,
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": len(prompt) // 4,
                        "completion_tokens": len(response_text) // 4,
                        "total_tokens": (len(prompt) + len(response_text)) // 4
                    }
                }
            
            else:
                # It's an editor config type
                # Deploy a dynamic agent based on the config
                from universal_model_integration import register_dynamic_agent_from_editor_config
                
                # Extract parameters
                params = task_matcher.extract_parameters(prompt, task_info)
                
                # Deploy the agent
                agent_id = register_dynamic_agent_from_editor_config(
                    top_match["task_id"], 
                    editor_config, 
                    prompt, 
                    params
                )
                
                # Get the agent name from the deployment
                agent_name = agent_api.deployments[agent_id]["name"]
                
                # Create agent instance
                agent_class = agent_api.registered_agents[agent_name]["class"]
                agent = agent_class()
                
                # Run agent
                result = agent.run({"text": prompt})
                
                # Format result
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
                
                # Return in OpenAI format
                return {
                    "id": f"cmpl-{uuid.uuid4()}",
                    "object": "text_completion",
                    "created": int(body.get("created", 0)),
                    "model": "universal",
                    "choices": [
                        {
                            "text": response_text,
                            "index": 0,
                            "logprobs": None,
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": len(prompt) // 4,
                        "completion_tokens": len(response_text) // 4,
                        "total_tokens": (len(prompt) + len(response_text)) // 4
                    }
                }
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
    
    # Add chat completions endpoint
    @app.post("/v1/chat/completions")
    async def openai_chat_completions(request: Request):
        """
        OpenAI-compatible chat completions endpoint with agent routing
        """
        try:
            # Parse request body
            body = await request.json()
            
            # Extract model and messages
            model = body.get("model", "")
            messages = body.get("messages", [])
            
            # Combine messages into a prompt
            prompt = "\n".join([m.get("content", "") for m in messages if m.get("content")])
            
            if model == "universal" or model == "auto":
                # Use multi-agent processing with auto-sequence
                multi_request = {
                    "prompt": prompt,
                    "auto_sequence": True
                }
                
                # Copy additional parameters
                for key in ["max_tokens", "temperature"]:
                    if key in body:
                        multi_request[key] = body[key]
                
                # Run multi-agent
                multi_agent_result = await run_multi_agent(MultiAgentRequest(**multi_request))
                
                # Format as OpenAI response
                chat_response = {
                    "id": multi_agent_result.id,
                    "object": "chat.completion",
                    "created": int(body.get("created", 0)),
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": multi_agent_result.result
                            },
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": multi_agent_result.tokens["prompt_tokens"],
                        "completion_tokens": multi_agent_result.tokens["completion_tokens"],
                        "total_tokens": multi_agent_result.tokens["total_tokens"]
                    }
                }
                
                return chat_response
            
            elif model.startswith("agent:"):
                # Route to specific agent
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
                
                # Run agent
                input_data = {"text": prompt}
                # Add any additional parameters from the request
                for key, value in body.items():
                    if key not in ["model", "messages"]:
                        input_data[key] = value
                        
                result = agent.run(input_data)
                
                # Format result
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
                    "id": f"chatcmpl-{uuid.uuid4()}",
                    "object": "chat.completion",
                    "created": int(body.get("created", 0)),
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": response_text
                            },
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": len(prompt) // 4,
                        "completion_tokens": len(response_text) // 4,
                        "total_tokens": (len(prompt) + len(response_text)) // 4
                    }
                }
            
            else:
                # Not a supported model
                raise HTTPException(
                    status_code=400,
                    detail=f"Model '{model}' is not supported. Use 'universal', 'auto', or 'agent:name'"
                )
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

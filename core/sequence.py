import json
import asyncio
from typing import Dict, List, Any, Optional
import uuid
import aiohttp
from pydantic import BaseModel, Field


class AgentStep(BaseModel):
    """Agent execution step in a sequence"""
    agent_id: str = Field(..., description="ID or name of the agent")
    parameters: Dict[str, Any] = Field(default={}, description="Parameters for the agent")
    extract_result: str = Field(default="response", description="Field to extract from result")


class SequenceConfig(BaseModel):
    """Configuration for a multi-agent sequence"""
    name: str = Field(..., description="Name of the sequence")
    description: str = Field(..., description="Description of the sequence")
    steps: List[AgentStep] = Field(..., description="Steps in the sequence")
    input_field: str = Field(default="text", description="Field to pass the input to the first agent")
    output_field: str = Field(default="result", description="Field containing the final output")


class SequenceExecutor:
    """Executes a multi-agent sequence"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.sequences = {}
    
    def register_sequence(self, sequence_config: SequenceConfig) -> str:
        """
        Register a new sequence
        
        Args:
            sequence_config: Sequence configuration
        
        Returns:
            Sequence ID
        """
        sequence_id = str(uuid.uuid4())
        self.sequences[sequence_id] = sequence_config
        return sequence_id
    
    async def execute_sequence(
        self, 
        sequence_id: str, 
        input_data: Any,
        additional_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute a sequence with the given input
        
        Args:
            sequence_id: ID of the sequence to execute
            input_data: Input data for the sequence
            additional_params: Additional parameters to pass to all agents
        
        Returns:
            Execution result
        """
        if sequence_id not in self.sequences:
            raise ValueError(f"Sequence '{sequence_id}' not found")
        
        sequence = self.sequences[sequence_id]
        current_data = input_data
        step_results = []
        
        # Create a session for all requests
        async with aiohttp.ClientSession() as session:
            for i, step in enumerate(sequence.steps):
                # Prepare parameters for this step
                if i == 0:
                    # First step gets the original input
                    params = {sequence.input_field: current_data}
                else:
                    # Subsequent steps get previous step's output
                    params = {"text": current_data}
                
                # Add agent-specific parameters
                params.update(step.parameters)
                
                # Add additional parameters
                if additional_params:
                    params.update(additional_params)
                
                # Execute the agent
                try:
                    # Try by ID first (for deployed agents)
                    response = await session.post(
                        f"{self.base_url}/v1/agents/{step.agent_id}/run",
                        json=params
                    )
                    
                    if response.status != 200:
                        # Try by name (for registered agents)
                        agent_response = await session.post(
                            f"{self.base_url}/v1/completions",
                            json={
                                "model": f"agent:{step.agent_id}",
                                "prompt": current_data if isinstance(current_data, str) else json.dumps(current_data)
                            }
                        )
                        
                        if agent_response.status != 200:
                            raise ValueError(f"Failed to execute agent '{step.agent_id}': {await agent_response.text()}")
                        
                        result = await agent_response.json()
                        
                        # Extract the completion text
                        if "choices" in result and len(result["choices"]) > 0:
                            extracted = result["choices"][0].get("text", "")
                        else:
                            extracted = str(result)
                    else:
                        # Process direct agent result
                        result = await response.json()
                        
                        # Extract specified field from result
                        if isinstance(result, dict):
                            if step.extract_result in result:
                                extracted = result[step.extract_result]
                            else:
                                extracted = str(result)
                        else:
                            extracted = str(result)
                    
                    # Save the result
                    step_results.append({
                        "step": i + 1,
                        "agent_id": step.agent_id,
                        "parameters": params,
                        "result": result,
                        "extracted": extracted
                    })
                    
                    # Update current data for next step
                    current_data = extracted
                
                except Exception as e:
                    # Record the error and stop execution
                    step_results.append({
                        "step": i + 1,
                        "agent_id": step.agent_id,
                        "parameters": params,
                        "error": str(e)
                    })
                    break
        
        # Prepare the final result
        return {
            "sequence_id": sequence_id,
            "sequence_name": sequence.name,
            "steps": step_results,
            "result": current_data,
            "status": "success" if len(step_results) == len(sequence.steps) else "error"
        }


# Create predefined sequences
def create_predefined_sequences(executor: SequenceExecutor) -> Dict[str, str]:
    """
    Create predefined agent sequences
    
    Args:
        executor: Sequence executor
        
    Returns:
        Dictionary mapping sequence names to IDs
    """
    sequences = {}
    
    # Text processing sequence
    text_processing = SequenceConfig(
        name="text_processing",
        description="Process text through extraction, summarization, and analysis",
        steps=[
            AgentStep(
                agent_id="text_extractor",
                extract_result="extracted_text"
            ),
            AgentStep(
                agent_id="summarizer",
                parameters={"max_length": 200},
                extract_result="summary"
            ),
            AgentStep(
                agent_id="sentiment_analyzer",
                extract_result="sentiment"
            )
        ]
    )
    sequences["text_processing"] = executor.register_sequence(text_processing)
    
    # Content creation sequence
    content_creation = SequenceConfig(
        name="content_creation",
        description="Create content with research, outlining, and writing steps",
        steps=[
            AgentStep(
                agent_id="researcher",
                parameters={"depth": "moderate"},
                extract_result="research"
            ),
            AgentStep(
                agent_id="outliner",
                extract_result="outline"
            ),
            AgentStep(
                agent_id="writer",
                parameters={"style": "professional"},
                extract_result="content"
            )
        ]
    )
    sequences["content_creation"] = executor.register_sequence(content_creation)
    
    return sequences


# Add multi-agent sequence endpoints to FastAPI app
def add_sequence_endpoints(app: FastAPI, executor: SequenceExecutor):
    """
    Add multi-agent sequence endpoints to FastAPI app
    
    Args:
        app: FastAPI application
        executor: Sequence executor
    """
    class SequenceExecuteRequest(BaseModel):
        input: Any = Field(..., description="Input data for the sequence")
        parameters: Dict[str, Any] = Field(default={}, description="Additional parameters")
    
    @app.post("/v1/sequences/{sequence_id}/run")
    async def run_sequence(
        sequence_id: str,
        request: SequenceExecuteRequest = Body(...)
    ):
        """
        Run a sequence with the given input
        """
        try:
            result = await executor.execute_sequence(
                sequence_id,
                request.input,
                request.parameters
            )
            return result
        
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error executing sequence: {str(e)}")
    
    @app.get("/v1/sequences")
    async def list_sequences():
        """
        List all registered sequences
        """
        return {
            "sequences": [
                {
                    "id": sequence_id,
                    "name": config.name,
                    "description": config.description,
                    "steps": len(config.steps)
                }
                for sequence_id, config in executor.sequences.items()
            ]
        }


# OpenAI-compatible endpoint for multi-agent sequences
def add_openai_sequence_endpoint(app: FastAPI, executor: SequenceExecutor, sequence_map: Dict[str, str]):
    """
    Add OpenAI-compatible endpoint for multi-agent sequences
    
    Args:
        app: FastAPI application
        executor: Sequence executor
        sequence_map: Mapping from sequence names to IDs
    """
    @app.post("/v1/sequence/completions")
    async def sequence_completions(request: Request):
        """
        Run a sequence with OpenAI-compatible format
        """
        try:
            # Parse request body
            body = await request.json()
            
            # Extract model and messages
            model = body.get("model", "")
            
            if not model.startswith("sequence:"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Model '{model}' is not a valid sequence. Use format 'sequence:name'"
                )
            
            sequence_name = model.split(":", 1)[1]
            
            if sequence_name not in sequence_map:
                raise HTTPException(
                    status_code=404,
                    detail=f"Sequence '{sequence_name}' not found"
                )
            
            sequence_id = sequence_map[sequence_name]
            
            # Extract prompt or messages
            prompt = body.get("prompt", "")
            if not prompt:
                # Try messages format
                messages = body.get("messages", [])
                prompt = "\n".join([m.get("content", "") for m in messages if m.get("content")])
            
            # Prepare additional parameters
            additional_params = {k: v for k, v in body.items() if k not in ["model", "prompt", "messages"]}
            
            # Execute sequence
            result = await executor.execute_sequence(
                sequence_id,
                prompt,
                additional_params
            )
            
            # Format as OpenAI response
            final_result = result["result"]
            if not isinstance(final_result, str):
                final_result = json.dumps(final_result)
            
            return {
                "id": f"seqcmpl-{uuid.uuid4()}",
                "object": "text_completion",
                "created": int(body.get("created", 0)),
                "model": model,
                "choices": [
                    {
                        "text": final_result,
                        "index": 0,
                        "logprobs": None,
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(prompt) // 4,
                    "completion_tokens": len(final_result) // 4,
                    "total_tokens": (len(prompt) + len(final_result)) // 4
                }
            }
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

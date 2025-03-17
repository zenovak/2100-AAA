import os
import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from fastapi import FastAPI, HTTPException, Request, Body
from pydantic import BaseModel, Field

# Import the dynamic agent handler
from dynamic_agent_handler import DynamicAgentHandler


def setup_universal_model(app: FastAPI):
    """
    Set up the universal model integration
    
    Args:
        app: FastAPI application
    """
    # Get editor config from app state
    editor_config = getattr(app.state, "editor_config", None)
    if editor_config is None:
        # Load editor config if not in app state
        editor_config = load_editor_config()
        app.state.editor_config = editor_config
    
    # Create dynamic agent handler
    @app.on_event("startup")
    async def startup_event():
        app.state.dynamic_agent_handler = await DynamicAgentHandler.create(editor_config)
    
    # Add universal model endpoints
    @app.post("/v1/universal/completions")
    async def universal_completions(request: Request):
        """
        Universal model completions endpoint
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
            
            if not prompt:
                raise HTTPException(
                    status_code=400,
                    detail="No prompt provided"
                )
            
            # Extract additional parameters
            additional_params = {k: v for k, v in body.items() if k not in ["prompt", "messages"]}
            
            # Process with dynamic agent handler
            handler = app.state.dynamic_agent_handler
            task_matcher = app.state.task_matcher
            
            result = await handler.process_prompt(prompt, task_matcher, additional_params)
            
            # Format response in OpenAI style
            response_text = format_response_text(result)
            
            return {
                "id": f"completion-{uuid.uuid4()}",
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
    
    # Add universal chat completions endpoint
    @app.post("/v1/universal/chat/completions")
    async def universal_chat_completions(request: Request):
        """
        Universal model chat completions endpoint
        """
        try:
            # Parse request body
            body = await request.json()
            
            # Extract messages
            messages = body.get("messages", [])
            
            # Extract system message if present
            system_message = ""
            user_messages = []
            
            for message in messages:
                role = message.get("role", "")
                content = message.get("content", "")
                
                if role == "system":
                    system_message = content
                elif role == "user":
                    user_messages.append(content)
            
            # Combine user messages
            prompt = "\n".join(user_messages)
            
            if not prompt:
                raise HTTPException(
                    status_code=400,
                    detail="No user messages provided"
                )
            
            # Add system message as additional parameter if present
            additional_params = {k: v for k, v in body.items() if k not in ["messages"]}
            if system_message:
                additional_params["system_message"] = system_message
            
            # Process with dynamic agent handler
            handler = app.state.dynamic_agent_handler
            task_matcher = app.state.task_matcher
            
            result = await handler.process_prompt(prompt, task_matcher, additional_params)
            
            # Format response in OpenAI chat style
            response_text = format_response_text(result)
            
            return {
                "id": f"chatcmpl-{uuid.uuid4()}",
                "object": "chat.completion",
                "created": int(body.get("created", 0)),
                "model": "universal",
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
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


def format_response_text(result: Dict[str, Any]) -> str:
    """
    Format agent result as text
    
    Args:
        result: Agent result
        
    Returns:
        Formatted text
    """
    if isinstance(result, dict):
        if "error" in result:
            return f"Error: {result['error']}"
        elif "summary" in result:
            return result["summary"]
        elif "response" in result:
            return result["response"]
        elif "result" in result:
            return result["result"]
        elif "content" in result:
            return result["content"]
        else:
            # Try to find first string value
            for key, value in result.items():
                if isinstance(value, str) and len(value) > 10:
                    return value
            
            # Fall back to JSON
            return json.dumps(result, indent=2)
    else:
        return str(result)


def load_editor_config() -> Dict[str, Any]:
    """
    Load the editor configuration from either a file or hardcoded defaults
    
    Returns:
        Editor configuration dictionary
    """
    # Try to load from file
    if os.path.exists("editor_config.json"):
        with open("editor_config.json", "r") as f:
            return json.load(f)
    
    # Return hardcoded defaults
    return {
        "tweet": {
            "url": "/editor/tweet",
            "fields": [
                {
                    "id": "subject",
                    "label": "Tweet Topic",
                    "type": "text"
                },
                {
                    "id": "style",
                    "label": "Style",
                    "type": "select",
                    "options": ["Professional", "Friendly", "Human", "Royal"]
                },
                {
                    "id": "from",
                    "label": "From",
                    "type": "text"
                },
                {
                    "id": "intention",
                    "label": "Intention",
                    "type": "text"
                },
                {
                    "id": "context",
                    "label": "Context",
                    "type": "text"
                },
                {
                    "id": "useEmoji",
                    "label": "Use Emoji",
                    "type": "select",
                    "options": ["Yes", "No"]
                }
            ],
            "defaults": {
                "subject": "",
                "intention": "",
                "context": "",
                "from": "",
                "style": "Professional",
                "useEmoji": "No"
            },
            "prompts": {
                "system": "You are an expert at writing engaging tweets. Create a tweet using the style: {style}. {useEmoji, select, Yes {Include relevant emojis} No {Do not use any emojis}}",
                "user": "Write a tweet about: {subject}\nWith the intention: {intention}\nContext: {context}\nFrom: {from}"
            }
        },
        "sales-pitch": {
            "url": "/editor/sales-pitch",
            "fields": [
                {
                    "id": "subject",
                    "label": "Subject",
                    "type": "text"
                },
                {
                    "id": "style",
                    "label": "Style",
                    "type": "select",
                    "options": ["Professional", "Friendly", "Human", "Royal"]
                },
                {
                    "id": "to",
                    "label": "To",
                    "type": "text"
                },
                {
                    "id": "from",
                    "label": "From",
                    "type": "text"
                },
                {
                    "id": "intention",
                    "label": "Intention",
                    "type": "text"
                },
                {
                    "id": "context",
                    "label": "Context",
                    "type": "text"
                }
            ],
            "defaults": {
                "subject": "",
                "intention": "",
                "context": "",
                "to": "",
                "from": "",
                "style": "Professional"
            },
            "prompts": {
                "system": "You are an expert at writing sales pitches. Create a compelling sales pitch using the style: {style}",
                "user": "Create a sales pitch for the subject: {subject}\nWith the intention: {intention}\nContext: {context}\nTargeted to: {to}\nFrom: {from}"
            }
        }
    }

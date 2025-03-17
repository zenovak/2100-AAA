import os
import json
import datetime
import uuid
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from fastapi import FastAPI, HTTPException, Request, Body
from pydantic import BaseModel, Field

# Import the original agent API components
from agent_integration_api import (
    agent_api, app, AgentType, BaseAgent, 
    DeploymentConfig, TextProcessorAgent, urfn_summarize_text
)

# Import the agent search components
from agent_search_api import add_agent_search_endpoints, update_completions_endpoint, TaskMatcher

# Import the dynamic agent handler
from dynamic_agent_handler import DynamicAgentHandler

# Import the universal model integration
from universal_model_integration import setup_universal_model, load_editor_config

# Import the multi-agent sequence processing
from multi_agent_sequence import (
    SequenceExecutor,
    create_predefined_sequences,
    add_sequence_endpoints,
    add_openai_sequence_endpoint,
    SequenceConfig,
    AgentStep
)


def initialize_app():
    """
    Initialize the FastAPI application with all integrations
    
    Returns:
        Initialized FastAPI application
    """
    # Load editor configurations
    editor_config = load_editor_config()
    
    # Store editor config in app state
    app.state.editor_config = editor_config
    
    # Initialize task matcher
    task_matcher = TaskMatcher(agent_api.registered_agents, editor_config)
    app.state.task_matcher = task_matcher
    
    # Add agent search endpoints
    add_agent_search_endpoints(app, agent_api, editor_config)
    
    # Update completions endpoint to support universal model
    update_completions_endpoint(app, agent_api, editor_config)
    
    # Setup universal model integration
    setup_universal_model(app)
    
    # Create sequence executor
    executor = SequenceExecutor()
    
    # Create predefined sequences
    sequence_map = create_predefined_sequences(executor)
    
    # Add sequence endpoints
    add_sequence_endpoints(app, executor)
    
    # Add OpenAI-compatible sequence endpoint
    add_openai_sequence_endpoint(app, executor, sequence_map)
    
    # Store sequence executor in app state
    app.state.sequence_executor = executor
    app.state.sequence_map = sequence_map
    
    return app


def register_additional_agents():
    """Register additional agent types"""
    
    # Register analyzer agent
    @agent_api.register_agent(
        agent_name="analyzer",
        agent_type=AgentType.TASK,
        description="Agent that analyzes text content"
    )
    class AnalyzerAgent(BaseAgent):
        def __init__(self):
            super().__init__("analyzer")
        
        def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            if "text" not in input_data:
                return {"error": "Input must contain 'text' key"}
            
            text = input_data["text"]
            
            # In a real implementation, this would use NLP or AI models
            # For demo purposes, just return basic statistics
            words = text.split()
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            
            return {
                "analysis": {
                    "word_count": len(words),
                    "sentence_count": len(sentences),
                    "average_word_length": sum(len(w) for w in words) / max(1, len(words)),
                    "average_sentence_length": len(words) / max(1, len(sentences))
                }
            }
    
    # Register summarizer agent
    @agent_api.register_agent(
        agent_name="summarizer",
        agent_type=AgentType.TASK,
        description="Agent that generates concise summaries"
    )
    class SummarizerAgent(BaseAgent):
        def __init__(self):
            super().__init__("summarizer")
        
        def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            if "text" not in input_data:
                return {"error": "Input must contain 'text' key"}
            
            text = input_data["text"]
            max_length = input_data.get("max_length", 100)
            
            # In a real implementation, this would use NLP or AI models
            # For demo purposes, just take the first part of the text
            summary = text[:max_length] + "..." if len(text) > max_length else text
            
            return {
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary)
            }
    
    # Register content generator agent
    @agent_api.register_agent(
        agent_name="content_generator",
        agent_type=AgentType.CREATIVE,
        description="Agent that generates creative content"
    )
    class ContentGeneratorAgent(BaseAgent):
        def __init__(self):
            super().__init__("content_generator")
        
        def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            if "text" not in input_data:
                return {"error": "Input must contain 'text' key"}
            
            text = input_data["text"]
            content_type = input_data.get("content_type", "article")
            style = input_data.get("style", "professional")
            
            # In a real implementation, this would use AI models
            # For demo purposes, just return a mock response
            return {
                "generated_content": f"[This would be a {style} {content_type} about: {text}]",
                "content_type": content_type,
                "style": style,
                "prompt": text
            }
    
    # Register additional function: sentiment analysis
    @agent_api.register_function(
        function_name="urfn_analyze_sentiment",
        description="Analyzes sentiment of input text"
    )
    def urfn_analyze_sentiment(input_text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of input text
        
        Args:
            input_text: The text to analyze
            
        Returns:
            Dictionary with sentiment analysis
        """
        # Simple word-based sentiment analysis
        positive_words = ["good", "great", "excellent", "positive", "happy", "love", "like"]
        negative_words = ["bad", "terrible", "negative", "sad", "hate", "dislike"]
        
        words = input_text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        # Calculate sentiment score
        score = (positive_count - negative_count) / max(1, len(words)) * 10
        
        # Determine sentiment label
        if score > 1:
            sentiment = "positive"
        elif score < -1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "score": score,
            "positive_words": positive_count,
            "negative_words": negative_count,
            "analysis": f"The text has a {sentiment} sentiment with a score of {score:.2f}"
        }


# Register additional agents
register_additional_agents()

# Initialize the app
initialized_app = initialize_app()


if __name__ == "__main__":
    import uvicorn
    
    # Print startup message
    print("Starting Agent of All Agents API with Universal Model support...")
    print("Available endpoints:")
    print("  * /v1/agents/deploy - Deploy a new agent")
    print("  * /v1/agents/search - Search for appropriate agents")
    print("  * /v1/agents/{agent_id}/run - Run a deployed agent")
    print("  * /v1/multi-agent/run - Run multiple agents in sequence")
    print("  * /v1/sequences - List available predefined sequences")
    print("  * /v1/sequences/{sequence_id}/run - Run a predefined sequence")
    print("  * /v1/completions - OpenAI-compatible completions with universal model")
    print("  * /v1/chat/completions - OpenAI-compatible chat completions")
    print("  * /v1/sequence/completions - OpenAI-compatible sequence execution")
    print("  * /v1/universal/completions - Direct universal model completions")
    print("  * /v1/universal/chat/completions - Direct universal model chat completions")
    
    # Start the server
    uvicorn.run(initialized_app, host="0.0.0.0", port=8000)

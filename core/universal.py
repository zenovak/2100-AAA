import os
import json
from fastapi import FastAPI

# Import original agent API
from agent_integration_api import agent_api, app

# Import universal model integration
from universal_model_integration import (
    setup_universal_models,
    load_editor_config,
    register_dynamic_agent_from_editor_config
)

# Import multi-agent sequence processing
from multi_agent_sequence import (
    SequenceExecutor,
    create_predefined_sequences,
    add_sequence_endpoints,
    add_openai_sequence_endpoint
)


def initialize_app():
    """
    Initialize the FastAPI application with all extensions
    
    Returns:
        Initialized FastAPI application
    """
    # Set up universal models
    setup_universal_models(app)
    
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


if __name__ == "__main__":
    import uvicorn
    
    # Initialize the app
    initialized_app = initialize_app()
    
    # Start the FastAPI server
    uvicorn.run(initialized_app, host="0.0.0.0", port=8000)

# Agent of All Agents API Routes

This document provides an overview of all available API routes in the Agent of All Agents API.

## Core Agent Management

### Deploy Agent
- **Endpoint**: `/v1/agents/deploy`
- **Method**: POST
- **Description**: Deploy a new agent with the specified configuration
- **Request Body**:
  ```json
  {
    "name": "summarizer",
    "type": "task",
    "description": "Agent that summarizes text content",
    "functions": ["urfn_summarize_text"],
    "system_prompt": "You are an expert text summarizer.",
    "config": {
      "max_length": 100
    }
  }
  ```
- **Response**:
  ```json
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "summarizer",
    "type": "task",
    "description": "Agent that summarizes text content",
    "status": "active",
    "created_at": "2025-03-17T12:00:00Z"
  }
  ```

### List Agents
- **Endpoint**: `/v1/agents`
- **Method**: GET
- **Description**: List all deployed agents
- **Response**:
  ```json
  {
    "data": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "summarizer",
        "type": "task",
        "description": "Agent that summarizes text content",
        "status": "active",
        "created_at": "2025-03-17T12:00:00Z"
      }
    ]
  }
  ```

### Get Agent Details
- **Endpoint**: `/v1/agents/{agent_id}`
- **Method**: GET
- **Description**: Get information about a specific deployed agent
- **Response**: Same as a single agent in the list response

### Delete Agent
- **Endpoint**: `/v1/agents/{agent_id}`
- **Method**: DELETE
- **Description**: Delete a deployed agent
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Agent 'summarizer' successfully deleted"
  }
  ```

### Run Agent
- **Endpoint**: `/v1/agents/{agent_id}/run`
- **Method**: POST
- **Description**: Run a deployed agent with the given input data
- **Request Body**:
  ```json
  {
    "text": "This is a sample text to process.",
    "operation": "summarize"
  }
  ```
- **Response**: Varies based on the agent, typically:
  ```json
  {
    "agent": "summarizer",
    "processed": true,
    "function_results": {
      "urfn_summarize_text": {
        "summary": "This is a sample text to process."
      }
    },
    "input": {
      "text": "This is a sample text to process.",
      "operation": "summarize"
    }
  }
  ```

## OpenAI-Compatible Endpoints

### Completions
- **Endpoint**: `/v1/completions`
- **Method**: POST
- **Description**: OpenAI-compatible completions endpoint that routes to agents
- **Request Body**:
  ```json
  {
    "model": "agent:summarizer",
    "prompt": "This is a long text that needs to be summarized.",
    "max_tokens": 100,
    "temperature": 0.7
  }
  ```
- **Response**:
  ```json
  {
    "id": "cmpl-550e8400e29b41d4a716446655440000",
    "object": "text_completion",
    "created": 1684936751,
    "model": "agent:summarizer",
    "choices": [
      {
        "text": "This is a long text that needs to be summarized.",
        "index": 0,
        "logprobs": null,
        "finish_reason": "stop"
      }
    ],
    "usage": {
      "prompt_tokens": 10,
      "completion_tokens": 8,
      "total_tokens": 18
    }
  }
  ```

## Dynamic API Augmentations

The API automatically exposes any endpoints registered through the `augment_api` decorator:

### Text Processor
- **Endpoint**: `/v1/augment/text-processor`
- **Method**: POST
- **Description**: Process text using available text processing functions
- **Request Body**:
  ```json
  {
    "text": "This is a sample text to process.",
    "operation": "summarize"
  }
  ```
- **Response**: Varies based on the operation, typically:
  ```json
  {
    "summary": "This is a sample text to process."
  }
  ```

## Additional Custom Endpoints

As new functions are registered with the `augment_api` decorator, they will automatically be exposed as endpoints in the API.

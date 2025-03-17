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

As new functions are registered with the `augment_api` decorator, they will automatically be exposed as endpoints in the API



# Universal Model and Multi-Agent Sequence API Guide

This guide explains how to use the Universal Model and Multi-Agent Sequence features of the Agent of All Agents API.

## Table of Contents
- [Universal Model](#universal-model)
- [Agent Search](#agent-search)
- [Multi-Agent Processing](#multi-agent-processing)
- [Predefined Sequences](#predefined-sequences)
- [Integration with OpenAI API](#integration-with-openai-api)
- [Examples](#examples)

## Universal Model

The Universal Model automatically detects the appropriate agent or task type for a given prompt and routes the request accordingly.

### Using the Universal Model

**Endpoint**: `/v1/completions`  
**Method**: POST  
**Model**: Use `"universal"` or `"auto"`

**Request**:
```json
{
  "model": "universal",
  "prompt": "Write a professional tweet about our new product launch",
  "max_tokens": 100,
  "temperature": 0.7
}
```

**Response**:
```json
{
  "id": "cmpl-abc123",
  "object": "text_completion",
  "created": 1684936751,
  "model": "universal",
  "choices": [
    {
      "text": "Excited to announce the launch of our new product...",
      "index": 0,
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 12,
    "total_tokens": 22
  }
}
```

## Agent Search

The Agent Search feature identifies the most appropriate agents or tasks for a given prompt.

### Searching for Agents

**Endpoint**: `/v1/agents/search`  
**Method**: POST

**Request**:
```json
{
  "prompt": "Write a tweet about our new product launch",
  "max_results": 3,
  "min_confidence": 0.2
}
```

**Response**:
```json
{
  "matches": [
    {
      "task_id": "tweet",
      "confidence": 0.85,
      "matched_keywords": ["tweet", "write"],
      "parameters": {
        "subject": "new product launch",
        "style": "Professional"
      },
      "task_type": "tweet"
    },
    {
      "task_id": "text_processor",
      "confidence": 0.42,
      "matched_keywords": ["write"],
      "parameters": {
        "text": "Write a tweet about our new product launch",
        "operation": "generate"
      },
      "task_type": "agent"
    }
  ]
}
```

## Multi-Agent Processing

Multi-Agent Processing allows using multiple agents in sequence to process a single request.

### Running Multi-Agent Processing

**Endpoint**: `/v1/multi-agent/run`  
**Method**: POST

**Request**:
```json
{
  "prompt": "Research AI trends, outline key points, and write a blog post",
  "auto_sequence": true,
  "max_tokens": 1000
}
```

**Request with Explicit Sequence**:
```json
{
  "prompt": "Research AI trends for a blog post",
  "agent_sequence": ["researcher", "outliner", "writer"],
  "auto_sequence": false
}
```

**Response**:
```json
{
  "id": "multiagent-abc123",
  "result": "# The Future of AI Trends\n\nArtificial intelligence continues to evolve...",
  "agents_used": [
    {
      "agent_id": "researcher",
      "parameters": {
        "text": "Research AI trends for a blog post"
      },
      "step": 1
    },
    {
      "agent_id": "outliner",
      "parameters": {
        "text": "AI trends include: 1. Generative AI, 2. AI Automation..."
      },
      "step": 2
    },
    {
      "agent_id": "writer",
      "parameters": {
        "text": "# Outline: The Future of AI\n1. Introduction\n2. Generative AI..."
      },
      "step": 3
    }
  ],
  "tokens": {
    "prompt_tokens": 8,
    "completion_tokens": 120,
    "total_tokens": 128
  }
}
```

## Predefined Sequences

Predefined sequences allow executing a fixed series of agents in a standardized workflow.

### Listing Available Sequences

**Endpoint**: `/v1/sequences`  
**Method**: GET

**Response**:
```json

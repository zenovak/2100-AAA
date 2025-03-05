# Agent Integration API: Developer Guide

A flexible Python API for integrating, developing, and extending AI agents with standardized interfaces and modular functionality.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Core Concepts](#core-concepts)
- [Getting Started](#getting-started)
- [Extending the API](#extending-the-api)
  - [Creating New Agents](#creating-new-agents)
  - [Adding Functions](#adding-functions)
  - [API Augmentation](#api-augmentation)
- [URFN Registry](#urfn-registry)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [Contributing](#contributing)

## Overview

The Agent Integration API provides a standardized way to create, register, and execute various AI agents while allowing for modular extension through Unique Reserved Function Names (URFNs) and API augmentation patterns.

Key features:
- Register custom agents with standardized interfaces
- Extend functionality with modular functions
- Augment the API with new endpoints
- Maintain compatibility with existing AI agent standards

## Installation

```bash
pip install agent-integration-api
```

Or with Poetry:

```bash
poetry add agent-integration-api
```

## Core Concepts

### Agents
Agents are the primary components that perform specific tasks. Each agent has a type, description, and implementation.

### URFNs (Unique Reserved Function Names)
URFNs provide modular functionality that can be used by any agent. They follow a standard naming convention (`urfn_*`) and are registered in a central registry.

### API Augmentation
API augmentation allows developers to extend the API with new endpoints without modifying core components.

## Getting Started

### Basic Usage

```python
from agent_integration_api import agent_api, BaseAgent, AgentType

# Create a custom agent
@agent_api.register_agent(
    agent_name="my_agent",
    agent_type=AgentType.TASK,
    description="An example agent"
)
class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("my_agent")
    
    def run(self, input_data):
        # Agent implementation
        return {"result": "Processed input: " + input_data.get("text", "")}

# Use the agent
agent = MyCustomAgent()
result = agent.run({"text": "Hello, world!"})
print(result)  # {"result": "Processed input: Hello, world!"}
```

### Using URFNs

```python
from agent_integration_api import agent_api

# Use an existing URFN
result = agent_api.execute_function("urfn_summarize_text", input_text="Long text to summarize...")
print(result)  # {"summary": "Summarized text..."}
```

## Extending the API

### Creating New Agents

1. Subclass `BaseAgent`
2. Register with `@agent_api.register_agent`
3. Implement the `run()` method

```python
@agent_api.register_agent(
    agent_name="sentiment_analyzer",
    agent_type=AgentType.TASK,
    description="Analyzes text sentiment"
)
class SentimentAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("sentiment_analyzer")
    
    def run(self, input_data):
        text = input_data.get("text", "")
        # Call a sentiment analysis URFN
        return self.call_function("urfn_analyze_sentiment", text=text)
```

### Adding Functions

1. Create a function with the URFN naming convention
2. Register with `@agent_api.register_function`
3. Implement the function logic

```python
@agent_api.register_function(
    function_name="urfn_analyze_sentiment",
    description="Analyzes the sentiment of text"
)
def urfn_analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of input text
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with sentiment scores
    """
    # Implementation details
    positive_score = len([word for word in text.split() if word in ["good", "great", "happy"]])
    negative_score = len([word for word in text.split() if word in ["bad", "awful", "sad"]])
    
    return {
        "positive": positive_score,
        "negative": negative_score,
        "overall": "positive" if positive_score > negative_score else "negative"
    }
```

### API Augmentation

1. Create a function to handle the new endpoint
2. Register with `@agent_api.augment_api`
3. Implement the endpoint logic

```python
@agent_api.augment_api(endpoint="/v1/augment/sentiment")
def analyze_sentiment_endpoint(data: dict) -> dict:
    """
    Analyze sentiment of provided text
    
    Args:
        data: Dictionary with text to analyze
        
    Returns:
        Sentiment analysis result
    """
    agent = SentimentAnalyzerAgent()
    return agent.run(data)
```

## URFN Registry

The URFN registry is a central JSON file that maintains metadata about all registered functions:

```json
{
  "urfn_summarize_text": {
    "description": "Summarizes the input text",
    "module": "text_processor",
    "function": "urfn_summarize_text",
    "parameters": {
      "input_text": {
        "type": "str",
        "required": true
      }
    }
  }
}
```

To view registered URFNs:

```python
print(agent_api.list_functions())
```

## Best Practices

### Agent Design
- Keep agents focused on specific tasks
- Use URFNs for reusable functionality
- Document expected inputs and outputs

### Function Implementation
- Follow the URFN naming convention
- Provide clear documentation
- Include proper type hints
- Handle edge cases

### API Augmentation
- Use RESTful design principles
- Document endpoints thoroughly
- Implement proper error handling

## Examples

### Text Processing Agent

```python
@agent_api.register_agent(
    agent_name="text_processor",
    agent_type=AgentType.TASK,
    description="Processes text in various ways"
)
class TextProcessorAgent(BaseAgent):
    def __init__(self):
        super().__init__("text_processor")
    
    def run(self, input_data):
        text = input_data.get("text", "")
        operation = input_data.get("operation", "summarize")
        
        operations = {
            "summarize": "urfn_summarize_text",
            "translate": "urfn_translate_text",
            "analyze": "urfn_analyze_text"
        }
        
        if operation not in operations:
            return {"error": f"Unsupported operation: {operation}"}
        
        return self.call_function(operations[operation], input_text=text)
```

### Translation Function

```python
@agent_api.register_function(
    function_name="urfn_translate_text",
    description="Translates text between languages"
)
def urfn_translate_text(input_text: str, target_language: str = "fr") -> dict:
    """
    Translate text to target language
    
    Args:
        input_text: Text to translate
        target_language: Target language code
        
    Returns:
        Dictionary with translated text
    """
    # Implementation details
    translations = {
        "fr": {
            "hello": "bonjour",
            "world": "monde"
        },
        "es": {
            "hello": "hola",
            "world": "mundo"
        }
    }
    
    # Simple word replacement (for example purposes)
    result = input_text.lower()
    for eng, trans in translations.get(target_language, {}).items():
        result = result.replace(eng, trans)
    
    return {
        "original": input_text,
        "translated": result,
        "language": target_language
    }
```

## Contributing

We welcome contributions to expand the Agent Integration API:

1. Fork the repository
2. Create a feature branch
3. Add your agent, function, or augmentation
4. Write tests for your addition
5. Submit a pull request

Please follow our contribution guidelines and code style conventions.

## License

MIT

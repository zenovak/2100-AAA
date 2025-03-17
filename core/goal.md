1. Universal Model
The Universal Model system automatically detects the appropriate agent or task type for a given prompt:
pythonCopy# Using the Universal Model
response = requests.post(
    "http://localhost:8000/v1/completions",
    json={
        "model": "universal",
        "prompt": "Write a professional tweet about our new AI product"
    }
)
This system:

Analyzes the content of prompts to determine intent
Matches patterns to identify appropriate agent types
Extracts relevant parameters from the prompt text
Routes requests to the most suitable agent

2. Agent Search API
The Agent Search API helps identify which agents are best suited for a specific task:
pythonCopyresponse = requests.post(
    "http://localhost:8000/v1/agents/search",
    json={
        "prompt": "Write a tweet about our product launch"
    }
)
This allows for:

Finding appropriate agents based on natural language prompts
Getting confidence scores for how well each agent matches
Seeing extracted parameters for each potential agent match

3. Multi-Agent Processing
The Multi-Agent system processes inputs through a sequence of specialized agents:
pythonCopyresponse = requests.post(
    "http://localhost:8000/v1/multi-agent/run",
    json={
        "prompt": "Research AI trends and write a blog post",
        "auto_sequence": True
    }
)
This enables:

Automatic determination of appropriate agent sequences
Passing output from one agent to the next
Building complex workflows from simple agent components

4. Predefined Sequences
The system supports predefined agent sequences for common workflows:
pythonCopyresponse = requests.post(
    f"http://localhost:8000/v1/sequences/{sequence_id}/run",
    json={
        "input": "Create content about quantum computing"
    }
)
These sequences:

Define standardized workflows for common tasks
Allow reuse of effective agent combinations
Can be invoked with simple API calls

5. OpenAI API Compatibility
All these features are available through OpenAI-compatible endpoints:
pythonCopyimport openai
openai.api_base = "http://localhost:8000/v1"

# Use the universal model
completion = openai.Completion.create(
    model="universal",
    prompt="Write a tweet announcing our product launch"
)

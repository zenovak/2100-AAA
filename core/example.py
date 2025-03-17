import requests
import json

# Base URL for API
API_URL = "http://localhost:8000"

# Example 1: Deploy a simple summarization agent
def deploy_summarization_agent():
    print("\n=== Deploying Summarization Agent ===")
    
    # Define the deployment configuration
    deployment_config = {
        "name": "summarizer",
        "type": "task",
        "description": "Agent that summarizes text content",
        "functions": ["urfn_summarize_text"],
        "system_prompt": "You are an expert text summarizer that creates concise summaries.",
        "config": {
            "max_length": 100,
            "include_key_points": True
        }
    }
    
    # Deploy the agent
    response = requests.post(
        f"{API_URL}/v1/agents/deploy",
        json=deployment_config
    )
    
    # Print response
    if response.status_code == 200:
        agent_data = response.json()
        print(f"✓ Successfully deployed agent: {agent_data['name']}")
        print(f"  ID: {agent_data['id']}")
        print(f"  Type: {agent_data['type']}")
        print(f"  Status: {agent_data['status']}")
        
        # Return the agent ID for later use
        return agent_data['id']
    else:
        print(f"✗ Error deploying agent: {response.status_code}")
        print(response.text)
        return None

# Example 2: Use the agent with the standard run endpoint
def run_agent_direct(agent_id, text):
    print(f"\n=== Running Agent Directly (ID: {agent_id}) ===")
    
    # Define input data
    input_data = {
        "text": text,
        "operation": "summarize"
    }
    
    # Run the agent
    response = requests.post(
        f"{API_URL}/v1/agents/{agent_id}/run",
        json=input_data
    )
    
    # Print response
    if response.status_code == 200:
        result = response.json()
        print("✓ Agent executed successfully")
        print(f"  Result: {json.dumps(result, indent=2)}")
    else:
        print(f"✗ Error running agent: {response.status_code}")
        print(response.text)

# Example 3: Use the agent with OpenAI-compatible API
def run_agent_openai_compatible(agent_name, text):
    print(f"\n=== Running Agent via OpenAI Compatible API (Agent: {agent_name}) ===")
    
    # Create OpenAI-style request
    openai_request = {
        "model": f"agent:{agent_name}",
        "prompt": text,
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    # Send request to completions endpoint
    response = requests.post(
        f"{API_URL}/v1/completions",
        json=openai_request
    )
    
    # Print response
    if response.status_code == 200:
        result = response.json()
        print("✓ Completion successful")
        print(f"  Text: {result['choices'][0]['text']}")
    else:
        print(f"✗ Error running completion: {response.status_code}")
        print(response.text)

# Example 4: List all deployed agents
def list_agents():
    print("\n=== Listing All Deployed Agents ===")
    
    # List agents
    response = requests.get(f"{API_URL}/v1/agents")
    
    # Print response
    if response.status_code == 200:
        agents = response.json()["data"]
        print(f"✓ Found {len(agents)} deployed agents")
        
        for agent in agents:
            print(f"  - {agent['name']} (ID: {agent['id']}, Type: {agent['type']})")
    else:
        print(f"✗ Error listing agents: {response.status_code}")
        print(response.text)

# Example 5: Delete an agent
def delete_agent(agent_id):
    print(f"\n=== Deleting Agent (ID: {agent_id}) ===")
    
    # Delete agent
    response = requests.delete(f"{API_URL}/v1/agents/{agent_id}")
    
    # Print response
    if response.status_code == 200:
        result = response.json()
        print(f"✓ {result['message']}")
    else:
        print(f"✗ Error deleting agent: {response.status_code}")
        print(response.text)

# Example 6: Deploy an agent with multiple functions
def deploy_multi_function_agent():
    print("\n=== Deploying Multi-Function Agent ===")
    
    # Define the deployment configuration
    deployment_config = {
        "name": "content_processor",
        "type": "task",
        "description": "Agent that processes content with multiple functions",
        "functions": [
            "urfn_summarize_text", 
            "urfn_analyze_text"  # Assuming this function exists
        ],
        "system_prompt": "You are a versatile content processor that can summarize and analyze text.",
        "config": {
            "default_operation": "summarize"
        }
    }
    
    # Deploy the agent
    response = requests.post(
        f"{API_URL}/v1/agents/deploy",
        json=deployment_config
    )
    
    # Print response
    if response.status_code == 200:
        agent_data = response.json()
        print(f"✓ Successfully deployed agent: {agent_data['name']}")
        print(f"  ID: {agent_data['id']}")
        print(f"  Type: {agent_data['type']}")
        print(f"  Status: {agent_data['status']}")
        
        # Return the agent ID for later use
        return agent_data['id']
    else:
        print(f"✗ Error deploying agent: {response.status_code}")
        print(response.text)
        return None


# Run the examples
if __name__ == "__main__":
    # Sample text for testing
    sample_text = """
    The Agent of All Agents API provides a flexible framework for creating, 
    deploying, and managing various AI agents. With its modular design, 
    developers can easily create new agents, register functions, and extend 
    the API with additional endpoints. The URFN (Unique Reserved Function Name) 
    system ensures consistent function naming and registration across the platform.
    """
    
    # Example 1: Deploy a simple summarization agent
    agent_id = deploy_summarization_agent()
    
    if agent_id:
        # Example 2: Use the agent with the standard run endpoint
        run_agent_direct(agent_id, sample_text)
        
        # Example 3: Use the agent with OpenAI-compatible API
        run_agent_openai_compatible("summarizer", sample_text)
        
        # Example 4: List all deployed agents
        list_agents()
        
        # Example 5: Delete the agent
        delete_agent(agent_id)
        
        # Example 6: Deploy a multi-function agent
        multi_agent_id = deploy_multi_function_agent()
        
        if multi_agent_id:
            # Run the multi-function agent
            run_agent_direct(multi_agent_id, sample_text)
            
            # Clean up
            delete_agent(multi_agent_id)

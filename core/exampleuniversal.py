import requests
import json
import asyncio
import aiohttp

# Base URL for API
API_URL = "http://localhost:8000"

# Example 1: Using the universal model
def use_universal_model():
    print("\n=== Using Universal Model ===")
    
    # Define a prompt
    prompt = "Write a professional tweet about the new AI features we've launched for our product."
    
    # Create a request
    request = {
        "model": "universal",
        "prompt": prompt,
        "max_tokens": 100
    }
    
    # Send the request to the completions endpoint
    response = requests.post(
        f"{API_URL}/v1/completions",
        json=request
    )
    
    # Print response
    if response.status_code == 200:
        result = response.json()
        
        print(f"✓ Universal model detected appropriate agent")
        print(f"  Output: {result['choices'][0]['text']}")
    else:
        print(f"✗ Error using universal model: {response.status_code}")
        print(response.text)

# Example 2: Search for appropriate agents
def search_agents():
    print("\n=== Searching for Appropriate Agents ===")
    
    # Define prompts to test
    prompts = [
        "Write a tweet about our new product launch",
        "Create a sales pitch for enterprise customers about our AI solution",
        "Can you summarize this article for me?",
        "Generate a compelling email subject line"
    ]
    
    for prompt in prompts:
        # Create a request
        request = {
            "prompt": prompt,
            "max_results": 2,
            "min_confidence": 0.2
        }
        
        # Send the request to the agent search endpoint
        response = requests.post(
            f"{API_URL}/v1/agents/search",
            json=request
        )
        
        # Print response
        if response.status_code == 200:
            result = response.json()
            
            print(f"\nPrompt: '{prompt}'")
            for i, match in enumerate(result["matches"]):
                print(f"  Match {i+1}: {match['task_id']} (Confidence: {match['confidence']:.2f})")
                print(f"    Keywords: {', '.join(match['matched_keywords'])}")
                print(f"    Parameters: {json.dumps(match['parameters'], indent=2)}")
        else:
            print(f"✗ Error searching agents: {response.status_code}")
            print(response.text)

# Example 3: Using multi-agent processing
async def use_multi_agent():
    print("\n=== Using Multi-Agent Processing ===")
    
    # Define a prompt
    prompt = "Can you research the latest AI trends, create an outline, and write a blog post about it?"
    
    # Create a request
    request = {
        "prompt": prompt,
        "auto_sequence": True
    }
    
    # Send the request to the multi-agent endpoint
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_URL}/v1/multi-agent/run",
            json=request
        ) as response:
            if response.status == 200:
                result = await response.json()
                
                print(f"✓ Multi-agent processing successful")
                print(f"  Agents used: {len(result['agents_used'])}")
                for i, agent in enumerate(result['agents_used']):
                    print(f"    Step {i+1}: {agent['agent_id']}")
                
                print(f"  Result: {result['result'][:100]}...")
            else:
                print(f"✗ Error using multi-agent: {response.status}")
                text = await response.text()
                print(text)

# Example 4: Using predefined sequences
async def use_predefined_sequence():
    print("\n=== Using Predefined Sequence ===")
    
    # List available sequences
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/v1/sequences") as response:
            if response.status == 200:
                sequences = await response.json()
                print(f"✓ Found {len(sequences['sequences'])} available sequences")
                
                for seq in sequences['sequences']:
                    print(f"  - {seq['name']}: {seq['description']} ({seq['steps']} steps)")
                
                # Use the content creation sequence
                content_seq = next((s for s in sequences['sequences'] if s['name'] == 'content_creation'), None)
                
                if content_seq:
                    # Execute the sequence
                    async with session.post(
                        f"{API_URL}/v1/sequences/{content_seq['id']}/run",
                        json={
                            "input": "Create content about the future of AI and automation",
                            "parameters": {
                                "style": "conversational",
                                "length": "medium"
                            }
                        }
                    ) as seq_response:
                        if seq_response.status == 200:
                            result = await seq_response.json()
                            
                            print(f"\n✓ Sequence execution successful")
                            print(f"  Steps completed: {len(result['steps'])}")
                            print(f"  Final result: {result['result'][:100]}...")
                        else:
                            print(f"✗ Error executing sequence: {seq_response.status}")
                            text = await seq_response.text()
                            print(text)
            else:
                print(f"✗ Error listing sequences: {response.status}")
                text = await response.text()
                print(text)

# Example 5: Using the OpenAI-compatible chat completions endpoint
def use_chat_completions():
    print("\n=== Using OpenAI-Compatible Chat Completions ===")
    
    # Define messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a tweet announcing our new AI feature."}
    ]
    
    # Create a request
    request = {
        "model": "universal",
        "messages": messages,
        "temperature": 0.7
    }
    
    # Send the request to the chat completions endpoint
    response = requests.post(
        f"{API_URL}/v1/chat/completions",
        json=request
    )
    
    # Print response
    if response.status_code == 200:
        result = response.json()
        
        print(f"✓ Chat completions successful")
        print(f"  Response: {result['choices'][0]['message']['content']}")
    else:
        print(f"✗ Error using chat completions: {response.status_code}")
        print(response.text)

# Run all examples
if __name__ == "__main__":
    # Run synchronous examples
    use_universal_model()
    search_agents()
    use_chat_completions()
    
    # Run asynchronous examples
    loop = asyncio.get_event_loop()
    loop.run_until_complete(use_multi_agent())
    loop.run_until_complete(use_predefined_sequence())

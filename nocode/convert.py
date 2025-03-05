
import re
import json
import uuid
from typing import Dict, List, Any, Tuple, Optional

# Import required for LLM integration
import requests
from typing import Dict, Any

class NaturalLanguageWorkflowParser:
    """
    A parser that converts natural language workflow descriptions to URFN registry entries
    """
    
    def __init__(self, llm_api_url: str = "http://localhost:7777/ask-claudee"):
        """
        Initialize the parser
        
        Args:
            llm_api_url: URL for the LLM API endpoint
        """
        self.llm_api_url = llm_api_url
        self.system_message = """
        You are a specialized AI assistant that converts natural language workflow descriptions
        into structured workflow definitions. Parse the user's description and extract:
        1. Workflow name
        2. Input variables
        3. Processing steps
        4. Connections between steps
        5. Output definition
        
        Format your response as a structured JSON object with these fields, and nothing else.
        """
    
    def call_llm(self, description: str) -> Dict[str, Any]:
        """
        Call the LLM to parse the natural language description
        
        Args:
            description: Natural language workflow description
            
        Returns:
            Structured workflow definition
        """
        try:
            # In a real implementation, you would call an actual LLM API
            # For demonstration, we'll simulate a successful response with mock parsing
            
            # Prepare request
            payload = {
                "system": self.system_message,
                "message": f"Convert this workflow description to structured JSON:\n\n{description}"
            }
            
            # Make API request
            response = requests.post(self.llm_api_url, json=payload)
            
            if response.status_code == 200:
                # Extract JSON from the response
                result = response.json()
                structured_workflow = result.get("response", "{}")
                
                # Parse the JSON, handling potential format issues
                try:
                    return json.loads(structured_workflow)
                except json.JSONDecodeError:
                    # Try to extract JSON from text response
                    json_match = re.search(r'```json\n(.*?)\n```', structured_workflow, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(1))
                    else:
                        # Fallback to simple parsing
                        return self._parse_workflow_simple(description)
            else:
                # Fallback to simple parsing if API call fails
                return self._parse_workflow_simple(description)
                
        except Exception as e:
            print(f"Error calling LLM: {e}")
            # Fallback to simple parsing
            return self._parse_workflow_simple(description)
    
    def _parse_workflow_simple(self, description: str) -> Dict[str, Any]:
        """
        Simple fallback parser for when the LLM call fails
        
        Args:
            description: Natural language workflow description
            
        Returns:
            Structured workflow definition
        """
        # Extract a workflow name
        name_match = re.search(r'(workflow|system|process) (called|named) ["\'"]?([a-zA-Z0-9 ]+)["\'"]?', description, re.IGNORECASE)
        workflow_name = name_match.group(3) if name_match else "Workflow" + str(uuid.uuid4())[:8]
        
        # Find inputs
        input_matches = re.findall(r'(input|take|accept)[s]? ([a-zA-Z0-9, ]+)', description, re.IGNORECASE)
        inputs = []
        if input_matches:
            for match in input_matches:
                input_items = match[1].split(',')
                for item in input_items:
                    item = item.strip()
                    if item and not item.lower() in ['and', 'or', 'the', 'an', 'a']:
                        inputs.append(item)
        
        # Find steps
        step_matches = re.findall(r'(step|then|first|next|after that)[,:]? ([^,.]+)', description, re.IGNORECASE)
        steps = []
        if step_matches:
            for match in step_matches:
                steps.append(match[1].strip())
        
        # Find output
        output_match = re.search(r'(output|return|produce)[s]? ([^,.]+)', description, re.IGNORECASE)
        output = output_match.group(2).strip() if output_match else "result"
        
        return {
            "workflow_name": workflow_name,
            "inputs": inputs,
            "steps": steps,
            "output": output
        }
    
    def convert_to_urfn(self, parsed_workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert the parsed workflow to URFN registry entries
        
        Args:
            parsed_workflow: Structured workflow definition
            
        Returns:
            URFN registry entries
        """
        workflow_name = parsed_workflow.get("workflow_name", "Workflow")
        workflow_id = workflow_name.lower().replace(" ", "_")
        
        # Create a workflow URFN
        workflow_urfn = f"urfn_workflow_{workflow_id}"
        
        # Build list of steps
        steps = []
        
        # Add input step
        steps.append({
            "id": "input",
            "type": "input",
            "description": "Workflow input",
            "params": {}
        })
        
        # Add processing steps
        for i, step in enumerate(parsed_workflow.get("steps", [])):
            step_id = f"step_{i+1}"
            
            # Determine if step is likely a prompt or function
            if any(kw in step.lower() for kw in ["ask", "prompt", "query", "question"]):
                steps.append({
                    "id": step_id,
                    "type": "prompt",
                    "description": step,
                    "params": {
                        "system": f"You are an AI assistant that helps with {workflow_name}.",
                        "user": step
                    }
                })
            else:
                steps.append({
                    "id": step_id,
                    "type": "function",
                    "description": step,
                    "params": {
                        "function_name": f"process_{step_id}",
                        "input": "{}"
                    }
                })
        
        # Add output step
        steps.append({
            "id": "output",
            "type": "output",
            "description": "Workflow output",
            "params": {
                "output_key": parsed_workflow.get("output", "result")
            }
        })
        
        # Build connections
        connections = []
        for i in range(len(steps) - 1):
            connections.append({
                "from": steps[i]["id"],
                "to": steps[i+1]["id"],
                "type": "sequence"
            })
        
        # Create URFN registry entry
        urfn_registry = {
            workflow_urfn: {
                "description": f"Workflow: {workflow_name}",
                "module": "natural_language_workflows",
                "function": "execute_workflow",
                "parameters": {
                    "workflow_def": json.dumps({
                        "name": workflow_name,
                        "steps": steps,
                        "connections": connections,
                        "inputs": parsed_workflow.get("inputs", []),
                        "output": parsed_workflow.get("output", "result")
                    }),
                    "input": "{}"
                }
            }
        }
        
        # Add step-specific URFNs if needed
        for step in steps:
            if step["type"] == "prompt":
                prompt_urfn = f"urfn_prompt_{workflow_id}_{step['id']}"
                urfn_registry[prompt_urfn] = {
                    "description": f"Prompt for {step['description']}",
                    "module": "natural_language_workflows.prompts",
                    "function": "execute_prompt",
                    "parameters": {
                        "system_template": step["params"].get("system", ""),
                        "user_template": step["params"].get("user", ""),
                        "variables": "{}"
                    }
                }
        
        return urfn_registry

def convert_natural_language_to_urfn(description: str) -> Dict[str, Any]:
    """
    Convert a natural language workflow description to URFN registry entries
    
    Args:
        description: Natural language workflow description
        
    Returns:
        URFN registry entries
    """
    parser = NaturalLanguageWorkflowParser()
    parsed_workflow = parser.call_llm(description)
    return parser.convert_to_urfn(parsed_workflow)


# Example usage
if __name__ == "__main__":
    # Sample natural language description
    description = """
    Create a workflow called "Customer Support" that takes a customer question as input.
    First, analyze the sentiment of the question.
    Then, search for relevant knowledge base articles.
    Next, generate a helpful response based on the articles and sentiment.
    Finally, output the response and suggested follow-up questions.
    """
    
    # Convert to URFN registry
    urfn_registry = convert_natural_language_to_urfn(description)
    
    # Print the result
    print(json.dumps(urfn_registry, indent=2))

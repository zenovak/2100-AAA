import re
import json
from typing import Dict, List, Any, Union, Optional, Callable
from enum import Enum


class NodeType(Enum):
    AGENT = "agent"
    FUNCTION = "function"
    INPUT = "input"
    OUTPUT = "output"
    PROMPT = "prompt"
    CONDITION = "condition"
    VARIABLE = "variable"


class ConnectionType(Enum):
    SEQUENCE = "-->"
    CONDITION_TRUE = "==>"
    CONDITION_FALSE = "=/>"
    VARIABLE_BINDING = ":="


class AgentDSL:
    """Parser and executor for the Agent Connection DSL"""
    
    def __init__(self):
        self.workflows = {}
        self.variables = {}
        self.registered_agents = {}
        self.registered_functions = {}
    
    def parse_workflow(self, workflow_text: str) -> Dict[str, Any]:
        """Parse a workflow definition in the DSL format"""
        lines = [line.strip() for line in workflow_text.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        # Extract workflow name and description
        name_line = lines[0]
        if not name_line.startswith("workflow:"):
            raise ValueError("Workflow must start with 'workflow: [name]'")
        
        workflow_name = name_line.split("workflow:")[1].strip()
        
        # Parse nodes and connections
        nodes = {}
        connections = []
        variables = {}
        
        for line in lines[1:]:
            if ":=" in line:  # Variable definition
                self._parse_variable(line, variables)
            elif "-->" in line or "==>" in line or "=/>" in line:  # Connection
                connections.append(self._parse_connection(line))
            elif "(" in line and ")" in line and ":" in line:  # Node definition
                node_name, node_def = self._parse_node(line)
                nodes[node_name] = node_def
        
        workflow = {
            "name": workflow_name,
            "nodes": nodes,
            "connections": connections,
            "variables": variables
        }
        
        self.workflows[workflow_name] = workflow
        return workflow
    
    def _parse_variable(self, line: str, variables: Dict[str, Any]) -> None:
        """Parse a variable definition"""
        var_name, var_value = [part.strip() for part in line.split(":=", 1)]
        
        # Handle different variable types
        if var_value.startswith('"') and var_value.endswith('"'):
            # String variable
            variables[var_name] = var_value[1:-1]
        elif var_value.lower() in ['true', 'false']:
            # Boolean variable
            variables[var_name] = var_value.lower() == 'true'
        elif var_value.isdigit() or (var_value.startswith('-') and var_value[1:].isdigit()):
            # Integer variable
            variables[var_name] = int(var_value)
        elif '.' in var_value and all(part.isdigit() for part in var_value.replace('-', '').split('.')):
            # Float variable
            variables[var_name] = float(var_value)
        elif var_value.startswith('[') and var_value.endswith(']'):
            # List variable
            items = [item.strip() for item in var_value[1:-1].split(',') if item.strip()]
            variables[var_name] = items
        elif var_value.startswith('{') and var_value.endswith('}'):
            # Try to parse as JSON
            try:
                variables[var_name] = json.loads(var_value)
            except json.JSONDecodeError:
                # Handle as string if not valid JSON
                variables[var_name] = var_value
        else:
            # Default to string
            variables[var_name] = var_value
    
    def _parse_connection(self, line: str) -> Dict[str, str]:
        """Parse a connection between nodes"""
        if "-->" in line:
            source, target = [part.strip() for part in line.split("-->", 1)]
            conn_type = ConnectionType.SEQUENCE
        elif "==>" in line:
            source, target = [part.strip() for part in line.split("==>", 1)]
            conn_type = ConnectionType.CONDITION_TRUE
        elif "=/>" in line:
            source, target = [part.strip() for part in line.split("=/>", 1)]
            conn_type = ConnectionType.CONDITION_FALSE
        else:
            raise ValueError(f"Invalid connection format: {line}")
        
        return {
            "source": source,
            "target": target,
            "type": conn_type.value
        }
    
    def _parse_node(self, line: str) -> tuple:
        """Parse a node definition"""
        node_name, node_def = [part.strip() for part in line.split(":", 1)]
        
        # Determine node type
        if node_def.startswith("agent("):
            node_type = NodeType.AGENT
            params = self._extract_params(node_def)
        elif node_def.startswith("function("):
            node_type = NodeType.FUNCTION
            params = self._extract_params(node_def)
        elif node_def.startswith("prompt("):
            node_type = NodeType.PROMPT
            params = self._extract_params(node_def)
        elif node_def.startswith("condition("):
            node_type = NodeType.CONDITION
            params = self._extract_params(node_def)
        elif node_def.startswith("input("):
            node_type = NodeType.INPUT
            params = self._extract_params(node_def)
        elif node_def.startswith("output("):
            node_type = NodeType.OUTPUT
            params = self._extract_params(node_def)
        else:
            raise ValueError(f"Unknown node type: {node_def}")
        
        return node_name, {
            "type": node_type.value,
            "params": params
        }
    
    def _extract_params(self, node_def: str) -> Dict[str, str]:
        """Extract parameters from node definition"""
        # Get everything between the first set of parentheses
        param_str = re.search(r'\((.*)\)', node_def).group(1)
        
        # Handle multi-line parameters with proper escaping
        params = {}
        
        # Split by commas not inside quotes
        param_parts = []
        current_part = ""
        in_quotes = False
        escape_next = False
        
        for char in param_str:
            if escape_next:
                current_part += char
                escape_next = False
            elif char == '\\':
                escape_next = True
            elif char == '"' and not escape_next:
                in_quotes = not in_quotes
                current_part += char
            elif char == ',' and not in_quotes:
                param_parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char
        
        if current_part.strip():
            param_parts.append(current_part.strip())
        
        # Process each parameter
        for part in param_parts:
            if "=" in part:
                key, value = [p.strip() for p in part.split("=", 1)]
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                
                params[key] = value
        
        return params
    
    def convert_to_urfn(self, workflow_name: str) -> Dict[str, Any]:
        """Convert a workflow to URFN registry entries"""
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")
        
        workflow = self.workflows[workflow_name]
        urfn_registry = {}
        
        # Create a unique URFN for the workflow
        workflow_urfn = f"urfn_workflow_{workflow_name.lower().replace(' ', '_')}"
        
        # Convert nodes to URFNs
        for node_name, node_def in workflow["nodes"].items():
            if node_def["type"] == NodeType.PROMPT.value:
                # Create a URFN for prompt nodes
                prompt_urfn = f"urfn_prompt_{node_name.lower().replace(' ', '_')}"
                urfn_registry[prompt_urfn] = {
                    "description": f"Prompt template for {node_name}",
                    "module": "agent_dsl.prompts",
                    "function": "execute_prompt",
                    "parameters": {
                        "system_template": node_def["params"].get("system", ""),
                        "user_template": node_def["params"].get("user", ""),
                        "variables": "{}"
                    }
                }
        
        # Create URFN for the workflow itself
        urfn_registry[workflow_urfn] = {
            "description": f"Workflow: {workflow_name}",
            "module": "agent_dsl.workflows",
            "function": "execute_workflow",
            "parameters": {
                "workflow_def": json.dumps(workflow),
                "input": "{}"
            }
        }
        
        return urfn_registry
    
    def execute_workflow(self, workflow_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow with given input data"""
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")
        
        workflow = self.workflows[workflow_name]
        
        # Initialize execution state
        state = {
            "input": input_data,
            "variables": workflow["variables"].copy(),
            "output": {},
            "current_node": None,
            "execution_path": []
        }
        
        # Find input nodes to start execution
        start_nodes = [name for name, node in workflow["nodes"].items() 
                      if node["type"] == NodeType.INPUT.value]
        
        if not start_nodes:
            raise ValueError(f"No input nodes found in workflow '{workflow_name}'")
        
        # Execute each starting node
        for node_name in start_nodes:
            self._execute_node(node_name, workflow, state)
        
        return state["output"]
    
    def _execute_node(self, node_name: str, workflow: Dict[str, Any], state: Dict[str, Any]) -> None:
        """Execute a single node in the workflow"""
        if node_name not in workflow["nodes"]:
            raise ValueError(f"Node '{node_name}' not found in workflow")
        
        node = workflow["nodes"][node_name]
        state["current_node"] = node_name
        state["execution_path"].append(node_name)
        
        # Handle different node types
        if node["type"] == NodeType.INPUT.value:
            # Just pass through, input is already in state
            pass
        
        elif node["type"] == NodeType.AGENT.value:
            agent_name = node["params"].get("name", "")
            if agent_name in self.registered_agents:
                agent = self.registered_agents[agent_name]
                agent_input = self._resolve_variables(node["params"].get("input", "{}"), state)
                result = agent.run(agent_input)
                state["variables"][node_name + "_result"] = result
            else:
                raise ValueError(f"Agent '{agent_name}' not registered")
        
        elif node["type"] == NodeType.FUNCTION.value:
            function_name = node["params"].get("name", "")
            if function_name in self.registered_functions:
                func = self.registered_functions[function_name]
                func_input = self._resolve_variables(node["params"].get("input", "{}"), state)
                result = func(**func_input)
                state["variables"][node_name + "_result"] = result
            else:
                raise ValueError(f"Function '{function_name}' not registered")
        
        elif node["type"] == NodeType.PROMPT.value:
            system_template = node["params"].get("system", "")
            user_template = node["params"].get("user", "")
            
            # Resolve variables in templates
            system_prompt = self._resolve_template(system_template, state)
            user_prompt = self._resolve_template(user_template, state)
            
            # In a real implementation, this would call the LLM
            # For now, just store the prompts
            result = {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "response": "Mock response for " + node_name
            }
            state["variables"][node_name + "_result"] = result
        
        elif node["type"] == NodeType.CONDITION.value:
            condition = node["params"].get("expression", "true")
            condition_result = self._evaluate_condition(condition, state)
            state["variables"][node_name + "_result"] = condition_result
        
        elif node["type"] == NodeType.OUTPUT.value:
            output_key = node["params"].get("key", "result")
            output_value = self._resolve_variables(node["params"].get("value", "{}"), state)
            state["output"][output_key] = output_value
        
        # Find and execute next nodes
        self._execute_next_nodes(node_name, workflow, state)
    
    def _execute_next_nodes(self, current_node: str, workflow: Dict[str, Any], state: Dict[str, Any]) -> None:
        """Find and execute nodes that should run after the current node"""
        node = workflow["nodes"][current_node]
        
        for connection in workflow["connections"]:
            if connection["source"] == current_node:
                if connection["type"] == ConnectionType.SEQUENCE.value:
                    # Always follow sequence connections
                    self._execute_node(connection["target"], workflow, state)
                
                elif connection["type"] == ConnectionType.CONDITION_TRUE.value:
                    # Follow only if condition is true
                    if node["type"] == NodeType.CONDITION.value:
                        condition_result = state["variables"].get(current_node + "_result", False)
                        if condition_result:
                            self._execute_node(connection["target"], workflow, state)
                
                elif connection["type"] == ConnectionType.CONDITION_FALSE.value:
                    # Follow only if condition is false
                    if node["type"] == NodeType.CONDITION.value:
                        condition_result = state["variables"].get(current_node + "_result", False)
                        if not condition_result:
                            self._execute_node(connection["target"], workflow, state)
    
    def _resolve_variables(self, input_str: str, state: Dict[str, Any]) -> Any:
        """Resolve variables in a string or dict"""
        if isinstance(input_str, str):
            if input_str.startswith("{") and input_str.endswith("}"):
                try:
                    # Parse as JSON
                    input_dict = json.loads(input_str)
                    
                    # Resolve variables in the dict
                    resolved_dict = {}
                    for key, value in input_dict.items():
                        if isinstance(value, str) and value.startswith("$"):
                            var_name = value[1:]
                            resolved_dict[key] = state["variables"].get(var_name, state["input"].get(var_name, value))
                        else:
                            resolved_dict[key] = value
                    
                    return resolved_dict
                except json.JSONDecodeError:
                    # Not a valid JSON, treat as string
                    pass
            
            # Check if it's a direct variable reference
            if input_str.startswith("$"):
                var_name = input_str[1:]
                return state["variables"].get(var_name, state["input"].get(var_name, input_str))
            
            return input_str
        
        return input_str
    
    def _resolve_template(self, template: str, state: Dict[str, Any]) -> str:
        """Resolve variables in a template string"""
        result = template
        
        # Find all variables in the format {{variable_name}}
        variables = re.findall(r'\{\{([^}]+)\}\}', template)
        
        for var in variables:
            var_value = None
            
            # Check if it's a path like result.key1.key2
            if "." in var:
                parts = var.split(".")
                current = state["variables"]
                
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        break
                else:
                    # If we got through all parts, current holds the value
                    var_value = current
            else:
                # Direct variable lookup
                var_value = state["variables"].get(var, state["input"].get(var, ""))
            
            # Replace in template
            if var_value is not None:
                result = result.replace("{{" + var + "}}", str(var_value))
        
        return result
    
    def _evaluate_condition(self, condition: str, state: Dict[str, Any]) -> bool:
        """Evaluate a condition expression using variable substitution"""
        # Replace variables with their values
        resolved_condition = condition
        
        # Find all variables in the format $variable_name
        variables = re.findall(r'\$([a-zA-Z0-9_]+)', condition)
        
        for var in variables:
            var_value = state["variables"].get(var, state["input"].get(var, ""))
            
            # Format value based on type for proper evaluation
            if isinstance(var_value, str):
                formatted_value = f'"{var_value}"'
            elif isinstance(var_value, bool):
                formatted_value = str(var_value).lower()
            else:
                formatted_value = str(var_value)
            
            resolved_condition = resolved_condition.replace(f"${var}", formatted_value)
        
        try:
            # Safely evaluate the condition
            # In a production environment, you would want to use a safer evaluation method
            return bool(eval(resolved_condition))
        except Exception as e:
            print(f"Error evaluating condition '{condition}': {e}")
            return False
    
    def register_agent(self, name: str, agent: Any) -> None:
        """Register an agent for use in workflows"""
        self.registered_agents[name] = agent
    
    def register_function(self, name: str, func: Callable) -> None:
        """Register a function for use in workflows"""
        self.registered_functions[name] = func


def generate_urfn_registry(dsl_text: str) -> Dict[str, Any]:
    """
    Generate URFN registry entries from DSL text
    
    Args:
        dsl_text: DSL text defining workflows
        
    Returns:
        Dict of URFN registry entries
    """
    dsl = AgentDSL()
    workflow = dsl.parse_workflow(dsl_text)
    return dsl.convert_to_urfn(workflow["name"])


# Helper functions for executing workflows
def execute_prompt(system_template: str, user_template: str, variables: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a prompt with variables
    
    Args:
        system_template: System message template
        user_template: User message template
        variables: Variables to insert into templates
        
    Returns:
        Dict with prompts and mock response
    """
    # In a real implementation, this would call the LLM API
    return {
        "system_prompt": system_template,
        "user_prompt": user_template,
        "response": "Mock response for prompt"
    }


def execute_workflow(workflow_def: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a workflow with input data
    
    Args:
        workflow_def: JSON string of workflow definition
        input_data: Input data for the workflow
        
    Returns:
        Workflow execution results
    """
    workflow = json.loads(workflow_def)
    dsl = AgentDSL()
    dsl.workflows[workflow["name"]] = workflow
    return dsl.execute_workflow(workflow["name"], input_data)

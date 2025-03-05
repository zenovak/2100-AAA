# Agent Connection DSL

A simple, no-code way to define agent workflows, prompt chains, and connections.

## Overview

The Agent Connection DSL (Domain Specific Language) allows you to create complex agent workflows without writing code. You can define:

- Agent interactions
- Prompt chains
- Conditional flows
- Variable substitution
- Multi-step processes

The DSL is automatically converted to URFN registry entries, making it compatible with the Agent Integration API.

## Syntax

### Workflow Definition

Each workflow starts with a workflow declaration:

```
workflow: WorkflowName
```

### Variable Definitions

Define variables using the `:=` operator:

```
variable_name := value
```

Examples:
```
max_length := 100
include_keywords := true
tone := "professional"
focus_areas := ["key findings", "methodology", "limitations"]
```

### Node Definitions

Nodes represent processing steps in your workflow:

```
node_name: node_type(parameters)
```

Node types:
- `input`: Input data sources
- `output`: Output destinations
- `agent`: Agent processing
- `function`: Function calls
- `prompt`: LLM prompts
- `condition`: Conditional logic

Examples:
```
userInput: input(type="text")
textAnalysis: function(name="analyze_text", input={"text": "$userInput"})
summaryPrompt: prompt(
  system="You are a summarizer...",
  user="Summarize: {{userInput}}"
)
checkLength: condition(expression="len($userInput) > 10")
```

### Connections

Connect nodes using arrows:

```
sourceNode --> targetNode    # Simple sequence
condition ==> trueTarget     # Follow if condition is true
condition =/> falseTarget    # Follow if condition is false
```

## Variable Substitution

### In Parameters

Use `$variable` to reference variables in parameters:

```
function(name="analyze_text", input={"text": "$userInput"})
```

### In Templates

Use `{{variable}}` to insert variables in templates:

```
prompt(
  user="Summarize: {{userInput}}\nLength: {{max_length}}"
)
```

### Accessing Results

Node results are available as `node_name_result`:

```
prompt(
  user="Analyze: {{userInput}}\nKeywords: {{textAnalysis_result.keywords}}"
)
```

## Node Types

### Input Nodes

```
inputNode: input(type="text|json|file")
```

### Output Nodes

```
outputNode: output(key="result_name", value="$someNode_result.response")
```

### Agent Nodes

```
agentNode: agent(name="agent_name", input={"param1": "value1"})
```

### Function Nodes

```
functionNode: function(name="function_name", input={"param1": "value1"})
```

### Prompt Nodes

```
promptNode: prompt(
  system="System message with {{variables}}",
  user="User message with {{variables}}"
)
```

### Condition Nodes

```
conditionNode: condition(expression="$var1 > 10 and len($var2) < 5")
```

## Integration with URFN Registry

The DSL is automatically converted to URFN registry entries:

```python
from agent_dsl import generate_urfn_registry

# Load DSL from file
with open("workflow.dsl", "r") as f:
    dsl_text = f.read()

# Generate URFN registry entries
urfn_entries = generate_urfn_registry(dsl_text)

# Add to agent API
for urfn_name, urfn_def in urfn_entries.items():
    agent_api.urfn_registry[urfn_name] = urfn_def
```

## Execution

To execute a workflow:

```python
from agent_dsl import AgentDSL

dsl = Agent

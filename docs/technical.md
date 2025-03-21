



## System Architecture



### Microservice: Agent Architecture

The Agent microservice handles the execution of the agent's workflow code, this is done via worker threads.





More details in Data Models of agent




## Data Models


### Agent
An Agent represents a single prompt chain with an option to trigger system events. Agents do not hold memory of previous interactions, intead is functionally equivalent to a workflow. It is a single pass operation. 

```
model Agent {
    id            String
    name          String
    description   String

    variables     Dictionary<String, String>
    promptChain   Node[]
}
```

`id` (String)\
uuid4 id string that identifies this agent.

`nade` (String)\
name of the agent

`description` (String)\
descriptions for the agent

`variables` (Dictionary of String key, String value)\
Corresponds to the templating string provided by `system` and `user`. Values stored here is referable to the promptChain, throughout the workflow runtime.

`promptChain` (Array of Node)\
corresponds to the chain of nodes that uses the node interface. 

<br>

### Node (Base class)
Node represents the base class of all nodes, it is meant as an interface defining the shared parameters of all nodes

```
model Node {
    type     enum
    name     String

    output   String
}
```

`type` (String, enum)\
Represents the type of node. This is used for determined casting in downstream nodes

`name` (String)\
the name of this node. Used for logging purposes

`output` (string, key)\
mapping that points to the agent's variables registry key where the model output is stored. If an unregistered key is
referenced, a new one will be created at workflow runtime.

<br>

### Prompt Node
Represents a single step within the prompt chain

```
model PromptNode extends Node {
    type             enum

    system           String
    user             String

    apikey           String
    llm              enum
    model            String
    temperature      int
    maxTokens        int

    output           String
}
```

`type` (String, enum)\
Represents the type of node. This is used for determined casting in downstream nodes

`name` (String)\
the name of this node. Used for logging purposes

`system` (string)\
Represents the system prompt. This string accepts a special templating synthax using `{field}`

`user` (string)\
Represents the user prompt. This string accepts a special templating synthax using `{field}`

`apiKey` (String)\
The API key for this agent. This string accepts a special templating syntax using `{field}` which will allow the API key to be parsed at workflow runtime and sent in `agent.variables`

`llm` (String, enum)\
Registered enum types of available LLM service provider Valid values are:
- `claude`
- `replicate`

`model` (String)\
The model available from the service provider. See Glossary of supported services for available models

`temperature` (Integer)\
The Model's temeperature settings

`maxToken` (Integer)\
The model's maximum tokens 

`output` (string, key)\
mapping that points to the agent's variables registry key where the model output is stored. If an unregistered key is
referenced, a new one will be created at workflow runtime.

<br>

### Return Node
Represents the terminal node, which an output can be listed for return

```
model ReturnNode extends Node {


    @Override
    output          Array<String>
}
```

`output` (Array of String key)
List of keys from the shared context variable to return within the task object once the workflow finishes

<br>

### Parser Node `@experimental`
Represents an input output filter node within the chain

```
model ParserNode {
    rawData       String
    parser        enum

    schema        String
    
    field       Dictionary<String, String>
    output      Dictionary<String, String>
}
```

`field` (Dictionary of key string, value string)\
Corresponds to the templating string provided by `rawData`. 


`output` (Dictionary of key string, value string)\
mapping that points to the next Node's field property.

<br>

### System Events
Events are API calls that will occur at stage of the agent's execution

```
model EventNode extends Node {
    endPoint    String
    method      String
    data        String

    field       Dictionary<String, String>
    output      Dictionary<String, String>
}
```

`endPoint` (String)\
The API endpoint to call. Uses the special templating syntax string.

`method` (string | enum)\
The API request method. `GET`, `POST`, `PUT`, `DELETE`, etc

`data` (string)\
The JSON template for making the request. Uses the special templating syntax string. During runtime, this string will be parsed back to JSON

`field` (Dictionary of key string, value string)\
Corresponds to the templating string provided by `endPoint` and `data`. 


`output` (Dictionary of key string, value string)\
mapping that points to the next Node's field property.

<br><br>

## Business Logic

<br>

### Making an Agent

As an example, an agent that summerizes the plot of the movie and list the characters. Can be constructed via the following nodes. Nodes are listed as pseudo code.

```
Node 1 PromptNode

systemPrompt: "You are a helpful assistant for creating a list of plots form a movie script denoted by ### \nPlease list the plots by enclosing them with the <plot></plot> syntax"
userPrompt: "### ${script} ###"

field: {
    script: "{entryPoint}"
}

output: {
    plots: "{output}",
    script: "{script}"
}
```

Each node denotes the output dictionary, and its current input with the above formatting


```
Node 2: PromptNode

systemPrompt: "You are a helpful assistant for creating a brief summary of a movie plot denoted by <plot></plot>"
userPrompt: "Movie script ${script} \n\nPlot ${summary}"

field: {
    script: "{script}",     // `{script}` came from prev node output
    summary: "{plots}"      // `{plot}` came from prev node output
}

output {
    summary: "{output}"      // `{output}` is a preserved keyword, of this node's output
}
```

Here, we generate the list of characters, but, we are also passing along the generated summary from the previous stage

```
Node 3 PromptNode

systemPrompt: """
You are a helpful assistant for listing all the characters of this movie script denoted by ### 

Please respond in JSON with the following schema:
{
    "characters: ["Alex", "Steve"]
}
"""
userPrompt: "Movie script ${script}"

field: {
    summary: "{summary}",
    script: "{script}",
}

output: {
    rawData: "{output}",
    summary: "{summary}"
}
```

Here we parse the LLM output into a json format and verify it with the schema property of this node, which is also just a string object.

The JSON is then stringify again and pass as a string within one of the output's field

We pass the generated summary information to the next node. 

```
Node 4 ParserNode
rawData: "{rawData}"
parser: "JSON",

schema: "
{
    "character": "Array<String>"
}
"

field: {
    rawData: "{rawData}",
    summary: "{summary}"
}

output: {
    lisOfCharacters: "{output}",
    summary: "{summmary}",
}
```


In the last node, we fire an event, which in this case is a single API endpoint. Here, the data property of this node is also just actually a string with our templating syntax, which will be parsed, and templated at runtime into a JSON object. 

```
Node 5 EventNode

endPoint : "/prediction/movie-script/result"
method: "POST"
param: null
data: {
    "characters": {characters},
    "summary": {summary},
}

field: {
    characters: "{listOfCharacters}" ,  // came from prev node
    summary: "{summary}"
}
```



### Agent and workflow




<br><br>


# API: Backend Agent Microservice
The following API backend is a protected internal system. It is not intended to be accessed outside of docker without the proxy pass of the frontend.


## `/api/agent`



## Webhook to frontend
For every task completed, a webhook is sent to the frontend to record the workflow's logs, and prediction sessions. 



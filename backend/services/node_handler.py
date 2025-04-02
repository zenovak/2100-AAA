from models.prompt_node import PromptNode
from models.return_node import ReturnNode
from services.claude_ai import claude_llm_completion
from services.replicate_llm import replicate_llm_completion
from utils.template_parser import parser


SERVICE_REGISTRY = {
    "claude": claude_llm_completion,
    "replicate": replicate_llm_completion
}


async def handle_prompt_node(node: PromptNode, context: dict):
    system = parser(node.system, context)
    user = parser(node.user, context)
    api = parser(node.apikey, context)
    model = parser(node.model, context)
    llm_service = node.llm

    llm_completion = SERVICE_REGISTRY.get(llm_service)

    try:
        results = await llm_completion(
            api_key=api,
            system=system,
            user=user,
            model=model,
            temperature=node.temperature,
            tokens=node.maxTokens
        )
        context[node.output] = results

    except Exception:
        print("Unable to handle prompt")


def handle_return_node(node: ReturnNode, context: dict) -> dict:
    outputDict = {}
    for key in node.output:
        outputDict[key] = context[key]
        
    return outputDict

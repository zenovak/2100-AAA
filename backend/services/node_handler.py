from models.prompt_node import PromptNode
from models.return_node import ReturnNode
from services.claude_ai import claude_llm_completion
from utils.template_parser import parser


SERVICE_REGISTRY = {
    "claude": claude_llm_completion
}


def handle_prompt_node(node: PromptNode, context: dict):
    system = parser(node.system, context)
    user = parser(node.user, context)
    api = parser(node.api, context)
    model = parser(node.model, context)
    llm_service = node.llm

    llm_completion = SERVICE_REGISTRY.get(llm_service)

    try:
        results = llm_completion(
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


def handle_return_node(node: ReturnNode, context: dict):
    return_obj = {}
    for key in node.output:
        return_obj[key] = context[key]

    return return_obj

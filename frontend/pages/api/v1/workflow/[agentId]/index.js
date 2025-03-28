import prisma from "@/utils/server/prisma";
import { runAgent } from "@/utils/server/run-workflow";


export default async function handler(req, res) {
  const agentId = req.query.agentId;
  const input = req.body;

  const agent = await prisma.agent.findUnique({
    where: {
      id: agentId
    }
  });

  if (!agent) {
    res.status(404).json({ message: "Agent not found" });
    return;
  }

  agent.variables = JSON.parse(agent.variables);
  agent.workflow = JSON.parse(agent.workflow);

  const workflowAgent = {
    id: agent.id,
    name: agent.name,
    variables: agent.variables,
    promptChain: agent.workflow
  }

  const response = await runAgent({agent: workflowAgent});

  if (response instanceof Error) {
    res.status(500).json({ message: response});
    return;
  }

  res.status(201).json(response);
  return;
}
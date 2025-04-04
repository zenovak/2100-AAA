import prisma from "@/utils/server/prisma";
import { runAgent } from "@/utils/server/run-workflow";


export default async function handler(req, res) {
  const agentId = req.query.agentId;
  const input = req.body.input;


  const agent = await prisma.agent.findUnique({
    where: {
      id: agentId
    }
  });

  if (!agent) {
    res.status(404).json({ message: "Agent not found" });
    return;
  }

  // parse and init agent's variables
  agent.variables = JSON.parse(agent.variables);
  agent.workflow = JSON.parse(agent.workflow);

  // replace keys in input body to populate variables
  for (const key in input) {
    if (Object.prototype.hasOwnProperty.call(input, key)) {
      const element = input[key];
      agent.variables[key] = element;
    }
  }

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

  // register the instance of running task to db
  const task = await prisma.task.create({
    data: {
      id: response.id,
      agentId: agent.id,
      status: response.status,
      logs: JSON.stringify(response.logs),
      output: JSON.stringify(response.output)
    }
  })

  res.status(201).json(response);
  return;
}
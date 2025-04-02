import prisma, { handlePrismaError } from "@/utils/server/prisma";


export default async function handler(req, res) {
  switch (req.method) {
    case "GET": {
      const agents = await prisma.agent.findMany();

      res.status(200).json(agents);
      return;
    }
    case "POST": {
      await post(req, res);
      return;
    }

    default: {
      res.status(400).json({ message: "Method not allowed" });
      return;
    }
  }
}


async function post(req, res) {
  const { id, name, description, variables, workflow } = req.body;

  if (!id || !name || !description || !workflow) {
    res.status(400).json({ message: "Missing required body args"});
    return;
  }

  try {
    const agent = await prisma.agent.create({
      data: {
        id: id,
        name: name,
        description: description,
        variables: JSON.stringify(variables || "[]"),
        workflow: JSON.stringify(workflow)
      }
    });

    // parse back to JSON
    agent.variables = JSON.parse(agent.variables);
    agent.workflow = JSON.parse(agent.workflow);
    res.status(201).json(agent);
    return;
  } catch (error) {
    const errorRes = handlePrismaError(error);
    res.status(errorRes.status).json({ message: errorRes.message });
    return;
  }
}
import prisma, { handlePrismaError } from "@/utils/server/prisma";


export default async function handler(req, res) {
  switch (req.method) {
    case "GET": {
      await get(req, res);
      return;
    }

    case "POST": {
      await post(req, res);
      return;
    }

    case "DELETE": {
      await handleDelete(req, res);
      return;
    }
    default: {
      res.status(400).json({ message: "Method not allowed" });
      return;
    }
  }
}

/**
 * Fetches the relevant agent from database
 * @param {*} req 
 * @param {*} res 
 * @returns 
 */
async function get(req, res) {
  const agentId = req.query.agentId;

  try {
    const agent = await prisma.agent.findUnique({
      where: {
        id: agentId
      }
    });

    if (!agent) {
      res.status(404).json(agent);
      return;
    }

    res.status(200).json(agent);
    return;
  } catch (error) {
    const errorRes = handlePrismaError(error);
    res.status(errorRes.status).json({ message: errorRes.message});
    return;
  }
}


/**
 * Updates the relevant agent
 * @param {*} req
 * @param {*} res  
 */
async function post(req, res) {
  const agentId = req.query.agentId;

  if (!name || !description || !workflow) {
    res.status(400).json({ message: "Missing required body args"});
    return;
  }

  try {
    const agent = await prisma.agent.update({
      where: {
        id: agentId
      },
      data: {
        name: name,
        description: description,
        variables: JSON.stringify(variables || "[]"),
        workflow: JSON.stringify(workflow)
      }
    });
    res.status(201).json(agent);
    return;
  } catch (error) {
    res.status(errorRes.status).json({ message: errorRes.message});
    return;
  }
}

/**
 * Deletes the agent
 * @param {*} req 
 * @param {*} res 
 * @returns 
 */
async function handleDelete(req, res) {
  const agentId = req.query.agentId;
  try {
    const agent = await prisma.agent.delete({
      where: {
        id: agentId
      }
    });
    res.status(201).json(agent);
    return;
  } catch (error) {
    res.status(errorRes.status).json({ message: errorRes.message});
    return;
  }
}
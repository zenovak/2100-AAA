import prisma from "@/utils/server/prisma";


/**
 * Callback API to update user received from backend
 * @param {*} req 
 * @param {*} res 
 */
export default async function handler(req, res) {
  const snooze = ms => new Promise(resolve => setTimeout(resolve, ms));

  const { id, logs, output, status } = req.body;

  let retries = 5;
  while (retries > 0) {
    try {
      const dbTask = await prisma.task.update({
        where: {
          id: id
        },
        data: {
          status: status,
          logs: JSON.stringify(logs),
          output: JSON.stringify(output)
        }
      });

      dbTask.logs = JSON.parse(dbTask.logs);
      dbTask.output = JSON.parse(dbTask.output);

      // fire notifications
      if (dbTask.callback) {
        await fireCallback({ url: dbTask.callback, taskData: dbTask});
      }
      res.status(200).json(dbTask);
      return;
    } catch (error) {
      await snooze(2000);
      console.log(error);
      retries--
    }
  }
  res.status(500).json({ message: "Unable to update user data" });
  return;
}

/**
 * Fires a callback notification
 * @param {*} url callback url
 * @param {*} taskData the task data
 * @param {*} onSuccess 
 * @param {*} onError 
 * @returns 
 */
async function fireCallback({ url, taskData }, onSuccess, onError) {
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(taskData)
    });

    if (!res.ok) {
      const error = new Error("Failed to make callback call");
      error.info = await res.json();
      error.status = res.status;
      throw error;
    }

    const data = await res.json();
    if (onSuccess) {
      onSuccess(data);
    }

    return data;
  } catch (error) {
    console.log(error);
    onError && onError(error);
    return error;
  }
}
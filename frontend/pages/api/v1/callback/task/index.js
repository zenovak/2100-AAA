import prisma from "@/utils/server/prisma";


/**
 * Callback API to update user received from backend
 * @param {*} req 
 * @param {*} res 
 */
export default async function handler(req, res) {
    const snooze = ms => new Promise(resolve => setTimeout(resolve, ms));

    const { id, logs, output } = req.body;


    if (!output instanceof String) {
        output = JSON.stringify(output);
    }

    let retries = 5;
    while (retries > 0) {
        try {
            const dbTask = await prisma.task.upsert({
                create: {
                    id: id,
                    logs: JSON.stringify(logs),
                    output: output
                },
                update: {
                    logs: JSON.stringify(logs),
                    output: output
                },
                where: {
                    id: id
                }
            });

            dbTask.logs = JSON.parse(dbTask.logs);
            dbTask.output = JSON.parse(dbTask.output);
            res.status(200).json(dbTask);
            return;
        } catch (error) {
            await snooze(2000);
            console.log(error);
            retries--
        }
    }
    res.status(500).json({message: "Unable to update user data"});
    return;
}
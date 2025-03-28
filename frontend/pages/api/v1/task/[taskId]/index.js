import prisma from "@/utils/server/prisma";


export default async function handler(req, res) {
    const taskId = req.query.taskId;

    try {
        const task = await prisma.task.findUnique({
            where: {
                id: taskId
            }
        });

        if (!task) {
            res.status(404).json({ message: "Task not found"});
            return;
        }

        task.logs = JSON.parse(task.logs);
        task.output = JSON.parse(task.output);
        res.status(200).json(task);
        return;
    } catch (error) {
        console.log(error);
        res.status(500).json({message: error});
        return;
    }
}
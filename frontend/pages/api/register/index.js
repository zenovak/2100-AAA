import prisma from "@/utils/server/prisma";
import { hash } from "bcrypt";


export default async function handler(req, res) {
  if (req.method != "POST") {
    res.status(400).json({ message: "Invalid request method" });
    return
  }

  try {
    const { password, email, name } = req.body;

    if (!email || !password) {
      res.status(400).json({ error: 'Email and password required' });
      return;
    }

    const hashedPassword = await hash(password, 10);
    const user = await prisma.user.create({
      data: {
        email: email,
        password: hashedPassword,
        // OR as defaulting operator. if name is null, -> name == username, and so on
        name: name || email,
      }
    });

    res.status(201).json({ success: true });
    return;
  } catch (error) {
    console.log(error);
    if (error.code && error.code == "P2002") {
      res.status(400).json({ error: 'Email or Username already taken' });
      return;
    }

    res.status(500).json({ error: 'Registration failed' });
    return;
  }
}
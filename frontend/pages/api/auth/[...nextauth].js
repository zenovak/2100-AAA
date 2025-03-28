import prisma from "@/utils/server/prisma";
import { compare } from "bcrypt";
import NextAuth from "next-auth/next"
import CredentialsProvider from "next-auth/providers/credentials";


export const authOptions = {
  secret: process.env.NEXTAUTH_SECRET,
  session: {
    strategy: "jwt",
  },

  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "text", placeholder: "john@gmail.com" },
        password: { label: "Password", type: "password" },
      },

      async authorize(credentials) {
        if (!credentials?.email || !credentials.password) {
          throw new Error("Missing username or password");
        }

        const user = await prisma.user.findUnique({
          where: {
            email: credentials.email
          }
        });

        if (!user) {
          throw new Error("User not found");
        }

        if (!user.password) {
          throw new Error("User account not valid for this type of login")
        }

        const isPasswordValid = await compare(
          credentials.password,
          user.password
        );

        if (!isPasswordValid) {
          throw new Error("Invalid password");
        }

        return user;
      }
    })
  ],

  callbacks: {
    // append additional username field to client session object
    async session({ session, user, token }) {
      session.user.username = token.user.username;
      return session;
    },

    // must also declare jwt callback
    jwt({ token, user }) {
      if (user) {
        token.user = user;
      }
      return token;
    },
  },
  pages: {
    signIn: '/auth/signin',
  },
}


export default NextAuth(authOptions);
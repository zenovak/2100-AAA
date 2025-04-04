import { LoadingSpinner } from "@/components/Primitives/Loading";
import { signIn } from "next-auth/react";
import Link from "next/link";
import { useRouter } from "next/router";
import { useState } from "react";


export default function SignIn() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const [isSigningIn, setIsSigningIn] = useState(false);

  const handleSubmit = async (e) => {
    setIsSigningIn(true);
    e.preventDefault();
    setError("");

    try {
      const result = await signIn("credentials", {
        email,
        password,
        redirect: false,
      });

      if (result?.error) {
        console.log(error);
        setIsSigningIn(false);
        setError("Invalid username or password");
        return;
      }

      router.push("/developers");
    } catch (error) {
      console.error("Sign in error:", error);
      setError("An error occurred during sign in");
      setIsSigningIn(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md space-y-8 p-6 bg-white rounded-lg shadow-md">
        <div>
          <h2 className="text-center text-3xl font-bold">Sign in to your account</h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="text-red-500 text-center text-sm">{error}</div>
          )}
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="text"
                placeholder="john@gmail.com"
                required
                autoComplete="username"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isSigningIn}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white 
              bg-blue-600 hover:bg-blue-700
               disabled:opacity-55 disabled:pointer-events-none"
            >
              {isSigningIn ?
                <LoadingSpinner /> :
                "Sign In"
              }
            </button>
          </div>
        </form>
        <Link href="/auth/signup" className="block mt-4 text-center text-blue-500 hover:underline">
          Dont have an account?
        </Link>
      </div>
    </div>
  );
}
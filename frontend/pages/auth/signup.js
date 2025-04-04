import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import { TextField } from "@/components/Primitives/HookForm/TextField";
import { useForm } from "react-hook-form";
import { registerUser } from "@/utils/client/register";
import { LoadingSpinner } from "@/components/Primitives/Loading";


export default function SignUp() {
  const { register, handleSubmit } = useForm();
  const [error, setError] = useState("");
  const router = useRouter();

  const [isSigningIn, setIsSigningIn] = useState(false);

  async function onSubmit(data) {
    setIsSigningIn(true);
    const response = await registerUser({
      email: data.email,
      password: data.password
    });

    if (response instanceof Error) {
      setError(response.info?.error || "Something went wrong. Try again later");
    } else {
      router.push("/auth/signin");
    }
    setIsSigningIn(false);
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="p-8 bg-white rounded-lg shadow-md w-96">
        <h2 className="text-2xl font-bold mb-6 text-center">Sign Up</h2>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm/6 font-medium text-gray-900 md-4">Email</label>
            <TextField>
              <TextField.Input
                register={register}
                registerProps={{ required: true }}
                id="email"
                type="email"
                name="email"
                autoComplete="username"
                placeholder="john@gmail.com"
              />
            </TextField>
          </div>

          <div>
            <label htmlFor="email" className="block text-sm/6 font-medium text-gray-900 md-4">Password</label>
            <TextField>
              <TextField.Input
                register={register}
                registerProps={{ required: true }}
                id="password"
                type="password"
                name="password"
                autoComplete="new-password"
              />
            </TextField>
          </div>
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button
            type="submit"
            disabled={isSigningIn}
            className="w-full flex justify-center items-center bg-blue-500 text-white p-2 rounded hover:bg-blue-600
              disabled:opacity-55 disabled:pointer-events-none
            "
          >
            {isSigningIn ? 
              <LoadingSpinner /> :
              "Sign Up"
            }
          </button>
        </form>
        <Link href="/auth/signin" className="block mt-4 text-center text-blue-500 hover:underline">
          Already have an account?
        </Link>
      </div>
    </div>
  );
}
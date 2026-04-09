"use client";

import { signIn } from "next-auth/react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center">
      <h1 className="text-5xl font-bold mb-4">Amplifi</h1>
      <p className="text-gray-400 mb-8">AI-powered marketing automation</p>
      <button
        onClick={() => signIn("google", { callbackUrl: "/dashboard" })}
        className="bg-white text-black px-6 py-3 rounded-lg font-medium hover:bg-gray-200 transition"
      >
        Sign in with Google
      </button>
    </main>
  );
}

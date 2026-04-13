"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleDevLogin = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/auth/dev-login", { method: "POST" });
      const data = await res.json();
      localStorage.setItem("amplifi_token", data.access_token);
      router.push("/dashboard");
    } catch {
      alert("Backend not running — start it with: cd backend && uvicorn app.main:app --reload");
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center relative overflow-hidden" style={{ background: 'var(--bg-primary)' }}>
      {/* Background orbs */}
      <div className="absolute top-[20%] left-[15%] w-[400px] h-[400px] rounded-full animate-float pointer-events-none" style={{ background: 'radial-gradient(circle, rgba(34, 211, 187, 0.06) 0%, transparent 70%)' }} />
      <div className="absolute bottom-[20%] right-[15%] w-[350px] h-[350px] rounded-full animate-float pointer-events-none" style={{ background: 'radial-gradient(circle, rgba(96, 165, 250, 0.04) 0%, transparent 70%)', animationDelay: '3s' }} />
      <div className="absolute top-[60%] left-[60%] w-[250px] h-[250px] rounded-full animate-float pointer-events-none" style={{ background: 'radial-gradient(circle, rgba(167, 139, 250, 0.04) 0%, transparent 70%)', animationDelay: '5s' }} />

      <div className="relative z-10 flex flex-col items-center animate-fade-up">
        <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-8 shadow-2xl" style={{ background: 'var(--accent)', boxShadow: '0 8px 32px var(--accent-glow)' }}>
          <span className="text-2xl font-black" style={{ color: 'var(--bg-primary)' }}>A</span>
        </div>

        <h1 className="text-7xl mb-3">
          Amplifi
        </h1>
        <p className="text-lg mb-14" style={{ color: 'var(--text-tertiary)' }}>
          Marketing automation for modern finance
        </p>

        <button
          onClick={handleDevLogin}
          disabled={loading}
          className="btn-primary text-base px-10 py-4 rounded-2xl disabled:opacity-50"
        >
          {loading ? (
            <div className="w-5 h-5 border-2 rounded-full animate-spin" style={{ borderColor: 'var(--bg-primary)', borderTopColor: 'transparent' }} />
          ) : (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          )}
          {loading ? "Connecting..." : "Enter Dashboard"}
        </button>

        <p className="mt-14 label">Cautilya Capital</p>
      </div>
    </main>
  );
}

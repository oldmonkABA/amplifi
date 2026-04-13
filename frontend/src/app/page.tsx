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
    <main className="mesh-bg grain grid-lines flex min-h-screen flex-col items-center justify-center relative">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full pointer-events-none" style={{ background: 'radial-gradient(circle, rgba(217,160,40,0.08) 0%, transparent 60%)' }} />

      <div className="relative z-10 flex flex-col items-center animate-fade-up">
        <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-amber-300 via-amber-500 to-orange-600 flex items-center justify-center mb-10 shadow-2xl shadow-amber-500/30 animate-float">
          <span className="text-3xl font-black text-black">A</span>
        </div>

        <h1 className="text-7xl font-bold tracking-tighter mb-4 text-gradient">
          Amplifi
        </h1>
        <p className="text-white/25 mb-16 text-lg font-medium tracking-wide max-w-sm text-center leading-relaxed">
          AI-powered marketing automation for modern finance
        </p>

        <button
          onClick={handleDevLogin}
          disabled={loading}
          className="group flex items-center gap-3 bg-white text-black px-8 py-4 rounded-2xl font-bold text-[15px] transition-all duration-500 shadow-[0_8px_32px_rgba(255,255,255,0.1)] hover:shadow-[0_16px_48px_rgba(255,255,255,0.15)] hover:scale-105 disabled:opacity-50"
        >
          {loading ? (
            <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
          ) : (
            <svg className="w-5 h-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          )}
          {loading ? "Connecting..." : "Enter Dashboard"}
          <svg className="w-4 h-4 text-black/30 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </button>

        <div className="mt-16 flex items-center gap-3">
          <div className="w-8 h-px bg-white/10" />
          <p className="text-[10px] text-white/15 font-bold tracking-[0.3em] uppercase">
            Cautilya Capital
          </p>
          <div className="w-8 h-px bg-white/10" />
        </div>
      </div>
    </main>
  );
}

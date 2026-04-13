"use client";

import { signIn } from "next-auth/react";

export default function Home() {
  return (
    <main className="mesh-bg grain grid-lines flex min-h-screen flex-col items-center justify-center relative">
      {/* Large ambient glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full pointer-events-none" style={{ background: 'radial-gradient(circle, rgba(217,160,40,0.08) 0%, transparent 60%)' }} />

      <div className="relative z-10 flex flex-col items-center animate-fade-up">
        {/* Logo */}
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
          onClick={() => signIn("google", { callbackUrl: "/dashboard" })}
          className="group flex items-center gap-3 bg-white text-black px-8 py-4 rounded-2xl font-bold text-[15px] transition-all duration-500 shadow-[0_8px_32px_rgba(255,255,255,0.1)] hover:shadow-[0_16px_48px_rgba(255,255,255,0.15)] hover:scale-105"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          Sign in with Google
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

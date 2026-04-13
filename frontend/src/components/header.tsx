"use client";

import Link from "next/link";
import { signOut, useSession } from "next-auth/react";

export function Header() {
  const { data: session } = useSession();

  return (
    <header className="h-16 border-b border-white/[0.04] flex items-center justify-between px-8 bg-black/20 backdrop-blur-sm">
      <Link
        href="/dashboard/campaigns/new"
        className="btn-primary group flex items-center gap-2 text-[15px]"
      >
        <svg className="w-4 h-4 transition-transform group-hover:rotate-90 duration-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
        </svg>
        New Campaign
      </Link>
      <div className="flex items-center gap-6">
        {session?.user?.name ? (
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-amber-400/20 to-amber-600/10 border border-amber-400/15 flex items-center justify-center">
              <span className="text-sm font-bold text-amber-400">
                {session.user.name.charAt(0).toUpperCase()}
              </span>
            </div>
            <span className="text-sm text-white/40 font-medium">{session.user.name}</span>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-white/[0.04] border border-white/[0.06] flex items-center justify-center">
              <span className="text-sm font-bold text-white/30">A</span>
            </div>
            <span className="text-sm text-white/30 font-medium">Arun</span>
          </div>
        )}
        <button
          onClick={() => signOut({ callbackUrl: "/" })}
          className="text-sm text-white/20 hover:text-white/50 transition-colors font-semibold"
        >
          Sign out
        </button>
      </div>
    </header>
  );
}

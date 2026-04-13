"use client";

import Link from "next/link";
import { signOut, useSession } from "next-auth/react";

export function Header() {
  const { data: session } = useSession();
  const name = session?.user?.name || "Arun";

  return (
    <header className="h-[60px] border-b flex items-center justify-between px-8" style={{ borderColor: 'var(--border)' }}>
      <Link href="/dashboard/campaigns/new" className="btn-primary">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
        </svg>
        New Campaign
      </Link>
      <div className="flex items-center gap-5">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold" style={{ background: 'var(--accent-dim)', color: 'var(--accent)' }}>
            {name.charAt(0).toUpperCase()}
          </div>
          <span className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>{name}</span>
        </div>
        <button
          onClick={() => signOut({ callbackUrl: "/" })}
          className="text-sm font-medium transition-colors"
          style={{ color: 'var(--text-tertiary)' }}
          onMouseEnter={(e) => e.currentTarget.style.color = 'var(--text-secondary)'}
          onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-tertiary)'}
        >
          Sign out
        </button>
      </div>
    </header>
  );
}

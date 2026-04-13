"use client";

import Link from "next/link";
import { signOut, useSession } from "next-auth/react";

export function Header() {
  const { data: session } = useSession();

  return (
    <header className="h-14 border-b border-gray-800 flex items-center justify-between px-6">
      <Link
        href="/dashboard/campaigns/new"
        className="text-sm px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium transition"
      >
        New Campaign
      </Link>
      <div className="flex items-center gap-4">
        {session?.user?.name && (
          <span className="text-sm text-gray-400">{session.user.name}</span>
        )}
        <button
          onClick={() => signOut({ callbackUrl: "/" })}
          className="text-sm text-gray-400 hover:text-white transition"
        >
          Sign out
        </button>
      </div>
    </header>
  );
}

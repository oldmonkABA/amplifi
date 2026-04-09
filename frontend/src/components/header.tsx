"use client";

import { signOut, useSession } from "next-auth/react";

export function Header() {
  const { data: session } = useSession();

  return (
    <header className="h-16 border-b border-gray-800 flex items-center justify-between px-6">
      <div />
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

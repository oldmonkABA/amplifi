"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0h4" },
  { label: "Campaigns", href: "/dashboard/campaigns", icon: "M13 10V3L4 14h7v7l9-11h-7z" },
  { label: "Content", href: "/dashboard/content", icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" },
  { label: "Ads", href: "/dashboard/ads", icon: "M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" },
  { label: "Analytics", href: "/dashboard/analytics", icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" },
  { label: "Calendar", href: "/dashboard/calendar", icon: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" },
  { label: "Settings", href: "/dashboard/settings", icon: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z" },
];

function NavIcon({ d }: { d: string }) {
  return (
    <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d={d} />
    </svg>
  );
}

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar-glow w-[280px] flex flex-col bg-[hsl(228,16%,6%)] border-r border-white/[0.04]">
      {/* Logo */}
      <div className="px-6 pt-7 pb-8">
        <Link href="/dashboard" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-300 via-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/25 group-hover:shadow-amber-500/40 transition-shadow duration-500">
            <span className="text-base font-black text-black">A</span>
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight text-gradient block leading-tight">Amplifi</span>
            <span className="text-xs font-semibold text-white/20 tracking-widest uppercase">Marketing AI</span>
          </div>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3">
        <p className="text-xs font-bold uppercase tracking-[0.15em] text-white/15 px-3 mb-3">Navigation</p>
        <div className="space-y-1">
          {navItems.map((item) => {
            const isActive =
              item.href === "/dashboard"
                ? pathname === "/dashboard"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-3 rounded-xl text-[15px] font-medium transition-all duration-200 relative",
                  isActive
                    ? "nav-active bg-white/[0.05] text-amber-400 ml-1"
                    : "text-white/35 hover:text-white/60 hover:bg-white/[0.02]",
                )}
              >
                <NavIcon d={item.icon} />
                {item.label}
                {isActive && (
                  <div className="absolute right-3 w-1.5 h-1.5 rounded-full bg-amber-400 shadow-[0_0_8px_rgba(217,160,40,0.6)]" />
                )}
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Bottom */}
      <div className="px-4 pb-5 space-y-3">
        <div className="rounded-2xl p-4 bg-gradient-to-br from-amber-500/[0.08] to-transparent border border-amber-500/[0.08]">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]" />
            <p className="text-xs font-bold text-white/40 uppercase tracking-widest">Active Site</p>
          </div>
          <p className="text-sm font-semibold text-white/80 truncate">cautilyacapital.com</p>
        </div>
      </div>
    </aside>
  );
}

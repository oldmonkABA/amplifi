"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navItems = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Campaigns", href: "/dashboard/campaigns" },
  { label: "Content", href: "/dashboard/content" },
  { label: "Ads", href: "/dashboard/ads" },
  { label: "Analytics", href: "/dashboard/analytics" },
  { label: "Calendar", href: "/dashboard/calendar" },
  { label: "Settings", href: "/dashboard/settings" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800 p-4 flex flex-col">
      <div className="text-xl font-bold mb-8 px-2">Amplifi</div>
      <nav className="space-y-1 flex-1">
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
                "block px-3 py-2 rounded-lg transition text-sm",
                isActive
                  ? "bg-gray-800 text-white font-medium"
                  : "text-gray-400 hover:bg-gray-800 hover:text-white",
              )}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

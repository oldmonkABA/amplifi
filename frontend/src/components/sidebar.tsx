import Link from "next/link";

const navItems = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Content", href: "/dashboard/content" },
  { label: "Ads", href: "/dashboard/ads" },
  { label: "Analytics", href: "/dashboard/analytics" },
  { label: "Calendar", href: "/dashboard/calendar" },
  { label: "Sites", href: "/dashboard/sites" },
  { label: "Settings", href: "/dashboard/settings" },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800 p-4">
      <div className="text-xl font-bold mb-8 px-2">Amplifi</div>
      <nav className="space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="block px-3 py-2 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white transition"
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}

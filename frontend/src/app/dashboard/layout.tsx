import { Sidebar } from "@/components/sidebar";
import { Header } from "@/components/header";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="mesh-bg grain flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden relative z-10">
        <Header />
        <main className="flex-1 overflow-y-auto p-8 grid-lines">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

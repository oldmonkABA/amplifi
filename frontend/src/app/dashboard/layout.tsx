import { Sidebar } from "@/components/sidebar";
import { Header } from "@/components/header";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden relative">
        {/* Ambient orbs for depth */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] rounded-full pointer-events-none" style={{ background: 'radial-gradient(circle, rgba(34, 211, 187, 0.04) 0%, transparent 70%)' }} />
        <div className="absolute bottom-0 left-[20%] w-[400px] h-[400px] rounded-full pointer-events-none" style={{ background: 'radial-gradient(circle, rgba(96, 165, 250, 0.03) 0%, transparent 70%)' }} />

        <Header />
        <main className="flex-1 overflow-y-auto p-8 surface-main relative z-10">
          <div className="max-w-[1200px] mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

import { Sidebar } from "@/components/sidebar";
import { Header } from "@/components/header";

export default function Dashboard() {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-6">
          <h2 className="text-2xl font-semibold mb-4">Dashboard</h2>
          <p className="text-gray-400">Welcome to Amplifi. Your marketing command center.</p>
        </main>
      </div>
    </div>
  );
}

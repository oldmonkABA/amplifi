import { cn } from "@/lib/utils";

const statusStyles: Record<string, string> = {
  draft: "bg-gray-700 text-gray-300",
  approved: "bg-green-900 text-green-300",
  scheduled: "bg-blue-900 text-blue-300",
  published: "bg-blue-700 text-blue-100",
  rejected: "bg-red-900 text-red-300",
  active: "bg-green-900 text-green-300",
  paused: "bg-amber-900 text-amber-300",
  completed: "bg-gray-700 text-gray-300",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize",
        statusStyles[status] ?? "bg-gray-700 text-gray-300",
      )}
    >
      {status}
    </span>
  );
}

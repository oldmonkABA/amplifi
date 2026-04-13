import { cn } from "@/lib/utils";

const statusConfig: Record<string, { bg: string; text: string; dot: string }> = {
  draft: { bg: "bg-white/[0.04]", text: "text-white/50", dot: "bg-white/30" },
  approved: { bg: "bg-emerald-500/10", text: "text-emerald-400", dot: "bg-emerald-400" },
  scheduled: { bg: "bg-blue-500/10", text: "text-blue-400", dot: "bg-blue-400" },
  published: { bg: "bg-amber-500/10", text: "text-amber-400", dot: "bg-amber-400" },
  rejected: { bg: "bg-red-500/10", text: "text-red-400", dot: "bg-red-400" },
  active: { bg: "bg-emerald-500/10", text: "text-emerald-400", dot: "bg-emerald-400" },
  paused: { bg: "bg-orange-500/10", text: "text-orange-400", dot: "bg-orange-400" },
  completed: { bg: "bg-white/[0.04]", text: "text-white/50", dot: "bg-white/30" },
};

export function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] ?? statusConfig.draft;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold capitalize tracking-wide",
        config.bg,
        config.text,
      )}
    >
      <span className={cn("w-1.5 h-1.5 rounded-full", config.dot)} />
      {status}
    </span>
  );
}

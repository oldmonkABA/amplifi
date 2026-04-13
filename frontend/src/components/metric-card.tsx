import { cn } from "@/lib/utils";

const glowVariants = [
  "metric-glow-amber",
  "metric-glow-blue",
  "metric-glow-emerald",
  "metric-glow-violet",
];

export function MetricCard({
  label,
  value,
  sub,
  index = 0,
}: {
  label: string;
  value: string | number;
  sub?: string;
  index?: number;
}) {
  return (
    <div className={cn(
      "rounded-2xl p-6 border transition-all duration-500 hover:scale-[1.03] cursor-default group",
      glowVariants[index % glowVariants.length],
    )}>
      <p className="text-xs font-bold uppercase tracking-[0.15em] text-white/30 mb-3">{label}</p>
      <p className="text-5xl font-bold tracking-tighter leading-none">{value}</p>
      {sub && <p className="text-sm text-white/25 mt-3 font-medium">{sub}</p>}
    </div>
  );
}

const statusConfig: Record<string, { bg: string; color: string }> = {
  draft:     { bg: "var(--bg-hover)",   color: "var(--text-secondary)" },
  approved:  { bg: "var(--green-dim)",  color: "var(--green)" },
  scheduled: { bg: "var(--blue-dim)",   color: "var(--blue)" },
  published: { bg: "var(--accent-dim)", color: "var(--accent)" },
  rejected:  { bg: "var(--red-dim)",    color: "var(--red)" },
  active:    { bg: "var(--green-dim)",  color: "var(--green)" },
  paused:    { bg: "var(--amber-dim)",  color: "var(--amber)" },
  completed: { bg: "var(--bg-hover)",   color: "var(--text-secondary)" },
};

export function StatusBadge({ status }: { status: string }) {
  const cfg = statusConfig[status] ?? statusConfig.draft;
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold capitalize"
      style={{ background: cfg.bg, color: cfg.color }}
    >
      <span className="w-1.5 h-1.5 rounded-full" style={{ background: cfg.color }} />
      {status}
    </span>
  );
}

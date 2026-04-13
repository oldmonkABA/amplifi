const variants = ["metric-teal", "metric-blue", "metric-green", "metric-violet"];

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
    <div className={`card rounded-2xl p-6 ${variants[index % variants.length]}`}>
      <p className="label mb-3">{label}</p>
      <p className="text-4xl font-light tracking-tight">
        {value}
      </p>
      {sub && <p className="text-sm mt-2" style={{ color: 'var(--text-tertiary)' }}>{sub}</p>}
    </div>
  );
}

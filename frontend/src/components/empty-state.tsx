export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
      <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-500/10 to-amber-600/5 border border-amber-500/10 flex items-center justify-center mb-5">
        <svg className="w-7 h-7 text-amber-500/40" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
        </svg>
      </div>
      <h3 className="text-lg font-bold mb-1.5 tracking-tight">{title}</h3>
      <p className="text-base text-white/30 mb-5 max-w-sm font-medium">{description}</p>
      {action}
    </div>
  );
}

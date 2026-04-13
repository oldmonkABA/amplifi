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
    <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-up">
      <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-5" style={{ background: 'var(--accent-dim)' }}>
        <svg className="w-6 h-6" style={{ color: 'var(--accent)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
        </svg>
      </div>
      <h3 className="text-xl mb-2">{title}</h3>
      <p className="text-sm mb-6" style={{ color: 'var(--text-tertiary)', maxWidth: '360px' }}>{description}</p>
      {action}
    </div>
  );
}

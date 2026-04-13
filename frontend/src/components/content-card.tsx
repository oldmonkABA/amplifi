"use client";

import type { ContentResponse } from "@/types/api";
import { StatusBadge } from "@/components/status-badge";
import { PlatformIcon } from "@/components/platform-icon";

export function ContentCard({
  content,
  onApprove,
  onReject,
}: {
  content: ContentResponse;
  onApprove?: (id: string) => void;
  onReject?: (id: string) => void;
}) {
  return (
    <div className="card card-interactive rounded-2xl p-5">
      <div className="flex items-center justify-between mb-3">
        <PlatformIcon platform={content.platform} />
        <StatusBadge status={content.status} />
      </div>
      <h4 className="text-base font-semibold mb-1.5 line-clamp-1">{content.title}</h4>
      <p className="text-sm line-clamp-2 mb-4 leading-relaxed" style={{ color: 'var(--text-tertiary)' }}>{content.body}</p>
      {content.status === "draft" && (onApprove || onReject) && (
        <div className="flex gap-2 pt-3" style={{ borderTop: '1px solid var(--border)' }}>
          {onApprove && (
            <button
              onClick={(e) => { e.stopPropagation(); onApprove(content.id); }}
              className="text-sm px-4 py-1.5 rounded-lg font-semibold transition-colors"
              style={{ background: 'var(--green-dim)', color: 'var(--green)' }}
            >
              Approve
            </button>
          )}
          {onReject && (
            <button
              onClick={(e) => { e.stopPropagation(); onReject(content.id); }}
              className="text-sm px-4 py-1.5 rounded-lg font-semibold transition-colors"
              style={{ background: 'var(--red-dim)', color: 'var(--red)' }}
            >
              Reject
            </button>
          )}
        </div>
      )}
    </div>
  );
}

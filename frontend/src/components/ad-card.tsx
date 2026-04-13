"use client";

import type { AdResponse } from "@/types/api";
import { StatusBadge } from "@/components/status-badge";

export function AdCard({
  ad,
  onApprove,
  onReject,
}: {
  ad: AdResponse;
  onApprove?: (id: string) => void;
  onReject?: (id: string) => void;
}) {
  return (
    <div className="card card-interactive rounded-2xl overflow-hidden">
      {ad.image_url && (
        <img src={ad.image_url} alt="Ad creative" className="w-full h-40 object-cover" />
      )}
      <div className="p-5">
        <div className="flex items-center justify-between mb-3">
          <span className="label">Ad</span>
          <StatusBadge status={ad.status} />
        </div>
        <h4 className="text-base font-semibold mb-1.5 line-clamp-1">{ad.headline}</h4>
        <p className="text-sm line-clamp-2 mb-1 leading-relaxed" style={{ color: 'var(--text-tertiary)' }}>{ad.description}</p>
        {ad.status === "draft" && (onApprove || onReject) && (
          <div className="flex gap-2 pt-3 mt-3" style={{ borderTop: '1px solid var(--border)' }}>
            {onApprove && (
              <button
                onClick={(e) => { e.stopPropagation(); onApprove(ad.id); }}
                className="text-sm px-4 py-1.5 rounded-lg font-semibold transition-colors"
                style={{ background: 'var(--green-dim)', color: 'var(--green)' }}
              >
                Approve
              </button>
            )}
            {onReject && (
              <button
                onClick={(e) => { e.stopPropagation(); onReject(ad.id); }}
                className="text-sm px-4 py-1.5 rounded-lg font-semibold transition-colors"
                style={{ background: 'var(--red-dim)', color: 'var(--red)' }}
              >
                Reject
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

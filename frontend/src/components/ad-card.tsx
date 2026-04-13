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
    <div className="glass-card rounded-2xl p-5 group hover:scale-[1.01] transition-all duration-300">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-bold uppercase tracking-widest text-white/20">Ad</span>
        <StatusBadge status={ad.status} />
      </div>
      <h4 className="font-bold text-base mb-1.5 line-clamp-1 tracking-tight">{ad.headline}</h4>
      <p className="text-sm text-white/30 line-clamp-2 mb-1 leading-relaxed">{ad.description}</p>
      {ad.display_url && (
        <p className="text-sm text-amber-400/60 mb-4 font-medium">{ad.display_url}</p>
      )}
      {ad.status === "draft" && (onApprove || onReject) && (
        <div className="flex gap-2 pt-3 border-t border-white/[0.04]">
          {onApprove && (
            <button
              onClick={() => onApprove(ad.id)}
              className="text-sm px-5 py-2 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 font-semibold transition-colors"
            >
              Approve
            </button>
          )}
          {onReject && (
            <button
              onClick={() => onReject(ad.id)}
              className="text-sm px-5 py-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 font-semibold transition-colors"
            >
              Reject
            </button>
          )}
        </div>
      )}
    </div>
  );
}

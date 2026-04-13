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
    <div className="glass-card rounded-2xl p-5 group hover:scale-[1.01] transition-all duration-300">
      <div className="flex items-center justify-between mb-3">
        <PlatformIcon platform={content.platform} />
        <StatusBadge status={content.status} />
      </div>
      <h4 className="font-bold text-base mb-1.5 line-clamp-1 tracking-tight">{content.title}</h4>
      <p className="text-sm text-white/30 line-clamp-2 mb-4 leading-relaxed">{content.body}</p>
      {content.status === "draft" && (onApprove || onReject) && (
        <div className="flex gap-2 pt-3 border-t border-white/[0.04]">
          {onApprove && (
            <button
              onClick={() => onApprove(content.id)}
              className="text-sm px-5 py-2 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 font-semibold transition-colors"
            >
              Approve
            </button>
          )}
          {onReject && (
            <button
              onClick={() => onReject(content.id)}
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

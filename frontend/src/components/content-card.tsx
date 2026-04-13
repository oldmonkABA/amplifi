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
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <PlatformIcon platform={content.platform} />
        <StatusBadge status={content.status} />
      </div>
      <h4 className="font-medium mb-1 line-clamp-1">{content.title}</h4>
      <p className="text-sm text-gray-400 line-clamp-2 mb-3">{content.body}</p>
      {content.status === "draft" && (onApprove || onReject) && (
        <div className="flex gap-2">
          {onApprove && (
            <button
              onClick={() => onApprove(content.id)}
              className="text-xs px-3 py-1 rounded bg-green-800 hover:bg-green-700 text-green-200 transition"
            >
              Approve
            </button>
          )}
          {onReject && (
            <button
              onClick={() => onReject(content.id)}
              className="text-xs px-3 py-1 rounded bg-red-900 hover:bg-red-800 text-red-200 transition"
            >
              Reject
            </button>
          )}
        </div>
      )}
    </div>
  );
}

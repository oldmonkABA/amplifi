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
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <StatusBadge status={ad.status} />
      </div>
      <h4 className="font-medium mb-1 line-clamp-1">{ad.headline}</h4>
      <p className="text-sm text-gray-400 line-clamp-2 mb-1">{ad.description}</p>
      {ad.display_url && (
        <p className="text-xs text-blue-400 mb-3">{ad.display_url}</p>
      )}
      {ad.status === "draft" && (onApprove || onReject) && (
        <div className="flex gap-2">
          {onApprove && (
            <button
              onClick={() => onApprove(ad.id)}
              className="text-xs px-3 py-1 rounded bg-green-800 hover:bg-green-700 text-green-200 transition"
            >
              Approve
            </button>
          )}
          {onReject && (
            <button
              onClick={() => onReject(ad.id)}
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

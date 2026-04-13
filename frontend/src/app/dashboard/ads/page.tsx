"use client";

import { useState } from "react";
import { useApi, useMutation } from "@/hooks/use-api";
import { getAds, updateAd } from "@/lib/api/ads";
import { StatusBadge } from "@/components/status-badge";
import { EmptyState } from "@/components/empty-state";
import Link from "next/link";
import type { AdListResponse, AdStatus } from "@/types/api";

export default function AdsPage() {
  const [statusFilter, setStatusFilter] = useState<AdStatus | "">("");

  const { data, loading, refetch } = useApi<AdListResponse>(
    (token) =>
      getAds(token, {
        status: statusFilter || undefined,
        limit: 50,
      }),
    [statusFilter],
  );

  const updateMut = useMutation((token: string, args: { id: string; status: AdStatus }) =>
    updateAd(token, args.id, { status: args.status }),
  );

  const handleApprove = async (id: string) => {
    await updateMut.execute({ id, status: "active" });
    refetch();
  };

  const handleReject = async (id: string) => {
    await updateMut.execute({ id, status: "rejected" });
    refetch();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl mb-6">Ads</h2>
        <Link
          href="/dashboard/campaigns/new"
          className="btn-primary"
        >
          Generate Ads
        </Link>
      </div>

      <div className="flex gap-3 mb-4">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as AdStatus | "")}
          className="rounded-lg px-3 py-1.5 text-sm"
          style={{ borderColor: 'var(--border)' }}
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="active">Active</option>
          <option value="paused">Paused</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      {loading ? (
        <p className="text-sm" style={{ color: 'var(--text-tertiary)' }}>Loading ads...</p>
      ) : !data?.items.length ? (
        <EmptyState
          title="No ads found"
          description="Generate ads through a campaign."
        />
      ) : (
        <div className="card overflow-hidden" style={{ borderColor: 'var(--border)' }}>
          <table className="data-table w-full text-sm">
            <thead>
              <tr className="text-left" style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                <th className="px-4 py-3 font-medium">Headline</th>
                <th className="px-4 py-3 font-medium">Description</th>
                <th className="px-4 py-3 font-medium">URL</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((ad) => (
                <tr key={ad.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td className="px-4 py-3 font-medium" style={{ color: 'var(--text-primary)' }}>{ad.headline}</td>
                  <td className="px-4 py-3 max-w-xs truncate" style={{ color: 'var(--text-secondary)' }}>{ad.description}</td>
                  <td className="px-4 py-3 text-xs" style={{ color: 'var(--text-tertiary)' }}>{ad.display_url || ad.final_url}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={ad.status} />
                  </td>
                  <td className="px-4 py-3">
                    {ad.status === "draft" && (
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleApprove(ad.id)}
                          className="text-xs px-2 py-1 rounded transition"
                          style={{ background: 'var(--green-dim)', color: 'var(--green)' }}
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => handleReject(ad.id)}
                          className="text-xs px-2 py-1 rounded transition"
                          style={{ background: 'var(--red-dim)', color: 'var(--red)' }}
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

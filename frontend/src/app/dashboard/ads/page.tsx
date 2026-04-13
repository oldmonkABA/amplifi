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
        <h2 className="text-2xl font-semibold">Ads</h2>
        <Link
          href="/dashboard/campaigns/new"
          className="text-sm px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium transition"
        >
          Generate Ads
        </Link>
      </div>

      <div className="flex gap-3 mb-4">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as AdStatus | "")}
          className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-sm text-gray-300"
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="active">Active</option>
          <option value="paused">Paused</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      {loading ? (
        <p className="text-gray-500 text-sm">Loading ads...</p>
      ) : !data?.items.length ? (
        <EmptyState
          title="No ads found"
          description="Generate ads through a campaign."
        />
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-left text-gray-400">
                <th className="px-4 py-3 font-medium">Headline</th>
                <th className="px-4 py-3 font-medium">Description</th>
                <th className="px-4 py-3 font-medium">URL</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((ad) => (
                <tr key={ad.id} className="border-b border-gray-800 last:border-0 hover:bg-gray-800/50">
                  <td className="px-4 py-3 font-medium">{ad.headline}</td>
                  <td className="px-4 py-3 text-gray-400 max-w-xs truncate">{ad.description}</td>
                  <td className="px-4 py-3 text-blue-400 text-xs">{ad.display_url || ad.final_url}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={ad.status} />
                  </td>
                  <td className="px-4 py-3">
                    {ad.status === "draft" && (
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleApprove(ad.id)}
                          className="text-xs px-2 py-1 rounded bg-green-900 hover:bg-green-800 text-green-300 transition"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => handleReject(ad.id)}
                          className="text-xs px-2 py-1 rounded bg-red-900 hover:bg-red-800 text-red-300 transition"
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

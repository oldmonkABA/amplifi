"use client";

import { useState } from "react";
import Link from "next/link";
import { useApi } from "@/hooks/use-api";
import { getCampaigns } from "@/lib/api/campaigns";
import { StatusBadge } from "@/components/status-badge";
import { PlatformIcon } from "@/components/platform-icon";
import { EmptyState } from "@/components/empty-state";
import type { CampaignListResponse, AdPlatform, CampaignStatus } from "@/types/api";

const SITE_ID = "default";

export default function CampaignsPage() {
  const [platformFilter, setPlatformFilter] = useState<AdPlatform | "">("");
  const [statusFilter, setStatusFilter] = useState<CampaignStatus | "">("");

  const { data, loading } = useApi<CampaignListResponse>(
    (token) =>
      getCampaigns(token, {
        site_id: SITE_ID,
        platform: platformFilter || undefined,
        status: statusFilter || undefined,
        limit: 50,
      }),
    [platformFilter, statusFilter],
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold">Campaigns</h2>
        <Link
          href="/dashboard/campaigns/new"
          className="text-sm px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium transition"
        >
          New Campaign
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-4">
        <select
          value={platformFilter}
          onChange={(e) => setPlatformFilter(e.target.value as AdPlatform | "")}
          className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-sm text-gray-300"
        >
          <option value="">All Platforms</option>
          <option value="google_ads">Google Ads</option>
          <option value="facebook_ads">Facebook Ads</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as CampaignStatus | "")}
          className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-sm text-gray-300"
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="active">Active</option>
          <option value="paused">Paused</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {/* Table */}
      {loading ? (
        <p className="text-gray-500 text-sm">Loading campaigns...</p>
      ) : !data?.items.length ? (
        <EmptyState
          title="No campaigns found"
          description="Create a campaign to start generating content and ads."
          action={
            <Link
              href="/dashboard/campaigns/new"
              className="text-sm px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition"
            >
              New Campaign
            </Link>
          }
        />
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-left text-gray-400">
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Platform</th>
                <th className="px-4 py-3 font-medium">Objective</th>
                <th className="px-4 py-3 font-medium">Budget/Day</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Created</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((c) => (
                <tr key={c.id} className="border-b border-gray-800 last:border-0 hover:bg-gray-800/50">
                  <td className="px-4 py-3">
                    <Link href={`/dashboard/campaigns/${c.id}`} className="text-blue-400 hover:text-blue-300">
                      {c.name}
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <PlatformIcon platform={c.platform} />
                  </td>
                  <td className="px-4 py-3 capitalize text-gray-400">{c.objective}</td>
                  <td className="px-4 py-3 text-gray-300">${(c.daily_budget_cents / 100).toFixed(2)}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={c.status} />
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {new Date(c.created_at).toLocaleDateString()}
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

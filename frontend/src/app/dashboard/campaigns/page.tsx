"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useApi } from "@/hooks/use-api";
import { getCampaigns } from "@/lib/api/campaigns";
import { StatusBadge } from "@/components/status-badge";
import { PlatformIcon } from "@/components/platform-icon";
import { EmptyState } from "@/components/empty-state";
import type { CampaignListResponse, AdPlatform, CampaignStatus } from "@/types/api";

import { DEV_SITE_ID as SITE_ID } from "@/lib/constants";

export default function CampaignsPage() {
  const router = useRouter();
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
        <h2 className="text-3xl font-bold tracking-tight">Campaigns</h2>
        <Link
          href="/dashboard/campaigns/new"
          className="btn-primary flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          New Campaign
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-6">
        <select
          value={platformFilter}
          onChange={(e) => setPlatformFilter(e.target.value as AdPlatform | "")}
          className="glass-card rounded-xl px-4 py-2.5 text-sm text-white/60 font-medium"
        >
          <option value="">All Platforms</option>
          <option value="google_ads">Google Ads</option>
          <option value="facebook_ads">Facebook Ads</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as CampaignStatus | "")}
          className="glass-card rounded-xl px-4 py-2.5 text-sm text-white/60 font-medium"
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="active">Active</option>
          <option value="paused">Paused</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {/* List */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="glass-card rounded-2xl p-5 animate-shimmer h-[80px]" />
          ))}
        </div>
      ) : !data?.items.length ? (
        <EmptyState
          title="No campaigns found"
          description="Create a campaign to start generating content and ads."
          action={
            <Link
              href="/dashboard/campaigns/new"
              className="btn-primary"
            >
              New Campaign
            </Link>
          }
        />
      ) : (
        <div className="space-y-2.5">
          {data.items.map((c) => (
            <div
              key={c.id}
              onClick={() => router.push(`/dashboard/campaigns/${c.id}`)}
              className="flex items-center gap-4 p-5 glass-card accent-card rounded-2xl cursor-pointer group"
            >
              <PlatformIcon platform={c.platform} />
              <div className="flex-1 min-w-0">
                <p className="text-base font-semibold truncate tracking-tight group-hover:text-amber-400 transition-colors duration-300">
                  {c.name}
                </p>
                <p className="text-sm text-white/25 font-medium mt-0.5">
                  ${(c.daily_budget_cents / 100).toFixed(2)}/day &middot; {c.objective}
                </p>
              </div>
              <StatusBadge status={c.status} />
              <span className="text-sm text-white/20">
                {new Date(c.created_at).toLocaleDateString()}
              </span>
              <svg className="w-5 h-5 text-white/10 group-hover:text-white/30 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

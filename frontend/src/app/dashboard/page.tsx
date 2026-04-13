"use client";

import { useApi } from "@/hooks/use-api";
import { getOverview } from "@/lib/api/analytics";
import { getContent } from "@/lib/api/content";
import { getCampaigns } from "@/lib/api/campaigns";
import { MetricCard } from "@/components/metric-card";
import { ContentCard } from "@/components/content-card";
import { StatusBadge } from "@/components/status-badge";
import { EmptyState } from "@/components/empty-state";
import { PlatformIcon } from "@/components/platform-icon";
import Link from "next/link";
import type { SiteOverviewResponse, ContentListResponse, CampaignListResponse } from "@/types/api";

const SITE_ID = "default";

export default function DashboardPage() {
  const { data: overview, loading: overviewLoading } = useApi<SiteOverviewResponse>(
    (token) => getOverview(token, SITE_ID),
  );
  const { data: drafts, loading: draftsLoading, refetch: refetchDrafts } = useApi<ContentListResponse>(
    (token) => getContent(token, { site_id: SITE_ID, status: "draft", limit: 5 }),
  );
  const { data: campaigns, loading: campaignsLoading } = useApi<CampaignListResponse>(
    (token) => getCampaigns(token, { site_id: SITE_ID, limit: 5 }),
  );

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6">Dashboard</h2>

      {/* Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <MetricCard
          label="Total Campaigns"
          value={overviewLoading ? "..." : overview?.total_campaigns ?? 0}
        />
        <MetricCard
          label="Content Pieces"
          value={overviewLoading ? "..." : overview?.total_content ?? 0}
        />
        <MetricCard
          label="Total Ads"
          value={overviewLoading ? "..." : overview?.total_ads ?? 0}
        />
        <MetricCard
          label="Subscribers"
          value={overviewLoading ? "..." : overview?.active_subscribers ?? 0}
          sub={overview ? `${overview.total_subscribers} total` : undefined}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Campaigns */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-medium">Recent Campaigns</h3>
            <Link href="/dashboard/campaigns" className="text-sm text-blue-400 hover:text-blue-300">
              View all
            </Link>
          </div>
          {campaignsLoading ? (
            <p className="text-gray-500 text-sm">Loading...</p>
          ) : !campaigns?.items.length ? (
            <EmptyState
              title="No campaigns yet"
              description="Create your first campaign to get started."
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
            <div className="space-y-2">
              {campaigns.items.map((c) => (
                <Link
                  key={c.id}
                  href={`/dashboard/campaigns/${c.id}`}
                  className="flex items-center gap-3 p-3 bg-gray-900 border border-gray-800 rounded-lg hover:border-gray-700 transition"
                >
                  <PlatformIcon platform={c.platform} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{c.name}</p>
                    <p className="text-xs text-gray-500">
                      ${(c.daily_budget_cents / 100).toFixed(2)}/day
                    </p>
                  </div>
                  <StatusBadge status={c.status} />
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Pending Approvals */}
        <div>
          <h3 className="text-lg font-medium mb-3">Pending Approvals</h3>
          {draftsLoading ? (
            <p className="text-gray-500 text-sm">Loading...</p>
          ) : !drafts?.items.length ? (
            <EmptyState
              title="All caught up"
              description="No content waiting for approval."
            />
          ) : (
            <div className="space-y-3">
              {drafts.items.map((item) => (
                <ContentCard
                  key={item.id}
                  content={item}
                  onApprove={() => refetchDrafts()}
                  onReject={() => refetchDrafts()}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

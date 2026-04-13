"use client";

import { useApi, useMutation } from "@/hooks/use-api";
import { getOverview } from "@/lib/api/analytics";
import { getContent, approveContent, rejectContent } from "@/lib/api/content";
import { getCampaigns } from "@/lib/api/campaigns";
import { MetricCard } from "@/components/metric-card";
import { StatusBadge } from "@/components/status-badge";
import { PlatformIcon } from "@/components/platform-icon";
import { EmptyState } from "@/components/empty-state";
import Link from "next/link";
import { DEV_SITE_ID as SITE_ID } from "@/lib/constants";
import type { SiteOverviewResponse, ContentListResponse, CampaignListResponse } from "@/types/api";

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

  const approveMut = useMutation((token: string, id: string) => approveContent(token, id));
  const rejectMut = useMutation((token: string, id: string) => rejectContent(token, id));

  const handleApprove = async (id: string) => { await approveMut.execute(id); refetchDrafts(); };
  const handleReject = async (id: string) => { await rejectMut.execute(id); refetchDrafts(); };

  const now = new Date();
  const dateStr = now.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" });

  return (
    <div>
      {/* Header */}
      <div className="mb-10 animate-fade-up">
        <p className="label mb-2" style={{ color: 'var(--accent)' }}>Cautilya Capital</p>
        <div className="flex items-end justify-between">
          <h2 className="text-5xl">
            Dashboard
          </h2>
          <p className="text-base pb-1" style={{ color: 'var(--text-tertiary)' }}>{dateStr}</p>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10 stagger">
        <MetricCard
          label="Campaigns"
          value={overviewLoading ? "\u2014" : overview?.total_campaigns ?? 0}
          sub={overview ? `${overview.total_ads} ads` : undefined}
          index={0}
        />
        <MetricCard
          label="Content"
          value={overviewLoading ? "\u2014" : overview?.total_content ?? 0}
          index={1}
        />
        <MetricCard
          label="Ads"
          value={overviewLoading ? "\u2014" : overview?.total_ads ?? 0}
          index={2}
        />
        <MetricCard
          label="Subscribers"
          value={overviewLoading ? "\u2014" : overview?.active_subscribers ?? 0}
          sub={overview ? `${overview.total_subscribers} total` : undefined}
          index={3}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        {/* Campaigns */}
        <div className="lg:col-span-3 animate-fade-up" style={{ animationDelay: '150ms' }}>
          <div className="flex items-center justify-between mb-5">
            <h3 className="text-2xl">Campaigns</h3>
            <Link href="/dashboard/campaigns" className="text-sm font-semibold transition-colors" style={{ color: 'var(--accent)' }}>
              View all &rarr;
            </Link>
          </div>
          {campaignsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="card rounded-2xl p-5 animate-shimmer h-[72px]" />
              ))}
            </div>
          ) : !campaigns?.items.length ? (
            <EmptyState
              title="No campaigns yet"
              description="Create your first campaign to start driving traffic."
              action={<Link href="/dashboard/campaigns/new" className="btn-primary">New Campaign</Link>}
            />
          ) : (
            <div className="space-y-2">
              {campaigns.items.map((c) => (
                <Link
                  key={c.id}
                  href={`/dashboard/campaigns/${c.id}`}
                  className="card card-interactive rounded-2xl p-5 flex items-center gap-4"
                >
                  <PlatformIcon platform={c.platform} />
                  <div className="flex-1 min-w-0">
                    <p className="text-[15px] font-semibold truncate">{c.name}</p>
                    <p className="text-sm mt-0.5" style={{ color: 'var(--text-tertiary)' }}>
                      ${(c.daily_budget_cents / 100).toFixed(0)}/day &middot; {c.objective}
                    </p>
                  </div>
                  <StatusBadge status={c.status} />
                  <svg className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--text-tertiary)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Pending */}
        <div className="lg:col-span-2 animate-fade-up" style={{ animationDelay: '300ms' }}>
          <h3 className="text-2xl mb-5">Pending Approval</h3>
          {draftsLoading ? (
            <div className="space-y-3">
              {[1, 2].map((i) => (
                <div key={i} className="card rounded-2xl p-5 animate-shimmer h-[140px]" />
              ))}
            </div>
          ) : !drafts?.items.length ? (
            <EmptyState title="All clear" description="Nothing waiting for your review." />
          ) : (
            <div className="space-y-3">
              {drafts.items.map((item) => (
                <div key={item.id} className="card rounded-2xl p-5">
                  <div className="flex items-center justify-between mb-3">
                    <PlatformIcon platform={item.platform} />
                    <StatusBadge status={item.status} />
                  </div>
                  <h4 className="text-[15px] font-semibold mb-1">{item.title}</h4>
                  <p className="text-sm line-clamp-2 leading-relaxed mb-4" style={{ color: 'var(--text-tertiary)' }}>{item.body}</p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleApprove(item.id)}
                      className="text-sm px-4 py-1.5 rounded-lg font-semibold transition-colors"
                      style={{ background: 'var(--green-dim)', color: 'var(--green)' }}
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => handleReject(item.id)}
                      className="text-sm px-4 py-1.5 rounded-lg font-semibold transition-colors"
                      style={{ background: 'var(--red-dim)', color: 'var(--red)' }}
                    >
                      Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

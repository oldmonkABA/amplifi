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
  const dateStr = now.toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" });

  return (
    <div>
      {/* Hero */}
      <div className="mb-10 animate-fade-up">
        <div className="flex items-end justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-amber-400/60 mb-2">Welcome back</p>
            <h2 className="text-5xl font-bold tracking-tight leading-[1.1]">
              Command<br />
              <span className="text-gradient">Center</span>
            </h2>
          </div>
          <div className="text-right pb-1">
            <p className="text-xs font-bold uppercase tracking-[0.15em] text-white/20 mb-1">Cautilya Capital</p>
            <p className="text-base text-white/40 font-medium">{dateStr}</p>
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5 mb-10 stagger">
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

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recent Campaigns */}
        <div className="lg:col-span-7 animate-fade-up" style={{ animationDelay: '200ms' }}>
          <div className="flex items-center justify-between mb-5">
            <h3 className="text-xl font-bold tracking-tight">Recent Campaigns</h3>
            <Link href="/dashboard/campaigns" className="text-sm text-amber-400/60 hover:text-amber-400 font-semibold transition-colors">
              View all &rarr;
            </Link>
          </div>
          {campaignsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="glass-card rounded-2xl p-4 animate-shimmer h-[72px]" />
              ))}
            </div>
          ) : !campaigns?.items.length ? (
            <EmptyState
              title="No campaigns yet"
              description="Create your first campaign to start driving traffic."
              action={
                <Link href="/dashboard/campaigns/new" className="btn-primary">
                  New Campaign
                </Link>
              }
            />
          ) : (
            <div className="space-y-2.5">
              {campaigns.items.map((c) => (
                <Link
                  key={c.id}
                  href={`/dashboard/campaigns/${c.id}`}
                  className="flex items-center gap-4 p-5 glass-card accent-card rounded-2xl group"
                >
                  <PlatformIcon platform={c.platform} />
                  <div className="flex-1 min-w-0">
                    <p className="text-base font-semibold truncate tracking-tight group-hover:text-amber-400 transition-colors duration-300">{c.name}</p>
                    <p className="text-sm text-white/25 font-medium mt-0.5">
                      ${(c.daily_budget_cents / 100).toFixed(0)}/day &middot; {c.objective}
                    </p>
                  </div>
                  <StatusBadge status={c.status} />
                  <svg className="w-5 h-5 text-white/10 group-hover:text-white/30 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Pending Approvals */}
        <div className="lg:col-span-5 animate-fade-up" style={{ animationDelay: '400ms' }}>
          <h3 className="text-xl font-bold tracking-tight mb-5">Pending Approval</h3>
          {draftsLoading ? (
            <div className="space-y-3">
              {[1, 2].map((i) => (
                <div key={i} className="glass-card rounded-2xl p-4 animate-shimmer h-[120px]" />
              ))}
            </div>
          ) : !drafts?.items.length ? (
            <EmptyState
              title="All clear"
              description="Nothing waiting for your approval."
            />
          ) : (
            <div className="space-y-2.5">
              {drafts.items.map((item) => (
                <div key={item.id} className="glass-card rounded-2xl p-5">
                  <div className="flex items-center justify-between mb-3">
                    <PlatformIcon platform={item.platform} />
                    <StatusBadge status={item.status} />
                  </div>
                  <h4 className="text-base font-semibold mb-1.5 tracking-tight">{item.title}</h4>
                  <p className="text-sm text-white/25 line-clamp-2 leading-relaxed mb-4">{item.body}</p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleApprove(item.id)}
                      className="text-sm px-5 py-2 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 font-semibold transition-colors"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => handleReject(item.id)}
                      className="text-sm px-5 py-2 rounded-lg bg-white/[0.03] hover:bg-white/[0.06] text-white/30 font-semibold transition-colors"
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

"use client";

import { MetricCard } from "@/components/metric-card";
import { StatusBadge } from "@/components/status-badge";
import { PlatformIcon } from "@/components/platform-icon";
import Link from "next/link";

const DEMO_CAMPAIGNS = [
  { id: "1", name: "Q2 Tax-Saving Investment Guide", platform: "google_ads", objective: "traffic", daily_budget_cents: 2500, status: "active" },
  { id: "2", name: "Mutual Fund Comparison Series", platform: "linkedin", objective: "leads", daily_budget_cents: 1500, status: "active" },
  { id: "3", name: "SIP Calculator Launch", platform: "twitter", objective: "awareness", daily_budget_cents: 1000, status: "draft" },
  { id: "4", name: "NPS vs PPF Deep Dive", platform: "blog", objective: "traffic", daily_budget_cents: 500, status: "scheduled" },
];

const DEMO_CONTENT = [
  { id: "1", title: "5 Tax-Saving ELSS Funds for 2026", platform: "blog", status: "draft", body: "A comprehensive analysis of the top ELSS mutual funds that can help you save up to \u20B946,800 in taxes under Section 80C..." },
  { id: "2", title: "Why SIPs beat lump-sum investing", platform: "twitter", status: "draft", body: "Thread: The math behind systematic investment plans and why rupee cost averaging works in volatile markets..." },
  { id: "3", title: "Understanding debt-to-equity ratios", platform: "linkedin", status: "draft", body: "A guide for new investors on how to evaluate company fundamentals using the D/E ratio..." },
];

const DEMO_ACTIVITY = [
  { action: "Published", item: "Market Weekly Roundup #23", time: "2h ago", color: "bg-amber-400" },
  { action: "Approved", item: "Google Ads: ELSS Campaign", time: "5h ago", color: "bg-emerald-400" },
  { action: "Generated", item: "3 LinkedIn posts", time: "1d ago", color: "bg-blue-400" },
  { action: "Scheduled", item: "Email: Monthly Newsletter", time: "1d ago", color: "bg-violet-400" },
];

export default function DashboardPage() {
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
            <p className="text-base text-white/40 font-medium">Sunday, Apr 13</p>
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5 mb-10 stagger">
        <MetricCard label="Campaigns" value={12} sub="4 active" index={0} />
        <MetricCard label="Content" value={84} sub="23 published" index={1} />
        <MetricCard label="Ads" value={31} sub="$125/day budget" index={2} />
        <MetricCard label="Subscribers" value="2.4k" sub="312 this month" index={3} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recent Campaigns */}
        <div className="lg:col-span-7 animate-fade-up" style={{ animationDelay: '200ms' }}>
          <div className="flex items-center justify-between mb-5">
            <h3 className="text-xl font-bold tracking-tight">Active Campaigns</h3>
            <Link href="/dashboard/campaigns" className="text-sm text-amber-400/60 hover:text-amber-400 font-semibold transition-colors">
              View all &rarr;
            </Link>
          </div>
          <div className="space-y-2.5">
            {DEMO_CAMPAIGNS.map((c, i) => (
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
        </div>

        {/* Right column */}
        <div className="lg:col-span-5 space-y-6">
          {/* Pending Approvals */}
          <div className="animate-fade-up" style={{ animationDelay: '400ms' }}>
            <h3 className="text-xl font-bold tracking-tight mb-5">Pending Approval</h3>
            <div className="space-y-2.5">
              {DEMO_CONTENT.map((item) => (
                <div key={item.id} className="glass-card rounded-2xl p-5">
                  <div className="flex items-center justify-between mb-3">
                    <PlatformIcon platform={item.platform} />
                    <StatusBadge status={item.status} />
                  </div>
                  <h4 className="text-base font-semibold mb-1.5 tracking-tight">{item.title}</h4>
                  <p className="text-sm text-white/25 line-clamp-2 leading-relaxed mb-4">{item.body}</p>
                  <div className="flex gap-2">
                    <button className="text-sm px-5 py-2 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 font-semibold transition-colors">
                      Approve
                    </button>
                    <button className="text-sm px-5 py-2 rounded-lg bg-white/[0.03] hover:bg-white/[0.06] text-white/30 font-semibold transition-colors">
                      Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Activity Feed */}
          <div className="animate-fade-up" style={{ animationDelay: '500ms' }}>
            <h3 className="text-xl font-bold tracking-tight mb-5">Recent Activity</h3>
            <div className="glass-card rounded-2xl p-6">
              <div className="space-y-5">
                {DEMO_ACTIVITY.map((a, i) => (
                  <div key={i} className="flex items-center gap-4">
                    <div className={`w-2.5 h-2.5 rounded-full ${a.color} shadow-[0_0_6px_currentColor] flex-shrink-0`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-[15px] font-medium">
                        <span className="text-white/40">{a.action}</span>{" "}
                        <span className="text-white/70">{a.item}</span>
                      </p>
                    </div>
                    <span className="text-sm text-white/20 font-medium flex-shrink-0">{a.time}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

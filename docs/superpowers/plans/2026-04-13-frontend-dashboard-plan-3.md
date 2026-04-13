# Frontend Dashboard Plan 3: Content, Ads, Analytics, Calendar & Settings Pages

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the remaining dashboard pages: Content list, Ads list, Analytics with charts, Calendar view, and Settings.

**Architecture:** Each page follows the same pattern established in Plans 1-2: Next.js page component, `useApi` hook for fetching, typed API client, shared components. Analytics uses Recharts for charts. Calendar is a simple CSS grid.

**Tech Stack:** Next.js 14, React 18, TypeScript, Tailwind CSS, Recharts, date-fns

**Prerequisite:** Plans 1 and 2 must be complete.

---

### Task 1: Content list page

**Files:**
- Create: `frontend/src/app/dashboard/content/page.tsx`

- [ ] **Step 1: Build the content list page**

Create `frontend/src/app/dashboard/content/page.tsx`:

```tsx
"use client";

import { useState } from "react";
import { useApi, useMutation } from "@/hooks/use-api";
import { getContent, approveContent, rejectContent } from "@/lib/api/content";
import { StatusBadge } from "@/components/status-badge";
import { PlatformIcon } from "@/components/platform-icon";
import { EmptyState } from "@/components/empty-state";
import Link from "next/link";
import type { ContentListResponse, ContentPlatform, ContentStatus } from "@/types/api";

const SITE_ID = "default";

const PLATFORMS: ContentPlatform[] = [
  "twitter", "linkedin", "reddit", "blog", "medium",
  "quora", "telegram", "youtube", "hackernews", "producthunt", "email",
];

export default function ContentPage() {
  const [platformFilter, setPlatformFilter] = useState<ContentPlatform | "">("");
  const [statusFilter, setStatusFilter] = useState<ContentStatus | "">("");

  const { data, loading, refetch } = useApi<ContentListResponse>(
    (token) =>
      getContent(token, {
        site_id: SITE_ID,
        platform: platformFilter || undefined,
        status: statusFilter || undefined,
        limit: 50,
      }),
    [platformFilter, statusFilter],
  );

  const approveMut = useMutation((token: string, id: string) => approveContent(token, id));
  const rejectMut = useMutation((token: string, id: string) => rejectContent(token, id));

  const handleApprove = async (id: string) => {
    await approveMut.execute(id);
    refetch();
  };

  const handleReject = async (id: string) => {
    await rejectMut.execute(id);
    refetch();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold">Content</h2>
        <Link
          href="/dashboard/campaigns/new"
          className="text-sm px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium transition"
        >
          Generate Content
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-4">
        <select
          value={platformFilter}
          onChange={(e) => setPlatformFilter(e.target.value as ContentPlatform | "")}
          className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-sm text-gray-300"
        >
          <option value="">All Platforms</option>
          {PLATFORMS.map((p) => (
            <option key={p} value={p} className="capitalize">
              {p}
            </option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as ContentStatus | "")}
          className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-sm text-gray-300"
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="approved">Approved</option>
          <option value="scheduled">Scheduled</option>
          <option value="published">Published</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      {loading ? (
        <p className="text-gray-500 text-sm">Loading content...</p>
      ) : !data?.items.length ? (
        <EmptyState
          title="No content found"
          description="Generate content through a campaign or directly."
        />
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-left text-gray-400">
                <th className="px-4 py-3 font-medium">Title</th>
                <th className="px-4 py-3 font-medium">Platform</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Created</th>
                <th className="px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((item) => (
                <tr key={item.id} className="border-b border-gray-800 last:border-0 hover:bg-gray-800/50">
                  <td className="px-4 py-3">
                    <span className="font-medium">{item.title}</span>
                    <p className="text-xs text-gray-500 line-clamp-1 mt-0.5">{item.body}</p>
                  </td>
                  <td className="px-4 py-3">
                    <PlatformIcon platform={item.platform} />
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={item.status} />
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {new Date(item.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    {item.status === "draft" && (
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleApprove(item.id)}
                          className="text-xs px-2 py-1 rounded bg-green-900 hover:bg-green-800 text-green-300 transition"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => handleReject(item.id)}
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
```

- [ ] **Step 2: Verify build**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/dashboard/content/
git commit -m "feat(frontend): add content list page with filters and approve/reject"
```

---

### Task 2: Ads list page

**Files:**
- Create: `frontend/src/app/dashboard/ads/page.tsx`

- [ ] **Step 1: Build the ads list page**

Create `frontend/src/app/dashboard/ads/page.tsx`:

```tsx
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
```

- [ ] **Step 2: Verify build**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/dashboard/ads/
git commit -m "feat(frontend): add ads list page with status filter and actions"
```

---

### Task 3: Analytics page with charts

**Files:**
- Create: `frontend/src/app/dashboard/analytics/page.tsx`

- [ ] **Step 1: Build the analytics page**

Create `frontend/src/app/dashboard/analytics/page.tsx`:

```tsx
"use client";

import { useState, useMemo } from "react";
import { useApi } from "@/hooks/use-api";
import {
  getOverview,
  getContentAnalytics,
  getAdsAnalytics,
  getEmailAnalytics,
  getTimeseries,
} from "@/lib/api/analytics";
import { MetricCard } from "@/components/metric-card";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { format, subDays } from "date-fns";
import type {
  SiteOverviewResponse,
  ContentAnalyticsResponse,
  AdsAnalyticsResponse,
  EmailAnalyticsResponse,
  TimeseriesResponse,
} from "@/types/api";

const SITE_ID = "default";

export default function AnalyticsPage() {
  const [days, setDays] = useState(30);

  const dateRange = useMemo(() => {
    const end = new Date();
    const start = subDays(end, days);
    return { start: start.toISOString(), end: end.toISOString() };
  }, [days]);

  const { data: overview } = useApi<SiteOverviewResponse>(
    (token) => getOverview(token, SITE_ID),
  );

  const { data: contentStats } = useApi<ContentAnalyticsResponse>(
    (token) => getContentAnalytics(token, SITE_ID),
  );

  const { data: adsStats } = useApi<AdsAnalyticsResponse>(
    (token) => getAdsAnalytics(token, SITE_ID),
  );

  const { data: emailStats } = useApi<EmailAnalyticsResponse>(
    (token) => getEmailAnalytics(token, SITE_ID),
  );

  const { data: timeseries } = useApi<TimeseriesResponse>(
    (token) => getTimeseries(token, SITE_ID, "content_published", dateRange.start, dateRange.end),
    [days],
  );

  const chartData = useMemo(() => {
    if (!timeseries?.points.length) return [];
    return timeseries.points.map((p) => ({
      date: format(new Date(p.recorded_at), "MMM d"),
      value: p.value,
    }));
  }, [timeseries]);

  const platformData = useMemo(() => {
    if (!overview?.content_by_platform.length) return [];
    return overview.content_by_platform.map((p) => ({
      platform: p.platform,
      count: p.count,
    }));
  }, [overview]);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold">Analytics</h2>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-sm text-gray-300"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* Overview metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <MetricCard
          label="Total Content"
          value={contentStats?.total ?? 0}
          sub={`${contentStats?.published_count ?? 0} published`}
        />
        <MetricCard
          label="Campaigns"
          value={adsStats?.total_campaigns ?? 0}
          sub={`${adsStats?.total_ads ?? 0} ads`}
        />
        <MetricCard
          label="Daily Ad Budget"
          value={adsStats ? `$${(adsStats.total_budget_cents_daily / 100).toFixed(2)}` : "$0"}
        />
        <MetricCard
          label="Email Open Rate"
          value={emailStats ? `${(emailStats.open_rate * 100).toFixed(1)}%` : "0%"}
          sub={emailStats ? `${emailStats.total_sent} sent` : undefined}
        />
      </div>

      {/* Timeseries chart */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 mb-6">
        <h3 className="text-sm font-medium text-gray-400 mb-4">Content Published Over Time</h3>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" tick={{ fill: "#9CA3AF", fontSize: 12 }} />
              <YAxis tick={{ fill: "#9CA3AF", fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1F2937",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                  color: "#F9FAFB",
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#3B82F6"
                strokeWidth={2}
                dot={{ fill: "#3B82F6", r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-gray-500 text-sm text-center py-8">No data for this period.</p>
        )}
      </div>

      {/* Platform breakdown */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 mb-6">
        <h3 className="text-sm font-medium text-gray-400 mb-4">Content by Platform</h3>
        {platformData.length > 0 ? (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={platformData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="platform" tick={{ fill: "#9CA3AF", fontSize: 11 }} />
              <YAxis tick={{ fill: "#9CA3AF", fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1F2937",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                  color: "#F9FAFB",
                }}
              />
              <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-gray-500 text-sm text-center py-8">No platform data yet.</p>
        )}
      </div>

      {/* Email stats */}
      {emailStats && emailStats.total_campaigns > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Email Performance</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard label="Campaigns" value={emailStats.total_campaigns} />
            <MetricCard label="Total Sent" value={emailStats.total_sent} />
            <MetricCard
              label="Click Rate"
              value={`${(emailStats.click_rate * 100).toFixed(1)}%`}
            />
            <MetricCard
              label="Subscribers"
              value={emailStats.active_subscribers}
              sub={`${emailStats.total_subscribers} total`}
            />
          </div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verify build**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/dashboard/analytics/
git commit -m "feat(frontend): add analytics page with timeseries and platform charts"
```

---

### Task 4: Calendar page

**Files:**
- Create: `frontend/src/app/dashboard/calendar/page.tsx`

- [ ] **Step 1: Build the calendar page**

Create `frontend/src/app/dashboard/calendar/page.tsx`:

```tsx
"use client";

import { useState, useMemo } from "react";
import { useApi } from "@/hooks/use-api";
import { getCalendar } from "@/lib/api/content";
import { StatusBadge } from "@/components/status-badge";
import { PlatformIcon } from "@/components/platform-icon";
import {
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  format,
  isSameMonth,
  isSameDay,
  addMonths,
  subMonths,
} from "date-fns";
import type { ContentCalendarResponse, ContentResponse } from "@/types/api";

const SITE_ID = "default";

export default function CalendarPage() {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);

  const { data } = useApi<ContentCalendarResponse>(
    (token) =>
      getCalendar(token, SITE_ID, monthStart.toISOString(), monthEnd.toISOString()),
    [currentMonth.getMonth(), currentMonth.getFullYear()],
  );

  const calendarDays = useMemo(() => {
    const start = startOfWeek(monthStart);
    const end = endOfWeek(monthEnd);
    return eachDayOfInterval({ start, end });
  }, [currentMonth]);

  const getItemsForDay = (day: Date): ContentResponse[] => {
    if (!data?.items) return [];
    return data.items.filter((item) => {
      const date = item.scheduled_at || item.published_at;
      if (!date) return false;
      return isSameDay(new Date(date), day);
    });
  };

  const selectedItems = selectedDate ? getItemsForDay(selectedDate) : [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold">Calendar</h2>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
            className="px-3 py-1 rounded bg-gray-900 border border-gray-800 text-gray-300 hover:bg-gray-800 transition text-sm"
          >
            Prev
          </button>
          <span className="text-sm font-medium min-w-[140px] text-center">
            {format(currentMonth, "MMMM yyyy")}
          </span>
          <button
            onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
            className="px-3 py-1 rounded bg-gray-900 border border-gray-800 text-gray-300 hover:bg-gray-800 transition text-sm"
          >
            Next
          </button>
        </div>
      </div>

      {/* Day headers */}
      <div className="grid grid-cols-7 gap-px mb-px">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
          <div key={day} className="text-center text-xs text-gray-500 py-2 font-medium">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-px bg-gray-800 border border-gray-800 rounded-lg overflow-hidden">
        {calendarDays.map((day) => {
          const items = getItemsForDay(day);
          const isCurrentMonth = isSameMonth(day, currentMonth);
          const isSelected = selectedDate && isSameDay(day, selectedDate);

          return (
            <button
              key={day.toISOString()}
              onClick={() => setSelectedDate(day)}
              className={`min-h-[80px] p-2 text-left transition ${
                isSelected
                  ? "bg-blue-900/30"
                  : isCurrentMonth
                    ? "bg-gray-900 hover:bg-gray-800/70"
                    : "bg-gray-950"
              }`}
            >
              <span
                className={`text-xs ${
                  isCurrentMonth ? "text-gray-300" : "text-gray-600"
                }`}
              >
                {format(day, "d")}
              </span>
              {items.length > 0 && (
                <div className="mt-1 space-y-0.5">
                  {items.slice(0, 3).map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center gap-1"
                    >
                      <div
                        className={`w-1.5 h-1.5 rounded-full ${
                          item.status === "published"
                            ? "bg-blue-400"
                            : item.status === "scheduled"
                              ? "bg-amber-400"
                              : "bg-gray-500"
                        }`}
                      />
                      <span className="text-[10px] text-gray-400 truncate">{item.title}</span>
                    </div>
                  ))}
                  {items.length > 3 && (
                    <span className="text-[10px] text-gray-500">+{items.length - 3} more</span>
                  )}
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Selected day detail */}
      {selectedDate && (
        <div className="mt-6">
          <h3 className="text-lg font-medium mb-3">
            {format(selectedDate, "EEEE, MMMM d, yyyy")}
          </h3>
          {selectedItems.length === 0 ? (
            <p className="text-sm text-gray-500">Nothing scheduled for this day.</p>
          ) : (
            <div className="space-y-2">
              {selectedItems.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center gap-3 p-3 bg-gray-900 border border-gray-800 rounded-lg"
                >
                  <PlatformIcon platform={item.platform} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{item.title}</p>
                    <p className="text-xs text-gray-500 truncate">{item.body}</p>
                  </div>
                  <StatusBadge status={item.status} />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verify build**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/dashboard/calendar/
git commit -m "feat(frontend): add calendar page with monthly grid view"
```

---

### Task 5: Settings page

**Files:**
- Create: `frontend/src/app/dashboard/settings/page.tsx`

- [ ] **Step 1: Build the settings page**

Create `frontend/src/app/dashboard/settings/page.tsx`:

```tsx
"use client";

import { useState } from "react";

export default function SettingsPage() {
  const [siteUrl, setSiteUrl] = useState("https://cautilyacapital.com");
  const [llmProvider, setLlmProvider] = useState("openai");
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    // Settings will be persisted via backend API in a future update
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="max-w-2xl">
      <h2 className="text-2xl font-semibold mb-6">Settings</h2>

      <div className="space-y-6">
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <h3 className="text-sm font-medium mb-3">Site Configuration</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Primary Site URL</label>
              <input
                type="url"
                value={siteUrl}
                onChange={(e) => setSiteUrl(e.target.value)}
                className="w-full bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm"
              />
            </div>
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <h3 className="text-sm font-medium mb-3">AI Provider</h3>
          <div>
            <label className="block text-xs text-gray-400 mb-1">LLM Provider</label>
            <select
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value)}
              className="bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm"
            >
              <option value="openai">OpenAI (GPT-4)</option>
              <option value="claude">Anthropic (Claude)</option>
              <option value="together">Together AI</option>
              <option value="ollama">Ollama (Local)</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleSave}
          className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition"
        >
          {saved ? "Saved!" : "Save Settings"}
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify build**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/dashboard/settings/
git commit -m "feat(frontend): add settings page with site and LLM provider config"
```

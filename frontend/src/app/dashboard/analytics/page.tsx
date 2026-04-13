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

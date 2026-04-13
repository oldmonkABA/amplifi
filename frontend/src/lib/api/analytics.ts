import { apiAuthFetch } from "@/lib/api";
import type {
  SiteOverviewResponse,
  ContentAnalyticsResponse,
  AdsAnalyticsResponse,
  EmailAnalyticsResponse,
  TimeseriesResponse,
} from "@/types/api";

export async function getOverview(token: string, siteId: string): Promise<SiteOverviewResponse> {
  return apiAuthFetch(`/api/analytics/overview?site_id=${siteId}`, token);
}

export async function getContentAnalytics(token: string, siteId: string): Promise<ContentAnalyticsResponse> {
  return apiAuthFetch(`/api/analytics/content?site_id=${siteId}`, token);
}

export async function getAdsAnalytics(token: string, siteId: string): Promise<AdsAnalyticsResponse> {
  return apiAuthFetch(`/api/analytics/ads?site_id=${siteId}`, token);
}

export async function getEmailAnalytics(token: string, siteId: string): Promise<EmailAnalyticsResponse> {
  return apiAuthFetch(`/api/analytics/email?site_id=${siteId}`, token);
}

export async function getTimeseries(
  token: string,
  siteId: string,
  metricType: string,
  start: string,
  end: string,
): Promise<TimeseriesResponse> {
  const params = new URLSearchParams({ site_id: siteId, metric_type: metricType, start, end });
  return apiAuthFetch(`/api/analytics/timeseries?${params}`, token);
}

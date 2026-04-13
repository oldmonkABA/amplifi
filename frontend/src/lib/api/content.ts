import { apiAuthFetch } from "@/lib/api";
import type {
  ContentCreateRequest,
  ContentUpdateRequest,
  ContentResponse,
  ContentListResponse,
  ContentGenerateRequest,
  ContentScheduleRequest,
  ContentCalendarResponse,
  ContentFilters,
} from "@/types/api";

export async function getContent(token: string, filters: ContentFilters): Promise<ContentListResponse> {
  const params = new URLSearchParams({ site_id: filters.site_id });
  if (filters.platform) params.set("platform", filters.platform);
  if (filters.status) params.set("status", filters.status);
  if (filters.limit) params.set("limit", String(filters.limit));
  if (filters.offset) params.set("offset", String(filters.offset));
  return apiAuthFetch(`/api/content/?${params}`, token);
}

export async function getContentItem(token: string, contentId: string): Promise<ContentResponse> {
  return apiAuthFetch(`/api/content/${contentId}`, token);
}

export async function createContent(token: string, data: ContentCreateRequest): Promise<ContentResponse> {
  return apiAuthFetch("/api/content/", token, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateContent(token: string, contentId: string, data: ContentUpdateRequest): Promise<ContentResponse> {
  return apiAuthFetch(`/api/content/${contentId}`, token, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteContent(token: string, contentId: string): Promise<void> {
  await apiAuthFetch(`/api/content/${contentId}`, token, { method: "DELETE" });
}

export async function generateContent(token: string, data: ContentGenerateRequest): Promise<ContentResponse> {
  return apiAuthFetch("/api/content/generate", token, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function approveContent(token: string, contentId: string): Promise<ContentResponse> {
  return apiAuthFetch(`/api/content/${contentId}/approve`, token, { method: "POST" });
}

export async function rejectContent(token: string, contentId: string): Promise<ContentResponse> {
  return apiAuthFetch(`/api/content/${contentId}/reject`, token, { method: "POST" });
}

export async function scheduleContent(token: string, contentId: string, data: ContentScheduleRequest): Promise<ContentResponse> {
  return apiAuthFetch(`/api/content/${contentId}/schedule`, token, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getCalendar(token: string, siteId: string, start: string, end: string): Promise<ContentCalendarResponse> {
  const params = new URLSearchParams({ site_id: siteId, start, end });
  return apiAuthFetch(`/api/content/calendar?${params}`, token);
}

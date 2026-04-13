import { apiAuthFetch } from "@/lib/api";
import type {
  AdCreateRequest,
  AdUpdateRequest,
  AdResponse,
  AdListResponse,
  AdGenerateRequest,
  AdGenerateResponse,
  AdFilters,
} from "@/types/api";

export async function getAds(token: string, filters: AdFilters): Promise<AdListResponse> {
  const params = new URLSearchParams();
  if (filters.campaign_id) params.set("campaign_id", filters.campaign_id);
  if (filters.status) params.set("status", filters.status);
  if (filters.limit) params.set("limit", String(filters.limit));
  if (filters.offset) params.set("offset", String(filters.offset));
  return apiAuthFetch(`/api/ads/ads/?${params}`, token);
}

export async function getAd(token: string, adId: string): Promise<AdResponse> {
  return apiAuthFetch(`/api/ads/ads/${adId}`, token);
}

export async function createAd(token: string, data: AdCreateRequest): Promise<AdResponse> {
  return apiAuthFetch("/api/ads/ads/", token, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateAd(token: string, adId: string, data: AdUpdateRequest): Promise<AdResponse> {
  return apiAuthFetch(`/api/ads/ads/${adId}`, token, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteAd(token: string, adId: string): Promise<void> {
  await apiAuthFetch(`/api/ads/ads/${adId}`, token, { method: "DELETE" });
}

export async function generateAds(token: string, data: AdGenerateRequest): Promise<AdGenerateResponse> {
  return apiAuthFetch("/api/ads/generate", token, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

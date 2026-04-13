import { apiAuthFetch } from "@/lib/api";
import type {
  CampaignCreateRequest,
  CampaignUpdateRequest,
  CampaignResponse,
  CampaignListResponse,
  CampaignFilters,
} from "@/types/api";

export async function getCampaigns(token: string, filters: CampaignFilters): Promise<CampaignListResponse> {
  const params = new URLSearchParams({ site_id: filters.site_id });
  if (filters.platform) params.set("platform", filters.platform);
  if (filters.status) params.set("status", filters.status);
  if (filters.limit) params.set("limit", String(filters.limit));
  if (filters.offset) params.set("offset", String(filters.offset));
  return apiAuthFetch(`/api/ads/campaigns/?${params}`, token);
}

export async function getCampaign(token: string, campaignId: string): Promise<CampaignResponse> {
  return apiAuthFetch(`/api/ads/campaigns/${campaignId}`, token);
}

export async function createCampaign(token: string, data: CampaignCreateRequest): Promise<CampaignResponse> {
  return apiAuthFetch("/api/ads/campaigns/", token, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateCampaign(token: string, campaignId: string, data: CampaignUpdateRequest): Promise<CampaignResponse> {
  return apiAuthFetch(`/api/ads/campaigns/${campaignId}`, token, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteCampaign(token: string, campaignId: string): Promise<void> {
  await apiAuthFetch(`/api/ads/campaigns/${campaignId}`, token, {
    method: "DELETE",
  });
}

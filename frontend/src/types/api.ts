// Auth
export interface UserResponse {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
  default_llm_provider: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// Content
export type ContentPlatform =
  | "twitter" | "linkedin" | "reddit" | "blog" | "medium"
  | "quora" | "telegram" | "youtube" | "hackernews" | "producthunt" | "email";

export type ContentStatus = "draft" | "approved" | "scheduled" | "published" | "rejected";

export interface ContentCreateRequest {
  site_id: string;
  platform: ContentPlatform;
  content_type: string;
  title: string;
  body: string;
  status?: ContentStatus;
  group_id?: string;
  scheduled_at?: string;
  target_timezone?: string;
  meta_data?: Record<string, unknown>;
}

export interface ContentUpdateRequest {
  title?: string;
  body?: string;
  status?: ContentStatus;
  scheduled_at?: string;
  target_timezone?: string;
  meta_data?: Record<string, unknown>;
}

export interface ContentResponse {
  id: string;
  site_id: string;
  user_id: string;
  platform: ContentPlatform;
  content_type: string;
  title: string;
  body: string;
  status: ContentStatus;
  group_id: string | null;
  scheduled_at: string | null;
  published_at: string | null;
  target_timezone: string | null;
  platform_post_id: string | null;
  meta_data: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface ContentListResponse {
  items: ContentResponse[];
  total: number;
}

export interface ContentGenerateRequest {
  site_id: string;
  platform: ContentPlatform;
  content_type: string;
  topic: string;
  tone?: string;
  keywords?: string[];
  additional_context?: string;
}

export interface ContentScheduleRequest {
  scheduled_at: string;
  target_timezone?: string;
}

export interface ContentCalendarResponse {
  items: ContentResponse[];
}

export interface ContentGroupCreateRequest {
  site_id: string;
  name: string;
  description?: string;
}

export interface ContentGroupResponse {
  id: string;
  site_id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

// Ads
export type AdPlatform = "google_ads" | "facebook_ads";
export type CampaignStatus = "draft" | "active" | "paused" | "completed";
export type CampaignObjective = "traffic" | "conversions" | "awareness" | "leads";
export type AdStatus = "draft" | "active" | "paused" | "rejected";

export interface CampaignCreateRequest {
  site_id: string;
  name: string;
  platform: AdPlatform;
  objective: CampaignObjective;
  daily_budget_cents: number;
  status?: CampaignStatus;
  targeting?: Record<string, unknown>;
  meta_data?: Record<string, unknown>;
}

export interface CampaignUpdateRequest {
  name?: string;
  platform?: AdPlatform;
  objective?: CampaignObjective;
  daily_budget_cents?: number;
  status?: CampaignStatus;
  targeting?: Record<string, unknown>;
  meta_data?: Record<string, unknown>;
}

export interface CampaignResponse {
  id: string;
  site_id: string;
  user_id: string;
  name: string;
  platform: AdPlatform;
  objective: CampaignObjective;
  daily_budget_cents: number;
  status: CampaignStatus;
  targeting: Record<string, unknown> | null;
  meta_data: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface CampaignListResponse {
  items: CampaignResponse[];
  total: number;
}

export interface AdCreateRequest {
  campaign_id: string;
  headline: string;
  headline_2?: string;
  headline_3?: string;
  description: string;
  description_2?: string;
  display_url?: string;
  final_url: string;
  image_url?: string;
  status?: AdStatus;
  meta_data?: Record<string, unknown>;
}

export interface AdUpdateRequest {
  headline?: string;
  headline_2?: string;
  headline_3?: string;
  description?: string;
  description_2?: string;
  display_url?: string;
  final_url?: string;
  image_url?: string;
  status?: AdStatus;
  meta_data?: Record<string, unknown>;
}

export interface AdResponse {
  id: string;
  campaign_id: string;
  headline: string;
  headline_2: string | null;
  headline_3: string | null;
  description: string;
  description_2: string | null;
  display_url: string | null;
  final_url: string;
  image_url: string | null;
  status: AdStatus;
  platform_ad_id: string | null;
  meta_data: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface AdListResponse {
  items: AdResponse[];
  total: number;
}

export interface AdGenerateRequest {
  campaign_id: string;
  site_id: string;
  platform: AdPlatform;
  topic: string;
  tone?: string;
  keywords?: string[];
  num_variants?: number;
}

export interface AdGenerateResponse {
  ads: AdResponse[];
}

// Analytics
export interface StatusCount {
  status: string;
  count: number;
}

export interface PlatformCount {
  platform: string;
  count: number;
}

export interface SiteOverviewResponse {
  site_id: string;
  total_content: number;
  content_by_status: StatusCount[];
  content_by_platform: PlatformCount[];
  total_campaigns: number;
  total_ads: number;
  total_subscribers: number;
  active_subscribers: number;
}

export interface ContentAnalyticsResponse {
  site_id: string;
  total: number;
  by_status: StatusCount[];
  by_platform: PlatformCount[];
  published_count: number;
  scheduled_count: number;
  draft_count: number;
}

export interface AdsAnalyticsResponse {
  site_id: string;
  total_campaigns: number;
  campaigns_by_status: StatusCount[];
  campaigns_by_platform: PlatformCount[];
  total_ads: number;
  ads_by_status: StatusCount[];
  total_budget_cents_daily: number;
}

export interface EmailAnalyticsResponse {
  site_id: string;
  total_campaigns: number;
  total_sent: number;
  total_opened: number;
  total_clicked: number;
  open_rate: number;
  click_rate: number;
  total_subscribers: number;
  active_subscribers: number;
}

export interface TimeseriesPoint {
  recorded_at: string;
  value: number;
  dimensions: Record<string, unknown> | null;
}

export interface TimeseriesResponse {
  site_id: string;
  metric_type: string;
  points: TimeseriesPoint[];
}

export interface MetricSnapshotCreateRequest {
  site_id: string;
  metric_type: string;
  value: number;
  dimensions?: Record<string, unknown>;
}

// Filters
export interface ContentFilters {
  site_id: string;
  platform?: ContentPlatform;
  status?: ContentStatus;
  limit?: number;
  offset?: number;
}

export interface CampaignFilters {
  site_id: string;
  platform?: AdPlatform;
  status?: CampaignStatus;
  limit?: number;
  offset?: number;
}

export interface AdFilters {
  campaign_id?: string;
  status?: AdStatus;
  limit?: number;
  offset?: number;
}

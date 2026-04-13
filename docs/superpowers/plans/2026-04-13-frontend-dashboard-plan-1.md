# Frontend Dashboard Plan 1: Foundation + Shared Components

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install dependencies (shadcn/ui, Recharts, date-fns), set up the dashboard layout with proper routing, build all shared components, and create the typed API layer.

**Architecture:** Extend the existing Next.js 14 app with shadcn/ui components (installed via CLI into `src/components/ui/`). Build Amplifi-specific shared components in `src/components/`. Create a typed API client in `src/lib/api/` with one file per domain. Add React hooks in `src/hooks/`.

**Tech Stack:** Next.js 14, React 18, TypeScript, Tailwind CSS, shadcn/ui, Recharts, date-fns

---

### Task 1: Install dependencies and configure shadcn/ui

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/tailwind.config.ts`
- Modify: `frontend/tsconfig.json`
- Create: `frontend/components.json`
- Create: `frontend/src/lib/utils.ts`

- [ ] **Step 1: Install shadcn/ui prerequisites and runtime deps**

```bash
cd frontend
npm install recharts date-fns clsx tailwind-merge class-variance-authority lucide-react
npm install -D @radix-ui/react-slot @radix-ui/react-dialog @radix-ui/react-tabs @radix-ui/react-select @radix-ui/react-dropdown-menu @radix-ui/react-popover
```

- [ ] **Step 2: Create the cn utility**

Create `frontend/src/lib/utils.ts`:

```typescript
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

- [ ] **Step 3: Create components.json for shadcn/ui**

Create `frontend/components.json`:

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "src/app/globals.css",
    "baseColor": "slate",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

- [ ] **Step 4: Update globals.css with CSS variables for dark theme**

Replace the content of `frontend/src/app/globals.css` with:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 3.9%;
    --foreground: 0 0% 98%;
    --card: 0 0% 5.5%;
    --card-foreground: 0 0% 98%;
    --popover: 0 0% 5.5%;
    --popover-foreground: 0 0% 98%;
    --primary: 217 91% 60%;
    --primary-foreground: 0 0% 98%;
    --secondary: 0 0% 14.9%;
    --secondary-foreground: 0 0% 98%;
    --muted: 0 0% 14.9%;
    --muted-foreground: 0 0% 63.9%;
    --accent: 0 0% 14.9%;
    --accent-foreground: 0 0% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 0 0% 98%;
    --border: 0 0% 14.9%;
    --input: 0 0% 14.9%;
    --ring: 217 91% 60%;
    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

- [ ] **Step 5: Update tailwind.config.ts for shadcn/ui**

Replace `frontend/tailwind.config.ts` with:

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
};
export default config;
```

- [ ] **Step 6: Verify the build compiles**

```bash
cd frontend && npx next build
```

Expected: Build succeeds with no errors.

- [ ] **Step 7: Commit**

```bash
git add frontend/
git commit -m "feat(frontend): install shadcn/ui, recharts, date-fns and configure theme"
```

---

### Task 2: TypeScript types mirroring backend schemas

**Files:**
- Create: `frontend/src/types/api.ts`

- [ ] **Step 1: Create the types file**

Create `frontend/src/types/api.ts` with all types matching the backend Pydantic schemas:

```typescript
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
```

- [ ] **Step 2: Verify build**

```bash
cd frontend && npx tsc --noEmit
```

Expected: No type errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/types/
git commit -m "feat(frontend): add TypeScript types mirroring backend schemas"
```

---

### Task 3: Typed API client functions

**Files:**
- Modify: `frontend/src/lib/api.ts`
- Create: `frontend/src/lib/api/campaigns.ts`
- Create: `frontend/src/lib/api/content.ts`
- Create: `frontend/src/lib/api/ads.ts`
- Create: `frontend/src/lib/api/analytics.ts`
- Create: `frontend/src/lib/api/index.ts`

- [ ] **Step 1: Create campaigns API**

Create `frontend/src/lib/api/campaigns.ts`:

```typescript
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
```

- [ ] **Step 2: Create content API**

Create `frontend/src/lib/api/content.ts`:

```typescript
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
```

- [ ] **Step 3: Create ads API**

Create `frontend/src/lib/api/ads.ts`:

```typescript
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
```

- [ ] **Step 4: Create analytics API**

Create `frontend/src/lib/api/analytics.ts`:

```typescript
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
```

- [ ] **Step 5: Create barrel export**

Create `frontend/src/lib/api/index.ts`:

```typescript
export * from "./campaigns";
export * from "./content";
export * from "./ads";
export * from "./analytics";
```

- [ ] **Step 6: Verify build**

```bash
cd frontend && npx tsc --noEmit
```

Expected: No type errors.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/lib/api/
git commit -m "feat(frontend): add typed API client for campaigns, content, ads, analytics"
```

---

### Task 4: React hooks for data fetching

**Files:**
- Create: `frontend/src/hooks/use-api.ts`

- [ ] **Step 1: Create the hooks file**

Create `frontend/src/hooks/use-api.ts`:

```typescript
"use client";

import { useState, useEffect, useCallback } from "react";
import { useSession } from "next-auth/react";

interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useApi<T>(
  fetcher: (token: string) => Promise<T>,
  deps: unknown[] = [],
): UseApiResult<T> {
  const { data: session } = useSession();
  const token = (session as any)?.id_token as string | undefined;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const refetch = useCallback(() => setRefreshKey((k) => k + 1), []);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    fetcher(token)
      .then((result) => {
        if (!cancelled) {
          setData(result);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [token, refreshKey, ...deps]);

  return { data, loading, error, refetch };
}

export function useMutation<TInput, TOutput>(
  mutator: (token: string, input: TInput) => Promise<TOutput>,
) {
  const { data: session } = useSession();
  const token = (session as any)?.id_token as string | undefined;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(
    async (input: TInput): Promise<TOutput> => {
      if (!token) throw new Error("Not authenticated");
      setLoading(true);
      setError(null);
      try {
        const result = await mutator(token, input);
        return result;
      } catch (err: any) {
        setError(err.message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [token, mutator],
  );

  return { execute, loading, error };
}
```

- [ ] **Step 2: Verify build**

```bash
cd frontend && npx tsc --noEmit
```

Expected: No type errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/hooks/
git commit -m "feat(frontend): add useApi and useMutation hooks for data fetching"
```

---

### Task 5: Shared UI components — StatusBadge, MetricCard, PlatformIcon, EmptyState

**Files:**
- Create: `frontend/src/components/status-badge.tsx`
- Create: `frontend/src/components/metric-card.tsx`
- Create: `frontend/src/components/platform-icon.tsx`
- Create: `frontend/src/components/empty-state.tsx`

- [ ] **Step 1: Create StatusBadge**

Create `frontend/src/components/status-badge.tsx`:

```tsx
import { cn } from "@/lib/utils";

const statusStyles: Record<string, string> = {
  draft: "bg-gray-700 text-gray-300",
  approved: "bg-green-900 text-green-300",
  scheduled: "bg-blue-900 text-blue-300",
  published: "bg-blue-700 text-blue-100",
  rejected: "bg-red-900 text-red-300",
  active: "bg-green-900 text-green-300",
  paused: "bg-amber-900 text-amber-300",
  completed: "bg-gray-700 text-gray-300",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize",
        statusStyles[status] ?? "bg-gray-700 text-gray-300",
      )}
    >
      {status}
    </span>
  );
}
```

- [ ] **Step 2: Create MetricCard**

Create `frontend/src/components/metric-card.tsx`:

```tsx
export function MetricCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string | number;
  sub?: string;
}) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
      <p className="text-sm text-gray-400">{label}</p>
      <p className="text-2xl font-semibold mt-1">{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  );
}
```

- [ ] **Step 3: Create PlatformIcon**

Create `frontend/src/components/platform-icon.tsx`:

```tsx
const platformLabels: Record<string, string> = {
  twitter: "TW",
  linkedin: "LI",
  reddit: "RD",
  blog: "BG",
  medium: "MD",
  quora: "QA",
  telegram: "TG",
  youtube: "YT",
  hackernews: "HN",
  producthunt: "PH",
  email: "EM",
  google_ads: "GA",
  facebook_ads: "FB",
};

const platformColors: Record<string, string> = {
  twitter: "bg-sky-800",
  linkedin: "bg-blue-800",
  reddit: "bg-orange-800",
  blog: "bg-purple-800",
  medium: "bg-gray-700",
  quora: "bg-red-800",
  telegram: "bg-sky-700",
  youtube: "bg-red-700",
  hackernews: "bg-orange-700",
  producthunt: "bg-orange-600",
  email: "bg-emerald-800",
  google_ads: "bg-green-800",
  facebook_ads: "bg-blue-700",
};

export function PlatformIcon({ platform }: { platform: string }) {
  return (
    <span
      className={`inline-flex items-center justify-center w-7 h-7 rounded text-[10px] font-bold ${platformColors[platform] ?? "bg-gray-700"}`}
      title={platform}
    >
      {platformLabels[platform] ?? platform.slice(0, 2).toUpperCase()}
    </span>
  );
}
```

- [ ] **Step 4: Create EmptyState**

Create `frontend/src/components/empty-state.tsx`:

```tsx
export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-12 h-12 rounded-full bg-gray-800 flex items-center justify-center mb-4">
        <span className="text-gray-500 text-xl">+</span>
      </div>
      <h3 className="text-lg font-medium mb-1">{title}</h3>
      <p className="text-sm text-gray-400 mb-4 max-w-md">{description}</p>
      {action}
    </div>
  );
}
```

- [ ] **Step 5: Verify build**

```bash
cd frontend && npx tsc --noEmit
```

Expected: No type errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/
git commit -m "feat(frontend): add StatusBadge, MetricCard, PlatformIcon, EmptyState components"
```

---

### Task 6: ContentCard and AdCard components

**Files:**
- Create: `frontend/src/components/content-card.tsx`
- Create: `frontend/src/components/ad-card.tsx`

- [ ] **Step 1: Create ContentCard**

Create `frontend/src/components/content-card.tsx`:

```tsx
"use client";

import type { ContentResponse } from "@/types/api";
import { StatusBadge } from "@/components/status-badge";
import { PlatformIcon } from "@/components/platform-icon";

export function ContentCard({
  content,
  onApprove,
  onReject,
}: {
  content: ContentResponse;
  onApprove?: (id: string) => void;
  onReject?: (id: string) => void;
}) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <PlatformIcon platform={content.platform} />
        <StatusBadge status={content.status} />
      </div>
      <h4 className="font-medium mb-1 line-clamp-1">{content.title}</h4>
      <p className="text-sm text-gray-400 line-clamp-2 mb-3">{content.body}</p>
      {content.status === "draft" && (onApprove || onReject) && (
        <div className="flex gap-2">
          {onApprove && (
            <button
              onClick={() => onApprove(content.id)}
              className="text-xs px-3 py-1 rounded bg-green-800 hover:bg-green-700 text-green-200 transition"
            >
              Approve
            </button>
          )}
          {onReject && (
            <button
              onClick={() => onReject(content.id)}
              className="text-xs px-3 py-1 rounded bg-red-900 hover:bg-red-800 text-red-200 transition"
            >
              Reject
            </button>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Create AdCard**

Create `frontend/src/components/ad-card.tsx`:

```tsx
"use client";

import type { AdResponse } from "@/types/api";
import { StatusBadge } from "@/components/status-badge";

export function AdCard({
  ad,
  onApprove,
  onReject,
}: {
  ad: AdResponse;
  onApprove?: (id: string) => void;
  onReject?: (id: string) => void;
}) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <StatusBadge status={ad.status} />
      </div>
      <h4 className="font-medium mb-1 line-clamp-1">{ad.headline}</h4>
      <p className="text-sm text-gray-400 line-clamp-2 mb-1">{ad.description}</p>
      {ad.display_url && (
        <p className="text-xs text-blue-400 mb-3">{ad.display_url}</p>
      )}
      {ad.status === "draft" && (onApprove || onReject) && (
        <div className="flex gap-2">
          {onApprove && (
            <button
              onClick={() => onApprove(ad.id)}
              className="text-xs px-3 py-1 rounded bg-green-800 hover:bg-green-700 text-green-200 transition"
            >
              Approve
            </button>
          )}
          {onReject && (
            <button
              onClick={() => onReject(ad.id)}
              className="text-xs px-3 py-1 rounded bg-red-900 hover:bg-red-800 text-red-200 transition"
            >
              Reject
            </button>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Verify build**

```bash
cd frontend && npx tsc --noEmit
```

Expected: No type errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/content-card.tsx frontend/src/components/ad-card.tsx
git commit -m "feat(frontend): add ContentCard and AdCard components"
```

---

### Task 7: Update layout — Dashboard layout wrapper, updated sidebar, header with CTA

**Files:**
- Create: `frontend/src/app/dashboard/layout.tsx`
- Modify: `frontend/src/components/sidebar.tsx`
- Modify: `frontend/src/components/header.tsx`
- Modify: `frontend/src/app/dashboard/page.tsx` (remove layout duplication)

- [ ] **Step 1: Create dashboard layout**

Create `frontend/src/app/dashboard/layout.tsx`:

```tsx
import { Sidebar } from "@/components/sidebar";
import { Header } from "@/components/header";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Update sidebar with Campaigns link and active state**

Replace `frontend/src/components/sidebar.tsx`:

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navItems = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Campaigns", href: "/dashboard/campaigns" },
  { label: "Content", href: "/dashboard/content" },
  { label: "Ads", href: "/dashboard/ads" },
  { label: "Analytics", href: "/dashboard/analytics" },
  { label: "Calendar", href: "/dashboard/calendar" },
  { label: "Settings", href: "/dashboard/settings" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800 p-4 flex flex-col">
      <div className="text-xl font-bold mb-8 px-2">Amplifi</div>
      <nav className="space-y-1 flex-1">
        {navItems.map((item) => {
          const isActive =
            item.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "block px-3 py-2 rounded-lg transition text-sm",
                isActive
                  ? "bg-gray-800 text-white font-medium"
                  : "text-gray-400 hover:bg-gray-800 hover:text-white",
              )}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
```

- [ ] **Step 3: Update header with New Campaign button**

Replace `frontend/src/components/header.tsx`:

```tsx
"use client";

import Link from "next/link";
import { signOut, useSession } from "next-auth/react";

export function Header() {
  const { data: session } = useSession();

  return (
    <header className="h-14 border-b border-gray-800 flex items-center justify-between px-6">
      <Link
        href="/dashboard/campaigns/new"
        className="text-sm px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium transition"
      >
        New Campaign
      </Link>
      <div className="flex items-center gap-4">
        {session?.user?.name && (
          <span className="text-sm text-gray-400">{session.user.name}</span>
        )}
        <button
          onClick={() => signOut({ callbackUrl: "/" })}
          className="text-sm text-gray-400 hover:text-white transition"
        >
          Sign out
        </button>
      </div>
    </header>
  );
}
```

- [ ] **Step 4: Simplify dashboard page (layout is now in layout.tsx)**

Replace `frontend/src/app/dashboard/page.tsx` with just the content (layout wrapper removed):

```tsx
export default function DashboardPage() {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Dashboard</h2>
      <p className="text-gray-400">Welcome to Amplifi. Your marketing command center.</p>
    </div>
  );
}
```

- [ ] **Step 5: Verify build**

```bash
cd frontend && npx tsc --noEmit
```

Expected: No type errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/app/dashboard/ frontend/src/components/sidebar.tsx frontend/src/components/header.tsx
git commit -m "feat(frontend): add dashboard layout, updated sidebar with active state, header with campaign CTA"
```

---

### Task 8: Add NextAuth SessionProvider to root layout

**Files:**
- Create: `frontend/src/components/providers.tsx`
- Modify: `frontend/src/app/layout.tsx`

- [ ] **Step 1: Create providers wrapper**

Create `frontend/src/components/providers.tsx`:

```tsx
"use client";

import { SessionProvider } from "next-auth/react";

export function Providers({ children }: { children: React.ReactNode }) {
  return <SessionProvider>{children}</SessionProvider>;
}
```

- [ ] **Step 2: Update root layout to wrap with Providers**

Replace `frontend/src/app/layout.tsx`:

```tsx
import type { Metadata } from "next";
import { Providers } from "@/components/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "Amplifi",
  description: "AI-powered marketing automation",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

- [ ] **Step 3: Verify build**

```bash
cd frontend && npx tsc --noEmit
```

Expected: No type errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/providers.tsx frontend/src/app/layout.tsx
git commit -m "feat(frontend): add SessionProvider wrapper to root layout"
```

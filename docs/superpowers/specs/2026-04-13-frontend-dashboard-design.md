# Amplifi Frontend Dashboard — Design Spec

## Overview

Build a campaign-first frontend dashboard for Amplifi. The primary workflow is a guided campaign wizard where the user defines a goal, AI generates content + ads across platforms, the user reviews/approves, and launches. Analytics is prominent throughout. Content/ads management is available as secondary views.

Primary site: Cautilya Capital. Multi-site switching available but not the focus.

## Tech Stack

- Next.js 14 (existing)
- React 18 (existing)
- NextAuth (existing, Google OAuth)
- Tailwind CSS (existing)
- **shadcn/ui** — component library built on Radix + Tailwind
- **Recharts** — charting for analytics
- **date-fns** — date utilities

No additional UI frameworks (no Material UI, Ant Design, etc).

## Page Structure

| Route | Purpose |
|---|---|
| `/dashboard` | Overview: metrics cards, recent campaigns, pending approvals |
| `/dashboard/campaigns` | List all campaigns with status, create new |
| `/dashboard/campaigns/new` | Guided campaign wizard (4 steps) |
| `/dashboard/campaigns/[id]` | Single campaign: content + ads + analytics in tabs |
| `/dashboard/content` | All content across campaigns, filterable by platform/status |
| `/dashboard/ads` | All ads across campaigns, filterable |
| `/dashboard/analytics` | Deep analytics: timeseries charts, platform breakdowns |
| `/dashboard/calendar` | Calendar view of scheduled content |
| `/dashboard/settings` | Site management, LLM provider config |

## Core Workflow: Guided Campaign Wizard

The centerpiece of the app. Steps:

1. **Goal** — User enters topic/description, selects tone, checks target platforms (Twitter, LinkedIn, blog, etc.)
2. **Generate** — Backend generates content (`POST /api/content/generate`) and ad variants (`POST /api/ads/generate`) for each selected platform. Loading state shown.
3. **Review** — Generated pieces displayed as cards in a grid. Each card is editable inline. User can approve, reject, or edit each piece individually. Bulk approve/reject actions available.
4. **Schedule & Launch** — User picks launch date/time or publishes immediately. Only approved items are included. Confirmation screen before final submission.

All wizard state is managed locally (React state). Backend calls happen at step 2 (generation) and step 4 (creating/scheduling the final items).

## Page Details

### Dashboard Overview (`/dashboard`)

- **MetricsGrid**: 4-6 stat cards — total campaigns, active content pieces, total impressions, click-through rate, pending approvals count. Data from `GET /api/analytics/overview`.
- **RecentCampaigns**: Last 5 campaigns with name, status badge, platform icons, date. Links to campaign detail.
- **PendingApprovals**: Draft content/ads needing review. Quick approve/reject buttons inline. Data from `GET /api/content?status=draft` and `GET /api/ads?status=draft`.

### Campaign List (`/dashboard/campaigns`)

- Table/card list of all campaigns
- Columns: name, platform, status, budget, content count, ad count, created date
- Filters: platform, status
- "New Campaign" button prominent at top

### Campaign Detail (`/dashboard/campaigns/[id]`)

- Header: campaign name, status badge, platform, budget, date range
- Three tabs:
  - **Content**: content pieces belonging to this campaign, with approve/reject/edit/schedule actions
  - **Ads**: ad variants for this campaign, same actions
  - **Analytics**: campaign-specific metrics and charts

### Content (`/dashboard/content`)

- DataTable of all content across all campaigns
- Columns: title, platform, status, campaign, scheduled date, created date
- Filters: platform, status, campaign
- Row click opens content detail/edit modal
- "Generate Content" button for standalone generation outside campaigns

### Ads (`/dashboard/ads`)

- DataTable of all ads
- Columns: headline, platform, campaign, status, created date
- Filters: platform, status, campaign
- Row click opens ad detail/edit modal

### Analytics (`/dashboard/analytics`)

- **Date range picker** at top (default: last 30 days)
- **TimeseriesChart** (Recharts line chart) — data from `GET /api/analytics/timeseries`
- **PlatformBreakdown** — bar or pie chart, content/impressions by platform
- **PerformanceTable** — sortable table of top content/ads by metrics
- **Email stats** — open rate, click rate from `GET /api/analytics/email`

### Calendar (`/dashboard/calendar`)

- Monthly calendar grid view
- Shows scheduled and published content as colored dots/pills on dates
- Click a date to see that day's items
- Data from `GET /api/content/calendar?start=...&end=...`

### Settings (`/dashboard/settings`)

- Site selector/manager (add site, set default)
- LLM provider configuration (which provider to use for generation)
- Not a priority — minimal implementation

## Shared Components

| Component | Purpose |
|---|---|
| `StatusBadge` | Colored pill for status (draft=gray, approved=green, scheduled=blue, published=blue-bright, rejected=red) |
| `ContentCard` | Card displaying content piece with title, platform icon, status, preview text, action buttons |
| `AdCard` | Card displaying ad with headlines, descriptions, display URL, status, action buttons |
| `MetricCard` | Stat card with label, value, optional trend indicator |
| `DataTable` | Generic sortable, filterable table with pagination |
| `EmptyState` | Placeholder illustration + message + CTA when no data |
| `DateRangePicker` | Start/end date selector for analytics |
| `PlatformIcon` | Icon for each platform (Twitter, LinkedIn, etc.) |
| `ConfirmDialog` | Confirmation modal for destructive actions |

## API Layer

Extend existing `lib/api.ts` with typed fetch functions:

```typescript
// Campaigns
getCampaigns(siteId, filters?) -> CampaignListResponse
getCampaign(campaignId) -> CampaignResponse
createCampaign(data) -> CampaignResponse
updateCampaign(campaignId, data) -> CampaignResponse
deleteCampaign(campaignId) -> void

// Content
getContent(siteId, filters?) -> ContentListResponse
getContentItem(contentId) -> ContentResponse
createContent(data) -> ContentResponse
updateContent(contentId, data) -> ContentResponse
deleteContent(contentId) -> void
generateContent(data) -> ContentResponse
approveContent(contentId) -> ContentResponse
rejectContent(contentId) -> ContentResponse
scheduleContent(contentId, data) -> ContentResponse
getCalendar(siteId, start, end) -> ContentCalendarResponse

// Ads
getAds(filters?) -> AdListResponse
getAd(adId) -> AdResponse
createAd(data) -> AdResponse
updateAd(adId, data) -> AdResponse
deleteAd(adId) -> void
generateAds(data) -> AdGenerateResponse

// Analytics
getOverview(siteId) -> SiteOverviewResponse
getContentAnalytics(siteId) -> ContentAnalyticsResponse
getAdsAnalytics(siteId) -> AdsAnalyticsResponse
getEmailAnalytics(siteId) -> EmailAnalyticsResponse
getTimeseries(siteId, metricType, start, end) -> TimeseriesResponse

// Auth (existing)
getCurrentUser() -> UserResponse
```

React hooks wrapping these: `useCampaigns()`, `useContent()`, `useAds()`, `useAnalytics()`, etc. Simple fetch + useState/useEffect pattern. No external state management library.

## Styling

- Dark theme: gray-950 background, gray-900 card backgrounds, gray-800 borders
- Accent: blue-500 primary actions, green-500 success/approved, amber-500 pending/warning, red-500 rejected/error
- Typography: system font stack via Tailwind defaults
- Cards: rounded-lg, subtle borders, consistent padding (p-4 / p-6)
- Desktop-first layout, sidebar collapses on smaller screens
- Data-dense, information-forward — no decorative elements

## What This Spec Does NOT Cover

- Real platform API integrations (Twitter, Google Ads, Facebook) — these remain mocked
- User onboarding / first-run experience
- Multi-user / team features
- Billing / SaaS features
- Mobile-optimized layouts (functional but not polished on mobile)

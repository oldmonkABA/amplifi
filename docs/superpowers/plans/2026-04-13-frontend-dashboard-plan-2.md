# Frontend Dashboard Plan 2: Dashboard Overview + Campaign Pages

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the dashboard overview page (metrics, recent campaigns, pending approvals) and the full campaigns flow (list, detail with tabs, and the guided campaign wizard).

**Architecture:** Each page is a Next.js app router page component. Pages use the `useApi` hook from Plan 1 to fetch data and the typed API client functions. The campaign wizard manages state locally across 4 steps.

**Tech Stack:** Next.js 14, React 18, TypeScript, Tailwind CSS, shadcn/ui components from Plan 1

**Prerequisite:** Plan 1 must be complete (shared components, API layer, hooks, layout).

---

### Task 1: Dashboard overview page

**Files:**
- Modify: `frontend/src/app/dashboard/page.tsx`

- [ ] **Step 1: Build the dashboard overview page**

Replace `frontend/src/app/dashboard/page.tsx`:

```tsx
"use client";

import { useApi } from "@/hooks/use-api";
import { getOverview } from "@/lib/api/analytics";
import { getContent } from "@/lib/api/content";
import { getCampaigns } from "@/lib/api/campaigns";
import { MetricCard } from "@/components/metric-card";
import { ContentCard } from "@/components/content-card";
import { StatusBadge } from "@/components/status-badge";
import { EmptyState } from "@/components/empty-state";
import { PlatformIcon } from "@/components/platform-icon";
import Link from "next/link";
import type { SiteOverviewResponse, ContentListResponse, CampaignListResponse } from "@/types/api";

const SITE_ID = "default";

export default function DashboardPage() {
  const { data: overview, loading: overviewLoading } = useApi<SiteOverviewResponse>(
    (token) => getOverview(token, SITE_ID),
  );
  const { data: drafts, loading: draftsLoading, refetch: refetchDrafts } = useApi<ContentListResponse>(
    (token) => getContent(token, { site_id: SITE_ID, status: "draft", limit: 5 }),
  );
  const { data: campaigns, loading: campaignsLoading } = useApi<CampaignListResponse>(
    (token) => getCampaigns(token, { site_id: SITE_ID, limit: 5 }),
  );

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6">Dashboard</h2>

      {/* Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <MetricCard
          label="Total Campaigns"
          value={overviewLoading ? "..." : overview?.total_campaigns ?? 0}
        />
        <MetricCard
          label="Content Pieces"
          value={overviewLoading ? "..." : overview?.total_content ?? 0}
        />
        <MetricCard
          label="Total Ads"
          value={overviewLoading ? "..." : overview?.total_ads ?? 0}
        />
        <MetricCard
          label="Subscribers"
          value={overviewLoading ? "..." : overview?.active_subscribers ?? 0}
          sub={overview ? `${overview.total_subscribers} total` : undefined}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Campaigns */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-medium">Recent Campaigns</h3>
            <Link href="/dashboard/campaigns" className="text-sm text-blue-400 hover:text-blue-300">
              View all
            </Link>
          </div>
          {campaignsLoading ? (
            <p className="text-gray-500 text-sm">Loading...</p>
          ) : !campaigns?.items.length ? (
            <EmptyState
              title="No campaigns yet"
              description="Create your first campaign to get started."
              action={
                <Link
                  href="/dashboard/campaigns/new"
                  className="text-sm px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition"
                >
                  New Campaign
                </Link>
              }
            />
          ) : (
            <div className="space-y-2">
              {campaigns.items.map((c) => (
                <Link
                  key={c.id}
                  href={`/dashboard/campaigns/${c.id}`}
                  className="flex items-center gap-3 p-3 bg-gray-900 border border-gray-800 rounded-lg hover:border-gray-700 transition"
                >
                  <PlatformIcon platform={c.platform} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{c.name}</p>
                    <p className="text-xs text-gray-500">
                      ${(c.daily_budget_cents / 100).toFixed(2)}/day
                    </p>
                  </div>
                  <StatusBadge status={c.status} />
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Pending Approvals */}
        <div>
          <h3 className="text-lg font-medium mb-3">Pending Approvals</h3>
          {draftsLoading ? (
            <p className="text-gray-500 text-sm">Loading...</p>
          ) : !drafts?.items.length ? (
            <EmptyState
              title="All caught up"
              description="No content waiting for approval."
            />
          ) : (
            <div className="space-y-3">
              {drafts.items.map((item) => (
                <ContentCard
                  key={item.id}
                  content={item}
                  onApprove={() => refetchDrafts()}
                  onReject={() => refetchDrafts()}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify build**

```bash
cd frontend && npx tsc --noEmit
```

Expected: No type errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/dashboard/page.tsx
git commit -m "feat(frontend): build dashboard overview with metrics, campaigns, approvals"
```

---

### Task 2: Campaign list page

**Files:**
- Create: `frontend/src/app/dashboard/campaigns/page.tsx`

- [ ] **Step 1: Build the campaigns list page**

Create `frontend/src/app/dashboard/campaigns/page.tsx`:

```tsx
"use client";

import { useState } from "react";
import Link from "next/link";
import { useApi } from "@/hooks/use-api";
import { getCampaigns } from "@/lib/api/campaigns";
import { StatusBadge } from "@/components/status-badge";
import { PlatformIcon } from "@/components/platform-icon";
import { EmptyState } from "@/components/empty-state";
import type { CampaignListResponse, AdPlatform, CampaignStatus } from "@/types/api";

const SITE_ID = "default";

export default function CampaignsPage() {
  const [platformFilter, setPlatformFilter] = useState<AdPlatform | "">("");
  const [statusFilter, setStatusFilter] = useState<CampaignStatus | "">("");

  const { data, loading } = useApi<CampaignListResponse>(
    (token) =>
      getCampaigns(token, {
        site_id: SITE_ID,
        platform: platformFilter || undefined,
        status: statusFilter || undefined,
        limit: 50,
      }),
    [platformFilter, statusFilter],
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold">Campaigns</h2>
        <Link
          href="/dashboard/campaigns/new"
          className="text-sm px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium transition"
        >
          New Campaign
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-4">
        <select
          value={platformFilter}
          onChange={(e) => setPlatformFilter(e.target.value as AdPlatform | "")}
          className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-sm text-gray-300"
        >
          <option value="">All Platforms</option>
          <option value="google_ads">Google Ads</option>
          <option value="facebook_ads">Facebook Ads</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as CampaignStatus | "")}
          className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-sm text-gray-300"
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="active">Active</option>
          <option value="paused">Paused</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {/* Table */}
      {loading ? (
        <p className="text-gray-500 text-sm">Loading campaigns...</p>
      ) : !data?.items.length ? (
        <EmptyState
          title="No campaigns found"
          description="Create a campaign to start generating content and ads."
          action={
            <Link
              href="/dashboard/campaigns/new"
              className="text-sm px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition"
            >
              New Campaign
            </Link>
          }
        />
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-left text-gray-400">
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Platform</th>
                <th className="px-4 py-3 font-medium">Objective</th>
                <th className="px-4 py-3 font-medium">Budget/Day</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Created</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((c) => (
                <tr key={c.id} className="border-b border-gray-800 last:border-0 hover:bg-gray-800/50">
                  <td className="px-4 py-3">
                    <Link href={`/dashboard/campaigns/${c.id}`} className="text-blue-400 hover:text-blue-300">
                      {c.name}
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <PlatformIcon platform={c.platform} />
                  </td>
                  <td className="px-4 py-3 capitalize text-gray-400">{c.objective}</td>
                  <td className="px-4 py-3 text-gray-300">${(c.daily_budget_cents / 100).toFixed(2)}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={c.status} />
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {new Date(c.created_at).toLocaleDateString()}
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
git add frontend/src/app/dashboard/campaigns/
git commit -m "feat(frontend): add campaigns list page with filters"
```

---

### Task 3: Campaign detail page with tabs

**Files:**
- Create: `frontend/src/app/dashboard/campaigns/[id]/page.tsx`

- [ ] **Step 1: Build the campaign detail page**

Create `frontend/src/app/dashboard/campaigns/[id]/page.tsx`:

```tsx
"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useApi, useMutation } from "@/hooks/use-api";
import { getCampaign } from "@/lib/api/campaigns";
import { getContent } from "@/lib/api/content";
import { getAds } from "@/lib/api/ads";
import { approveContent, rejectContent } from "@/lib/api/content";
import { updateAd } from "@/lib/api/ads";
import { StatusBadge } from "@/components/status-badge";
import { PlatformIcon } from "@/components/platform-icon";
import { ContentCard } from "@/components/content-card";
import { AdCard } from "@/components/ad-card";
import { EmptyState } from "@/components/empty-state";
import type { CampaignResponse, ContentListResponse, AdListResponse } from "@/types/api";

type Tab = "content" | "ads" | "analytics";

export default function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<Tab>("content");

  const { data: campaign, loading: campaignLoading } = useApi<CampaignResponse>(
    (token) => getCampaign(token, id),
    [id],
  );

  const { data: contentData, loading: contentLoading, refetch: refetchContent } = useApi<ContentListResponse>(
    (token) => getContent(token, { site_id: campaign?.site_id ?? "", limit: 50 }),
    [campaign?.site_id],
  );

  const { data: adsData, loading: adsLoading, refetch: refetchAds } = useApi<AdListResponse>(
    (token) => getAds(token, { campaign_id: id, limit: 50 }),
    [id],
  );

  const approveMutation = useMutation((token: string, contentId: string) =>
    approveContent(token, contentId),
  );

  const rejectMutation = useMutation((token: string, contentId: string) =>
    rejectContent(token, contentId),
  );

  const approveAdMutation = useMutation((token: string, adId: string) =>
    updateAd(token, adId, { status: "active" }),
  );

  const rejectAdMutation = useMutation((token: string, adId: string) =>
    updateAd(token, adId, { status: "rejected" }),
  );

  const handleApproveContent = async (contentId: string) => {
    await approveMutation.execute(contentId);
    refetchContent();
  };

  const handleRejectContent = async (contentId: string) => {
    await rejectMutation.execute(contentId);
    refetchContent();
  };

  const handleApproveAd = async (adId: string) => {
    await approveAdMutation.execute(adId);
    refetchAds();
  };

  const handleRejectAd = async (adId: string) => {
    await rejectAdMutation.execute(adId);
    refetchAds();
  };

  if (campaignLoading) {
    return <p className="text-gray-500">Loading campaign...</p>;
  }

  if (!campaign) {
    return <p className="text-gray-500">Campaign not found.</p>;
  }

  const tabs: { key: Tab; label: string }[] = [
    { key: "content", label: "Content" },
    { key: "ads", label: "Ads" },
    { key: "analytics", label: "Analytics" },
  ];

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <Link href="/dashboard/campaigns" className="text-sm text-gray-500 hover:text-gray-300 mb-2 inline-block">
          &larr; Campaigns
        </Link>
        <div className="flex items-center gap-3">
          <PlatformIcon platform={campaign.platform} />
          <h2 className="text-2xl font-semibold">{campaign.name}</h2>
          <StatusBadge status={campaign.status} />
        </div>
        <div className="flex gap-4 mt-2 text-sm text-gray-400">
          <span>Objective: {campaign.objective}</span>
          <span>Budget: ${(campaign.daily_budget_cents / 100).toFixed(2)}/day</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-gray-800 mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
              activeTab === tab.key
                ? "border-blue-500 text-white"
                : "border-transparent text-gray-400 hover:text-gray-300"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === "content" && (
        <div>
          {contentLoading ? (
            <p className="text-gray-500 text-sm">Loading content...</p>
          ) : !contentData?.items.length ? (
            <EmptyState title="No content" description="Generate content for this campaign." />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {contentData.items.map((item) => (
                <ContentCard
                  key={item.id}
                  content={item}
                  onApprove={handleApproveContent}
                  onReject={handleRejectContent}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "ads" && (
        <div>
          {adsLoading ? (
            <p className="text-gray-500 text-sm">Loading ads...</p>
          ) : !adsData?.items.length ? (
            <EmptyState title="No ads" description="Generate ads for this campaign." />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {adsData.items.map((ad) => (
                <AdCard
                  key={ad.id}
                  ad={ad}
                  onApprove={handleApproveAd}
                  onReject={handleRejectAd}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "analytics" && (
        <div className="text-gray-400 text-sm">
          Campaign analytics coming in Plan 3.
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
git add frontend/src/app/dashboard/campaigns/
git commit -m "feat(frontend): add campaign detail page with content/ads tabs"
```

---

### Task 4: Campaign wizard — Step 1 (Goal) and Step 2 (Generate)

**Files:**
- Create: `frontend/src/app/dashboard/campaigns/new/page.tsx`

- [ ] **Step 1: Build the campaign wizard**

Create `frontend/src/app/dashboard/campaigns/new/page.tsx`:

```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { generateContent } from "@/lib/api/content";
import { generateAds } from "@/lib/api/ads";
import { createCampaign } from "@/lib/api/campaigns";
import { createContent } from "@/lib/api/content";
import { createAd } from "@/lib/api/ads";
import { approveContent } from "@/lib/api/content";
import { updateAd } from "@/lib/api/ads";
import { scheduleContent } from "@/lib/api/content";
import { StatusBadge } from "@/components/status-badge";
import { PlatformIcon } from "@/components/platform-icon";
import type {
  ContentResponse,
  AdResponse,
  ContentPlatform,
  AdPlatform,
  CampaignObjective,
} from "@/types/api";

const SITE_ID = "default";

const CONTENT_PLATFORMS: ContentPlatform[] = [
  "twitter", "linkedin", "blog", "reddit", "medium", "email",
];

const AD_PLATFORMS: AdPlatform[] = ["google_ads", "facebook_ads"];

type WizardStep = "goal" | "generating" | "review" | "schedule";

interface GeneratedPiece {
  type: "content" | "ad";
  data: ContentResponse | AdResponse;
  approved: boolean;
  rejected: boolean;
}

export default function NewCampaignPage() {
  const router = useRouter();
  const { data: session } = useSession();
  const token = (session as any)?.id_token as string | undefined;

  const [step, setStep] = useState<WizardStep>("goal");

  // Step 1 state
  const [topic, setTopic] = useState("");
  const [tone, setTone] = useState("professional");
  const [selectedContentPlatforms, setSelectedContentPlatforms] = useState<ContentPlatform[]>([]);
  const [selectedAdPlatform, setSelectedAdPlatform] = useState<AdPlatform | "">("");
  const [objective, setObjective] = useState<CampaignObjective>("traffic");
  const [budgetDollars, setBudgetDollars] = useState("10");
  const [campaignName, setCampaignName] = useState("");

  // Step 2-3 state
  const [pieces, setPieces] = useState<GeneratedPiece[]>([]);
  const [generateError, setGenerateError] = useState<string | null>(null);

  // Step 4 state
  const [scheduleDate, setScheduleDate] = useState("");
  const [publishing, setPublishing] = useState(false);

  const toggleContentPlatform = (p: ContentPlatform) => {
    setSelectedContentPlatforms((prev) =>
      prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p],
    );
  };

  const handleGenerate = async () => {
    if (!token || !topic.trim()) return;
    setStep("generating");
    setGenerateError(null);
    const results: GeneratedPiece[] = [];

    try {
      // Generate content for each selected platform
      for (const platform of selectedContentPlatforms) {
        const content = await generateContent(token, {
          site_id: SITE_ID,
          platform,
          content_type: "post",
          topic,
          tone,
        });
        results.push({ type: "content", data: content, approved: false, rejected: false });
      }

      // Generate ads if ad platform selected
      if (selectedAdPlatform) {
        const adResult = await generateAds(token, {
          campaign_id: "pending",
          site_id: SITE_ID,
          platform: selectedAdPlatform,
          topic,
          tone,
          num_variants: 3,
        });
        for (const ad of adResult.ads) {
          results.push({ type: "ad", data: ad, approved: false, rejected: false });
        }
      }

      setPieces(results);
      setStep("review");
    } catch (err: any) {
      setGenerateError(err.message);
      setStep("goal");
    }
  };

  const toggleApprove = (index: number) => {
    setPieces((prev) =>
      prev.map((p, i) =>
        i === index ? { ...p, approved: !p.approved, rejected: false } : p,
      ),
    );
  };

  const toggleReject = (index: number) => {
    setPieces((prev) =>
      prev.map((p, i) =>
        i === index ? { ...p, rejected: !p.rejected, approved: false } : p,
      ),
    );
  };

  const approveAll = () => {
    setPieces((prev) => prev.map((p) => ({ ...p, approved: true, rejected: false })));
  };

  const approvedPieces = pieces.filter((p) => p.approved);

  const handleLaunch = async () => {
    if (!token || approvedPieces.length === 0) return;
    setPublishing(true);

    try {
      // Create the campaign
      const campaign = await createCampaign(token, {
        site_id: SITE_ID,
        name: campaignName || `Campaign: ${topic}`,
        platform: selectedAdPlatform || "google_ads",
        objective,
        daily_budget_cents: Math.round(parseFloat(budgetDollars) * 100),
      });

      // Create and approve content pieces
      for (const piece of approvedPieces) {
        if (piece.type === "content") {
          const c = piece.data as ContentResponse;
          const created = await createContent(token, {
            site_id: SITE_ID,
            platform: c.platform,
            content_type: c.content_type,
            title: c.title,
            body: c.body,
            group_id: campaign.id,
          });
          await approveContent(token, created.id);
          if (scheduleDate) {
            await scheduleContent(token, created.id, {
              scheduled_at: new Date(scheduleDate).toISOString(),
            });
          }
        } else {
          const a = piece.data as AdResponse;
          await createAd(token, {
            campaign_id: campaign.id,
            headline: a.headline,
            headline_2: a.headline_2 ?? undefined,
            headline_3: a.headline_3 ?? undefined,
            description: a.description,
            description_2: a.description_2 ?? undefined,
            display_url: a.display_url ?? undefined,
            final_url: a.final_url,
            status: "active",
          });
        }
      }

      router.push(`/dashboard/campaigns/${campaign.id}`);
    } catch (err: any) {
      setGenerateError(err.message);
      setPublishing(false);
    }
  };

  return (
    <div className="max-w-3xl">
      <h2 className="text-2xl font-semibold mb-6">New Campaign</h2>

      {/* Progress bar */}
      <div className="flex gap-2 mb-8">
        {(["goal", "generating", "review", "schedule"] as WizardStep[]).map((s, i) => (
          <div
            key={s}
            className={`h-1 flex-1 rounded ${
              (["goal", "generating", "review", "schedule"] as WizardStep[]).indexOf(step) >= i
                ? "bg-blue-500"
                : "bg-gray-800"
            }`}
          />
        ))}
      </div>

      {generateError && (
        <div className="bg-red-900/50 border border-red-800 rounded-lg p-3 mb-4 text-sm text-red-300">
          {generateError}
        </div>
      )}

      {/* Step 1: Goal */}
      {step === "goal" && (
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-1">Campaign Name</label>
            <input
              type="text"
              value={campaignName}
              onChange={(e) => setCampaignName(e.target.value)}
              placeholder="e.g., Q2 Investment Guide Launch"
              className="w-full bg-gray-900 border border-gray-800 rounded-lg px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Topic / Goal</label>
            <textarea
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="What do you want to promote? e.g., New blog post about tax-saving investment strategies"
              rows={3}
              className="w-full bg-gray-900 border border-gray-800 rounded-lg px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Tone</label>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-2 text-sm"
            >
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="persuasive">Persuasive</option>
              <option value="informative">Informative</option>
              <option value="friendly">Friendly</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Content Platforms</label>
            <div className="flex flex-wrap gap-2">
              {CONTENT_PLATFORMS.map((p) => (
                <button
                  key={p}
                  onClick={() => toggleContentPlatform(p)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border transition ${
                    selectedContentPlatforms.includes(p)
                      ? "border-blue-500 bg-blue-900/30 text-blue-300"
                      : "border-gray-800 text-gray-400 hover:border-gray-700"
                  }`}
                >
                  <PlatformIcon platform={p} />
                  <span className="capitalize">{p}</span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Ad Platform (optional)</label>
            <div className="flex gap-2">
              {AD_PLATFORMS.map((p) => (
                <button
                  key={p}
                  onClick={() => setSelectedAdPlatform(selectedAdPlatform === p ? "" : p)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border transition ${
                    selectedAdPlatform === p
                      ? "border-blue-500 bg-blue-900/30 text-blue-300"
                      : "border-gray-800 text-gray-400 hover:border-gray-700"
                  }`}
                >
                  <PlatformIcon platform={p} />
                  <span>{p === "google_ads" ? "Google Ads" : "Facebook Ads"}</span>
                </button>
              ))}
            </div>
          </div>

          {selectedAdPlatform && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Objective</label>
                <select
                  value={objective}
                  onChange={(e) => setObjective(e.target.value as CampaignObjective)}
                  className="w-full bg-gray-900 border border-gray-800 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="traffic">Traffic</option>
                  <option value="conversions">Conversions</option>
                  <option value="awareness">Awareness</option>
                  <option value="leads">Leads</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Daily Budget ($)</label>
                <input
                  type="number"
                  value={budgetDollars}
                  onChange={(e) => setBudgetDollars(e.target.value)}
                  min="1"
                  step="1"
                  className="w-full bg-gray-900 border border-gray-800 rounded-lg px-3 py-2 text-sm"
                />
              </div>
            </div>
          )}

          <button
            onClick={handleGenerate}
            disabled={!topic.trim() || (selectedContentPlatforms.length === 0 && !selectedAdPlatform)}
            className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 disabled:text-gray-500 text-white font-medium transition"
          >
            Generate Content & Ads
          </button>
        </div>
      )}

      {/* Step 2: Generating */}
      {step === "generating" && (
        <div className="flex flex-col items-center justify-center py-16">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-gray-400">Generating content and ads with AI...</p>
        </div>
      )}

      {/* Step 3: Review */}
      {step === "review" && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-gray-400">
              {pieces.length} pieces generated. Approve the ones you want to launch.
            </p>
            <button
              onClick={approveAll}
              className="text-sm px-3 py-1 rounded bg-green-800 hover:bg-green-700 text-green-200 transition"
            >
              Approve All
            </button>
          </div>

          <div className="space-y-3 mb-6">
            {pieces.map((piece, i) => (
              <div
                key={i}
                className={`bg-gray-900 border rounded-lg p-4 transition ${
                  piece.approved
                    ? "border-green-700"
                    : piece.rejected
                      ? "border-red-800 opacity-50"
                      : "border-gray-800"
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-medium uppercase text-gray-500">{piece.type}</span>
                  {piece.type === "content" && (
                    <PlatformIcon platform={(piece.data as ContentResponse).platform} />
                  )}
                  {piece.approved && <StatusBadge status="approved" />}
                  {piece.rejected && <StatusBadge status="rejected" />}
                </div>
                {piece.type === "content" ? (
                  <>
                    <h4 className="font-medium mb-1">{(piece.data as ContentResponse).title}</h4>
                    <p className="text-sm text-gray-400 line-clamp-3">
                      {(piece.data as ContentResponse).body}
                    </p>
                  </>
                ) : (
                  <>
                    <h4 className="font-medium mb-1">{(piece.data as AdResponse).headline}</h4>
                    <p className="text-sm text-gray-400">{(piece.data as AdResponse).description}</p>
                  </>
                )}
                <div className="flex gap-2 mt-3">
                  <button
                    onClick={() => toggleApprove(i)}
                    className={`text-xs px-3 py-1 rounded transition ${
                      piece.approved
                        ? "bg-green-700 text-green-100"
                        : "bg-green-900 hover:bg-green-800 text-green-200"
                    }`}
                  >
                    {piece.approved ? "Approved" : "Approve"}
                  </button>
                  <button
                    onClick={() => toggleReject(i)}
                    className={`text-xs px-3 py-1 rounded transition ${
                      piece.rejected
                        ? "bg-red-700 text-red-100"
                        : "bg-red-900 hover:bg-red-800 text-red-200"
                    }`}
                  >
                    {piece.rejected ? "Rejected" : "Reject"}
                  </button>
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={() => setStep("schedule")}
            disabled={approvedPieces.length === 0}
            className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 disabled:text-gray-500 text-white font-medium transition"
          >
            Continue with {approvedPieces.length} approved piece{approvedPieces.length !== 1 ? "s" : ""}
          </button>
        </div>
      )}

      {/* Step 4: Schedule & Launch */}
      {step === "schedule" && (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium mb-2">Schedule & Launch</h3>
            <p className="text-sm text-gray-400 mb-4">
              {approvedPieces.length} piece{approvedPieces.length !== 1 ? "s" : ""} ready to go.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Schedule for (optional)</label>
            <input
              type="datetime-local"
              value={scheduleDate}
              onChange={(e) => setScheduleDate(e.target.value)}
              className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-2 text-sm"
            />
            <p className="text-xs text-gray-500 mt-1">Leave empty to save as approved (publish manually later).</p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep("review")}
              className="px-4 py-2.5 rounded-lg border border-gray-800 text-gray-300 hover:bg-gray-800 transition"
            >
              Back
            </button>
            <button
              onClick={handleLaunch}
              disabled={publishing}
              className="flex-1 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 disabled:text-gray-500 text-white font-medium transition"
            >
              {publishing ? "Launching..." : "Launch Campaign"}
            </button>
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
git add frontend/src/app/dashboard/campaigns/new/
git commit -m "feat(frontend): add guided campaign wizard with 4-step flow"
```

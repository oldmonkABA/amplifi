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

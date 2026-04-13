"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useApi, useMutation } from "@/hooks/use-api";
import { getCampaign } from "@/lib/api/campaigns";
import { getContent, updateContent, deleteContent } from "@/lib/api/content";
import { getAds, updateAd, deleteAd } from "@/lib/api/ads";
import { approveContent, rejectContent } from "@/lib/api/content";
import { StatusBadge } from "@/components/status-badge";
import { PlatformIcon } from "@/components/platform-icon";
import { EmptyState } from "@/components/empty-state";
import type { CampaignResponse, ContentResponse, ContentListResponse, AdResponse, AdListResponse } from "@/types/api";

type Tab = "content" | "ads" | "analytics";

function ContentModal({
  content,
  onClose,
  onApprove,
  onReject,
  onSave,
  onDelete,
}: {
  content: ContentResponse;
  onClose: () => void;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  onSave: (id: string, title: string, body: string) => void;
  onDelete: (id: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(content.title);
  const [body, setBody] = useState(content.body);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />
      <div
        className="relative glass-card rounded-3xl max-w-2xl w-full max-h-[85vh] flex flex-col animate-scale-in"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 pb-4 border-b border-white/[0.06]">
          <div className="flex items-center gap-3">
            <PlatformIcon platform={content.platform} />
            <StatusBadge status={content.status} />
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] flex items-center justify-center transition-colors"
          >
            <svg className="w-4 h-4 text-white/40" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6">
          {editing ? (
            <div className="space-y-4">
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-white/[0.03] border border-white/[0.08] rounded-xl px-4 py-3 text-lg font-bold tracking-tight focus:border-amber-400/40"
              />
              <textarea
                value={body}
                onChange={(e) => setBody(e.target.value)}
                rows={15}
                className="w-full bg-white/[0.03] border border-white/[0.08] rounded-xl px-4 py-3 text-base text-white/60 leading-relaxed resize-y focus:border-amber-400/40"
              />
            </div>
          ) : (
            <>
              <h2 className="text-2xl font-bold tracking-tight mb-6">{content.title}</h2>
              <div className="text-base text-white/60 leading-relaxed whitespace-pre-wrap">{content.body}</div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center gap-2 p-6 pt-4 border-t border-white/[0.06]">
          {editing ? (
            <>
              <button
                onClick={() => { onSave(content.id, title, body); onClose(); }}
                className="btn-primary"
              >
                Save Changes
              </button>
              <button
                onClick={() => { setEditing(false); setTitle(content.title); setBody(content.body); }}
                className="text-sm px-5 py-2.5 rounded-xl font-semibold bg-white/[0.04] hover:bg-white/[0.08] text-white/40 transition-colors"
              >
                Cancel
              </button>
            </>
          ) : (
            <>
              {content.status === "draft" && (
                <>
                  <button
                    onClick={() => { onApprove(content.id); onClose(); }}
                    className="text-sm px-5 py-2.5 rounded-xl font-semibold transition-all"
                    style={{ background: "linear-gradient(135deg, #10b981 0%, #059669 100%)", color: "#0a0a0f" }}
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => { onReject(content.id); onClose(); }}
                    className="text-sm px-5 py-2.5 rounded-xl font-semibold bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors"
                  >
                    Reject
                  </button>
                </>
              )}
              <button
                onClick={() => setEditing(true)}
                className="text-sm px-5 py-2.5 rounded-xl font-semibold bg-white/[0.04] hover:bg-white/[0.08] text-white/50 transition-colors flex items-center gap-2"
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit
              </button>
              <div className="flex-1" />
              <button
                onClick={() => { if (confirm("Delete this content?")) { onDelete(content.id); onClose(); } }}
                className="text-sm px-4 py-2.5 rounded-xl font-semibold bg-red-500/5 hover:bg-red-500/15 text-red-400/60 hover:text-red-400 transition-colors flex items-center gap-2"
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function AdModal({
  ad,
  onClose,
  onSave,
  onDelete,
}: {
  ad: AdResponse;
  onClose: () => void;
  onSave: (id: string, data: { headline?: string; description?: string }) => void;
  onDelete: (id: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [headline, setHeadline] = useState(ad.headline);
  const [description, setDescription] = useState(ad.description);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />
      <div
        className="relative glass-card rounded-3xl max-w-xl w-full flex flex-col animate-scale-in"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 pb-4 border-b border-white/[0.06]">
          <div className="flex items-center gap-3">
            <span className="text-xs font-bold uppercase tracking-widest text-white/20">Ad Preview</span>
            <StatusBadge status={ad.status} />
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] flex items-center justify-center transition-colors"
          >
            <svg className="w-4 h-4 text-white/40" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5 overflow-y-auto max-h-[60vh]">
          {/* Ad image */}
          {ad.image_url && !editing && (
            <div className="rounded-2xl overflow-hidden" style={{ border: '1px solid var(--border)' }}>
              <img src={ad.image_url} alt="Ad creative" className="w-full h-auto" />
            </div>
          )}

          {editing ? (
            <div className="space-y-4">
              <div>
                <label className="label block mb-2">Headline</label>
                <input
                  type="text"
                  value={headline}
                  onChange={(e) => setHeadline(e.target.value)}
                  className="w-full"
                />
              </div>
              <div>
                <label className="label block mb-2">Primary Text</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={6}
                  className="w-full"
                />
              </div>
            </div>
          ) : (
            <>
              <div className="card rounded-2xl p-5">
                <p className="label mb-3">Headline</p>
                <h3 className="text-xl font-bold tracking-tight mb-1">{ad.headline}</h3>
                {ad.headline_2 && <h4 className="text-lg font-semibold mb-1" style={{ color: 'var(--text-secondary)' }}>{ad.headline_2}</h4>}
                {ad.headline_3 && <h4 className="text-base font-medium" style={{ color: 'var(--text-tertiary)' }}>{ad.headline_3}</h4>}
              </div>

              <div className="card rounded-2xl p-5">
                <p className="label mb-3">Primary Text</p>
                <p className="text-base leading-relaxed whitespace-pre-wrap" style={{ color: 'var(--text-secondary)' }}>{ad.description}</p>
                {ad.description_2 && (
                  <>
                    <p className="label mt-4 mb-2">Link Description</p>
                    <p className="text-sm" style={{ color: 'var(--text-tertiary)' }}>{ad.description_2}</p>
                  </>
                )}
              </div>

              <div className="flex items-center gap-6 text-sm">
                <div>
                  <p className="label mb-1">Final URL</p>
                  <p className="font-medium" style={{ color: 'var(--accent)' }}>{ad.final_url}</p>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center gap-2 p-6 pt-4 border-t border-white/[0.06]">
          {editing ? (
            <>
              <button
                onClick={() => { onSave(ad.id, { headline, description }); onClose(); }}
                className="btn-primary"
              >
                Save Changes
              </button>
              <button
                onClick={() => { setEditing(false); setHeadline(ad.headline); setDescription(ad.description); }}
                className="text-sm px-5 py-2.5 rounded-xl font-semibold bg-white/[0.04] hover:bg-white/[0.08] text-white/40 transition-colors"
              >
                Cancel
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setEditing(true)}
                className="text-sm px-5 py-2.5 rounded-xl font-semibold bg-white/[0.04] hover:bg-white/[0.08] text-white/50 transition-colors flex items-center gap-2"
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit
              </button>
              <div className="flex-1" />
              <button
                onClick={() => { if (confirm("Delete this ad?")) { onDelete(ad.id); onClose(); } }}
                className="text-sm px-4 py-2.5 rounded-xl font-semibold bg-red-500/5 hover:bg-red-500/15 text-red-400/60 hover:text-red-400 transition-colors flex items-center gap-2"
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<Tab>("content");
  const [selectedContent, setSelectedContent] = useState<ContentResponse | null>(null);
  const [selectedAd, setSelectedAd] = useState<AdResponse | null>(null);

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

  const approveMut = useMutation((token: string, contentId: string) => approveContent(token, contentId));
  const rejectMut = useMutation((token: string, contentId: string) => rejectContent(token, contentId));
  const approveAdMut = useMutation((token: string, adId: string) => updateAd(token, adId, { status: "active" }));
  const rejectAdMut = useMutation((token: string, adId: string) => updateAd(token, adId, { status: "rejected" }));
  const updateContentMut = useMutation((token: string, args: { id: string; title: string; body: string }) =>
    updateContent(token, args.id, { title: args.title, body: args.body }),
  );
  const deleteContentMut = useMutation((token: string, contentId: string) => deleteContent(token, contentId));
  const updateAdMut = useMutation((token: string, args: { id: string; data: { headline?: string; description?: string } }) =>
    updateAd(token, args.id, args.data),
  );
  const deleteAdMut = useMutation((token: string, adId: string) => deleteAd(token, adId));

  const handleApproveContent = async (cid: string) => { await approveMut.execute(cid); refetchContent(); };
  const handleRejectContent = async (cid: string) => { await rejectMut.execute(cid); refetchContent(); };
  const handleApproveAd = async (aid: string) => { await approveAdMut.execute(aid); refetchAds(); };
  const handleRejectAd = async (aid: string) => { await rejectAdMut.execute(aid); refetchAds(); };
  const handleSaveContent = async (cid: string, title: string, body: string) => {
    await updateContentMut.execute({ id: cid, title, body });
    refetchContent();
  };
  const handleDeleteContent = async (cid: string) => { await deleteContentMut.execute(cid); refetchContent(); };
  const handleSaveAd = async (aid: string, data: { headline?: string; description?: string }) => {
    await updateAdMut.execute({ id: aid, data });
    refetchAds();
  };
  const handleDeleteAd = async (aid: string) => { await deleteAdMut.execute(aid); refetchAds(); };

  if (campaignLoading) {
    return (
      <div className="space-y-4">
        <div className="glass-card rounded-2xl p-6 animate-shimmer h-[100px]" />
        <div className="glass-card rounded-2xl p-6 animate-shimmer h-[200px]" />
      </div>
    );
  }

  if (!campaign) {
    return <p className="text-white/40 text-lg">Campaign not found.</p>;
  }

  const tabs: { key: Tab; label: string; count?: number }[] = [
    { key: "content", label: "Content", count: contentData?.items.length },
    { key: "ads", label: "Ads", count: adsData?.items.length },
    { key: "analytics", label: "Analytics" },
  ];

  return (
    <div>
      {/* Header */}
      <div className="mb-8 animate-fade-up">
        <Link href="/dashboard/campaigns" className="text-sm text-white/30 hover:text-white/50 mb-3 inline-flex items-center gap-1 font-medium transition-colors">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Campaigns
        </Link>
        <div className="flex items-center gap-4 mb-2">
          <PlatformIcon platform={campaign.platform} />
          <h2 className="text-3xl font-bold tracking-tight">{campaign.name}</h2>
          <StatusBadge status={campaign.status} />
        </div>
        <div className="flex gap-6 mt-2 text-sm text-white/30 font-medium">
          <span>Objective: <span className="text-white/50 capitalize">{campaign.objective}</span></span>
          <span>Budget: <span className="text-white/50">${(campaign.daily_budget_cents / 100).toFixed(2)}/day</span></span>
          <span>Created: <span className="text-white/50">{new Date(campaign.created_at).toLocaleDateString()}</span></span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-white/[0.06] mb-8">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-5 py-3 text-sm font-semibold border-b-2 transition-all ${
              activeTab === tab.key
                ? "border-amber-400 text-amber-400"
                : "border-transparent text-white/30 hover:text-white/50"
            }`}
          >
            {tab.label}
            {tab.count !== undefined && (
              <span className={`ml-2 px-1.5 py-0.5 rounded text-[11px] ${
                activeTab === tab.key ? "bg-amber-400/15" : "bg-white/[0.04]"
              }`}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Content Tab */}
      {activeTab === "content" && (
        <div>
          {contentLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2].map((i) => (
                <div key={i} className="glass-card rounded-2xl p-5 animate-shimmer h-[160px]" />
              ))}
            </div>
          ) : !contentData?.items.length ? (
            <EmptyState title="No content" description="Generate content for this campaign." />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {contentData.items.map((item) => (
                <div
                  key={item.id}
                  onClick={() => setSelectedContent(item)}
                  className="glass-card rounded-2xl p-5 cursor-pointer group hover:scale-[1.01] transition-all duration-300"
                >
                  <div className="flex items-center justify-between mb-3">
                    <PlatformIcon platform={item.platform} />
                    <StatusBadge status={item.status} />
                  </div>
                  <h4 className="font-bold text-base mb-1.5 line-clamp-1 tracking-tight group-hover:text-amber-400 transition-colors">{item.title}</h4>
                  <p className="text-sm text-white/25 line-clamp-3 leading-relaxed mb-3">{item.body}</p>
                  <span className="text-xs text-white/15 font-medium">Click to view / edit</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Ads Tab */}
      {activeTab === "ads" && (
        <div>
          {adsLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="glass-card rounded-2xl p-5 animate-shimmer h-[160px]" />
              ))}
            </div>
          ) : !adsData?.items.length ? (
            <EmptyState title="No ads" description="Generate ads for this campaign." />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {adsData.items.map((ad) => (
                <div
                  key={ad.id}
                  onClick={() => setSelectedAd(ad)}
                  className="card card-interactive rounded-2xl overflow-hidden"
                >
                  {ad.image_url && (
                    <img src={ad.image_url} alt="Ad creative" className="w-full h-40 object-cover" />
                  )}
                  <div className="p-5">
                    <div className="flex items-center justify-between mb-3">
                      <span className="label">Ad</span>
                      <StatusBadge status={ad.status} />
                    </div>
                    <h4 className="font-semibold text-base mb-1.5 line-clamp-1">{ad.headline}</h4>
                    <p className="text-sm line-clamp-2 leading-relaxed mb-1" style={{ color: 'var(--text-tertiary)' }}>{ad.description}</p>
                    <p className="text-xs mt-2 font-medium" style={{ color: 'var(--text-tertiary)' }}>Click to view</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === "analytics" && (
        <EmptyState title="Campaign Analytics" description="Analytics for individual campaigns coming soon." />
      )}

      {/* Modals */}
      {selectedContent && (
        <ContentModal
          content={selectedContent}
          onClose={() => setSelectedContent(null)}
          onApprove={handleApproveContent}
          onReject={handleRejectContent}
          onSave={handleSaveContent}
          onDelete={handleDeleteContent}
        />
      )}
      {selectedAd && (
        <AdModal
          ad={selectedAd}
          onClose={() => setSelectedAd(null)}
          onSave={handleSaveAd}
          onDelete={handleDeleteAd}
        />
      )}
    </div>
  );
}

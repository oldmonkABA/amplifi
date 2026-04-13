"use client";

import { useState } from "react";
import { useApi, useMutation } from "@/hooks/use-api";
import { getContent, approveContent, rejectContent } from "@/lib/api/content";
import { StatusBadge } from "@/components/status-badge";
import { PlatformIcon } from "@/components/platform-icon";
import { EmptyState } from "@/components/empty-state";
import Link from "next/link";
import type { ContentResponse, ContentListResponse, ContentPlatform, ContentStatus } from "@/types/api";

import { DEV_SITE_ID as SITE_ID } from "@/lib/constants";

const PLATFORMS: ContentPlatform[] = [
  "twitter", "linkedin", "reddit", "blog", "medium",
  "quora", "telegram", "youtube", "hackernews", "producthunt", "email",
];

function ContentDetailModal({
  content,
  onClose,
  onApprove,
  onReject,
}: {
  content: ContentResponse;
  onClose: () => void;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />

      {/* Modal */}
      <div
        className="relative glass-card rounded-3xl max-w-2xl w-full max-h-[85vh] flex flex-col animate-scale-in"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 pb-4 border-b border-white/[0.06]">
          <div className="flex items-center gap-3">
            <PlatformIcon platform={content.platform} />
            <StatusBadge status={content.status} />
            <span className="text-sm text-white/20 font-medium">
              {new Date(content.created_at).toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </span>
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
          <h2 className="text-2xl font-bold tracking-tight mb-6">{content.title}</h2>
          <div className="text-base text-white/60 leading-relaxed whitespace-pre-wrap">
            {content.body}
          </div>
        </div>

        {/* Footer */}
        {content.status === "draft" && (
          <div className="flex items-center gap-3 p-6 pt-4 border-t border-white/[0.06]">
            <button
              onClick={() => { onApprove(content.id); onClose(); }}
              className="btn-primary flex items-center gap-2"
              style={{ background: "linear-gradient(135deg, #10b981 0%, #059669 100%)" }}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              Approve
            </button>
            <button
              onClick={() => { onReject(content.id); onClose(); }}
              className="text-sm px-5 py-2.5 rounded-xl font-semibold bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors"
            >
              Reject
            </button>
            <div className="flex-1" />
            <span className="text-xs text-white/15 font-medium capitalize">{content.platform} &middot; {content.content_type}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default function ContentPage() {
  const [platformFilter, setPlatformFilter] = useState<ContentPlatform | "">("");
  const [statusFilter, setStatusFilter] = useState<ContentStatus | "">("");
  const [selectedContent, setSelectedContent] = useState<ContentResponse | null>(null);

  const { data, loading, refetch } = useApi<ContentListResponse>(
    (token) =>
      getContent(token, {
        site_id: SITE_ID,
        platform: platformFilter || undefined,
        status: statusFilter || undefined,
        limit: 50,
      }),
    [platformFilter, statusFilter],
  );

  const approveMut = useMutation((token: string, id: string) => approveContent(token, id));
  const rejectMut = useMutation((token: string, id: string) => rejectContent(token, id));

  const handleApprove = async (id: string) => {
    await approveMut.execute(id);
    refetch();
  };

  const handleReject = async (id: string) => {
    await rejectMut.execute(id);
    refetch();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-bold tracking-tight">Content</h2>
        <Link
          href="/dashboard/campaigns/new"
          className="btn-primary flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Generate Content
        </Link>
      </div>

      <div className="flex gap-3 mb-6">
        <select
          value={platformFilter}
          onChange={(e) => setPlatformFilter(e.target.value as ContentPlatform | "")}
          className="glass-card rounded-xl px-4 py-2.5 text-sm text-white/60 font-medium"
        >
          <option value="">All Platforms</option>
          {PLATFORMS.map((p) => (
            <option key={p} value={p} className="capitalize">
              {p}
            </option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as ContentStatus | "")}
          className="glass-card rounded-xl px-4 py-2.5 text-sm text-white/60 font-medium"
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="approved">Approved</option>
          <option value="scheduled">Scheduled</option>
          <option value="published">Published</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="glass-card rounded-2xl p-6 animate-shimmer h-[100px]" />
          ))}
        </div>
      ) : !data?.items.length ? (
        <EmptyState
          title="No content found"
          description="Generate content through a campaign or directly."
        />
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden">
          <table className="data-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Platform</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((item) => (
                <tr
                  key={item.id}
                  className="cursor-pointer"
                  onClick={() => setSelectedContent(item)}
                >
                  <td className="max-w-md">
                    <span className="font-semibold text-[15px] block hover:text-amber-400 transition-colors">{item.title}</span>
                    <p className="text-sm text-white/25 line-clamp-2 mt-1 leading-relaxed">{item.body}</p>
                  </td>
                  <td>
                    <PlatformIcon platform={item.platform} />
                  </td>
                  <td>
                    <StatusBadge status={item.status} />
                  </td>
                  <td className="text-white/30 text-sm">
                    {new Date(item.created_at).toLocaleDateString()}
                  </td>
                  <td>
                    {item.status === "draft" && (
                      <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => handleApprove(item.id)}
                          className="text-sm px-4 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 font-semibold transition-colors"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => handleReject(item.id)}
                          className="text-sm px-4 py-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 font-semibold transition-colors"
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Detail Modal */}
      {selectedContent && (
        <ContentDetailModal
          content={selectedContent}
          onClose={() => setSelectedContent(null)}
          onApprove={handleApprove}
          onReject={handleReject}
        />
      )}
    </div>
  );
}

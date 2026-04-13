"use client";

import { useState } from "react";
import { useApi, useMutation } from "@/hooks/use-api";
import { getContent, approveContent, rejectContent } from "@/lib/api/content";
import { StatusBadge } from "@/components/status-badge";
import { PlatformIcon } from "@/components/platform-icon";
import { EmptyState } from "@/components/empty-state";
import Link from "next/link";
import type { ContentListResponse, ContentPlatform, ContentStatus } from "@/types/api";

const SITE_ID = "default";

const PLATFORMS: ContentPlatform[] = [
  "twitter", "linkedin", "reddit", "blog", "medium",
  "quora", "telegram", "youtube", "hackernews", "producthunt", "email",
];

export default function ContentPage() {
  const [platformFilter, setPlatformFilter] = useState<ContentPlatform | "">("");
  const [statusFilter, setStatusFilter] = useState<ContentStatus | "">("");

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
        <h2 className="text-2xl font-semibold">Content</h2>
        <Link
          href="/dashboard/campaigns/new"
          className="text-sm px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium transition"
        >
          Generate Content
        </Link>
      </div>

      <div className="flex gap-3 mb-4">
        <select
          value={platformFilter}
          onChange={(e) => setPlatformFilter(e.target.value as ContentPlatform | "")}
          className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-sm text-gray-300"
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
          className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-sm text-gray-300"
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
        <p className="text-gray-500 text-sm">Loading content...</p>
      ) : !data?.items.length ? (
        <EmptyState
          title="No content found"
          description="Generate content through a campaign or directly."
        />
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-left text-gray-400">
                <th className="px-4 py-3 font-medium">Title</th>
                <th className="px-4 py-3 font-medium">Platform</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Created</th>
                <th className="px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((item) => (
                <tr key={item.id} className="border-b border-gray-800 last:border-0 hover:bg-gray-800/50">
                  <td className="px-4 py-3">
                    <span className="font-medium">{item.title}</span>
                    <p className="text-xs text-gray-500 line-clamp-1 mt-0.5">{item.body}</p>
                  </td>
                  <td className="px-4 py-3">
                    <PlatformIcon platform={item.platform} />
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={item.status} />
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {new Date(item.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    {item.status === "draft" && (
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleApprove(item.id)}
                          className="text-xs px-2 py-1 rounded bg-green-900 hover:bg-green-800 text-green-300 transition"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => handleReject(item.id)}
                          className="text-xs px-2 py-1 rounded bg-red-900 hover:bg-red-800 text-red-300 transition"
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
    </div>
  );
}

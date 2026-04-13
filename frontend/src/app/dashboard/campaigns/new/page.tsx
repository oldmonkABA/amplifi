"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { getToken } from "@/lib/api";
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

import { DEV_SITE_ID as SITE_ID } from "@/lib/constants";

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
  const token = getToken();

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
    const errors: string[] = [];

    // Generate content for each selected platform
    for (const platform of selectedContentPlatforms) {
      try {
        const content = await generateContent(token, {
          site_id: SITE_ID,
          platform,
          content_type: "post",
          topic,
          tone,
        });
        results.push({ type: "content", data: content, approved: false, rejected: false });
      } catch (err: any) {
        errors.push(`Content (${platform}): ${err.message}`);
      }
    }

    // Generate ads if ad platform selected
    if (selectedAdPlatform) {
      try {
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
      } catch (err: any) {
        errors.push(`Ads (${selectedAdPlatform}): ${err.message}`);
      }
    }

    if (errors.length > 0) {
      setGenerateError(errors.join("\n"));
    }

    if (results.length > 0) {
      setPieces(results);
      setStep("review");
    } else {
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

      // Approve existing content (already saved during generate step) and create ads
      for (const piece of approvedPieces) {
        if (piece.type === "content") {
          const c = piece.data as ContentResponse;
          // Content was already created by the generate endpoint — just approve it
          await approveContent(token, c.id);
          if (scheduleDate) {
            await scheduleContent(token, c.id, {
              scheduled_at: new Date(scheduleDate).toISOString(),
            });
          }
        } else {
          // Ads with campaign_id="pending" were NOT saved — create them now with real campaign ID
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
      <h2 className="text-3xl mb-6">New Campaign</h2>

      {/* Progress bar */}
      <div className="flex gap-2 mb-8">
        {(["goal", "generating", "review", "schedule"] as WizardStep[]).map((s, i) => (
          <div
            key={s}
            className="h-1 flex-1 rounded"
            style={{
              background:
                (["goal", "generating", "review", "schedule"] as WizardStep[]).indexOf(step) >= i
                  ? "var(--accent)"
                  : "var(--border)",
            }}
          />
        ))}
      </div>

      {generateError && (
        <div
          className="rounded-lg p-3 mb-4 text-sm"
          style={{ background: "var(--red-dim)", border: "1px solid var(--red)", color: "var(--red)" }}
        >
          {generateError}
        </div>
      )}

      {/* Step 1: Goal */}
      {step === "goal" && (
        <div className="space-y-6">
          <div>
            <label className="label block mb-2">Campaign Name</label>
            <input
              type="text"
              value={campaignName}
              onChange={(e) => setCampaignName(e.target.value)}
              placeholder="e.g., Q2 Investment Guide Launch"
              className="w-full rounded-lg px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="label block mb-2">Topic / Goal</label>
            <textarea
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="What do you want to promote? e.g., New blog post about tax-saving investment strategies"
              rows={3}
              className="w-full rounded-lg px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="label block mb-2">Tone</label>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="rounded-lg px-3 py-2 text-sm"
            >
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="persuasive">Persuasive</option>
              <option value="informative">Informative</option>
              <option value="friendly">Friendly</option>
            </select>
          </div>

          <div>
            <label className="label block mb-2">Content Platforms</label>
            <div className="flex flex-wrap gap-2">
              {CONTENT_PLATFORMS.map((p) => (
                <button
                  key={p}
                  onClick={() => toggleContentPlatform(p)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border transition"
                  style={
                    selectedContentPlatforms.includes(p)
                      ? { borderColor: "var(--accent)", background: "var(--accent-dim)", color: "var(--accent)" }
                      : { borderColor: "var(--border)", color: "var(--text-secondary)" }
                  }
                >
                  <PlatformIcon platform={p} />
                  <span className="capitalize">{p}</span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="label block mb-2">Ad Platform (optional)</label>
            <div className="flex gap-2">
              {AD_PLATFORMS.map((p) => (
                <button
                  key={p}
                  onClick={() => setSelectedAdPlatform(selectedAdPlatform === p ? "" : p)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border transition"
                  style={
                    selectedAdPlatform === p
                      ? { borderColor: "var(--accent)", background: "var(--accent-dim)", color: "var(--accent)" }
                      : { borderColor: "var(--border)", color: "var(--text-secondary)" }
                  }
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
                <label className="label block mb-2">Objective</label>
                <select
                  value={objective}
                  onChange={(e) => setObjective(e.target.value as CampaignObjective)}
                  className="w-full rounded-lg px-3 py-2 text-sm"
                >
                  <option value="traffic">Traffic</option>
                  <option value="conversions">Conversions</option>
                  <option value="awareness">Awareness</option>
                  <option value="leads">Leads</option>
                </select>
              </div>
              <div>
                <label className="label block mb-2">Daily Budget ($)</label>
                <input
                  type="number"
                  value={budgetDollars}
                  onChange={(e) => setBudgetDollars(e.target.value)}
                  min="1"
                  step="1"
                  className="w-full rounded-lg px-3 py-2 text-sm"
                />
              </div>
            </div>
          )}

          <button
            onClick={handleGenerate}
            disabled={!topic.trim() || (selectedContentPlatforms.length === 0 && !selectedAdPlatform)}
            className="btn-primary w-full py-3"
          >
            Generate Content & Ads
          </button>
        </div>
      )}

      {/* Step 2: Generating */}
      {step === "generating" && (
        <div className="flex flex-col items-center justify-center py-16">
          <div
            className="w-8 h-8 border-2 rounded-full animate-spin mb-4"
            style={{ borderColor: "var(--accent)", borderTopColor: "transparent" }}
          />
          <p style={{ color: "var(--text-secondary)" }}>Generating content and ads with AI...</p>
        </div>
      )}

      {/* Step 3: Review */}
      {step === "review" && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
              {pieces.length} pieces generated. Approve the ones you want to launch.
            </p>
            <button
              onClick={approveAll}
              className="text-sm px-3 py-1 rounded transition"
              style={{ background: "var(--green-dim)", color: "var(--green)" }}
            >
              Approve All
            </button>
          </div>

          <div className="space-y-3 mb-6">
            {pieces.map((piece, i) => (
              <div
                key={i}
                className={`card transition${piece.rejected ? " opacity-50" : ""}`}
                style={{
                  borderColor: piece.approved
                    ? "var(--green)"
                    : piece.rejected
                      ? "var(--red)"
                      : undefined,
                }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="label">{piece.type}</span>
                  {piece.type === "content" && (
                    <PlatformIcon platform={(piece.data as ContentResponse).platform} />
                  )}
                  {piece.approved && <StatusBadge status="approved" />}
                  {piece.rejected && <StatusBadge status="rejected" />}
                </div>
                {piece.type === "content" ? (
                  <>
                    <h4 className="text-base font-semibold mb-1">{(piece.data as ContentResponse).title}</h4>
                    <p className="text-sm line-clamp-3" style={{ color: "var(--text-tertiary)" }}>
                      {(piece.data as ContentResponse).body}
                    </p>
                  </>
                ) : (
                  <>
                    <h4 className="text-base font-semibold mb-1">{(piece.data as AdResponse).headline}</h4>
                    <p className="text-sm" style={{ color: "var(--text-tertiary)" }}>{(piece.data as AdResponse).description}</p>
                  </>
                )}
                <div className="flex gap-2 mt-3">
                  <button
                    onClick={() => toggleApprove(i)}
                    className="text-xs px-3 py-1 rounded transition"
                    style={{
                      background: piece.approved ? "var(--green)" : "var(--green-dim)",
                      color: piece.approved ? "var(--bg)" : "var(--green)",
                    }}
                  >
                    {piece.approved ? "Approved" : "Approve"}
                  </button>
                  <button
                    onClick={() => toggleReject(i)}
                    className="text-xs px-3 py-1 rounded transition"
                    style={{
                      background: piece.rejected ? "var(--red)" : "var(--red-dim)",
                      color: piece.rejected ? "var(--bg)" : "var(--red)",
                    }}
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
            className="btn-primary w-full py-3"
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
            <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>
              {approvedPieces.length} piece{approvedPieces.length !== 1 ? "s" : ""} ready to go.
            </p>
          </div>

          <div>
            <label className="label block mb-2">Schedule for (optional)</label>
            <input
              type="datetime-local"
              value={scheduleDate}
              onChange={(e) => setScheduleDate(e.target.value)}
              className="rounded-lg px-3 py-2 text-sm"
            />
            <p className="text-xs mt-1" style={{ color: "var(--text-secondary)" }}>Leave empty to save as approved (publish manually later).</p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep("review")}
              className="btn-ghost"
            >
              Back
            </button>
            <button
              onClick={handleLaunch}
              disabled={publishing}
              className="btn-primary flex-1 py-3"
            >
              {publishing ? "Launching..." : "Launch Campaign"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

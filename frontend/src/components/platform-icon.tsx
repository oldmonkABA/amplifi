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

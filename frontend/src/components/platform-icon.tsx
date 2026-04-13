const platformLabels: Record<string, string> = {
  twitter: "X",
  linkedin: "in",
  reddit: "r/",
  blog: "Bl",
  medium: "M",
  quora: "Q",
  telegram: "Tg",
  youtube: "Yt",
  hackernews: "HN",
  producthunt: "PH",
  email: "Em",
  google_ads: "G",
  facebook_ads: "f",
};

const platformGradients: Record<string, string> = {
  twitter: "from-neutral-700 to-neutral-800",
  linkedin: "from-blue-600 to-blue-800",
  reddit: "from-orange-500 to-orange-700",
  blog: "from-violet-500 to-violet-700",
  medium: "from-neutral-600 to-neutral-800",
  quora: "from-red-600 to-red-800",
  telegram: "from-sky-400 to-sky-600",
  youtube: "from-red-500 to-red-700",
  hackernews: "from-orange-400 to-orange-600",
  producthunt: "from-orange-400 to-red-500",
  email: "from-emerald-500 to-emerald-700",
  google_ads: "from-green-500 to-blue-500",
  facebook_ads: "from-blue-500 to-blue-700",
};

export function PlatformIcon({ platform }: { platform: string }) {
  return (
    <span
      className={`inline-flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br text-[11px] font-black shadow-lg ${platformGradients[platform] ?? "from-gray-600 to-gray-800"}`}
      title={platform}
    >
      {platformLabels[platform] ?? platform.slice(0, 2).toUpperCase()}
    </span>
  );
}

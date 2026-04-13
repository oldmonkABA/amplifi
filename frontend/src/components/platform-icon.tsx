const platformLabels: Record<string, string> = {
  twitter: "X", linkedin: "in", reddit: "r/", blog: "Bl", medium: "M",
  quora: "Q", telegram: "Tg", youtube: "Yt", hackernews: "HN",
  producthunt: "PH", email: "Em", google_ads: "G", facebook_ads: "f",
};

const platformColors: Record<string, string> = {
  twitter: "#1d9bf0", linkedin: "#0a66c2", reddit: "#ff4500", blog: "#8b5cf6",
  medium: "#888", quora: "#b92b27", telegram: "#26a5e4", youtube: "#ff0000",
  hackernews: "#ff6600", producthunt: "#da552f", email: "#10b981",
  google_ads: "#4285f4", facebook_ads: "#1877f2",
};

export function PlatformIcon({ platform }: { platform: string }) {
  const color = platformColors[platform] ?? "#5a6580";
  return (
    <span
      className="inline-flex items-center justify-center w-8 h-8 rounded-lg text-[11px] font-bold"
      style={{ background: color + "1a", color }}
      title={platform}
    >
      {platformLabels[platform] ?? platform.slice(0, 2).toUpperCase()}
    </span>
  );
}

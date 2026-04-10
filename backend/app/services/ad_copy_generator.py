import json
import re


AD_PLATFORM_CONFIGS = {
    "google_ads": {
        "headline_max": 30,
        "description_max": 90,
        "num_headlines": 3,
        "num_descriptions": 2,
        "system_prompt": (
            "You are a Google Ads copywriter. Write compelling search ad copy. "
            "Headlines must be under 30 characters each. Descriptions under 90 characters. "
            "Focus on strong CTAs, unique value propositions, and keyword relevance. "
            "Return ONLY a JSON array — no markdown fences, no commentary."
        ),
    },
    "facebook_ads": {
        "headline_max": 40,
        "description_max": 125,
        "num_headlines": 1,
        "num_descriptions": 1,
        "system_prompt": (
            "You are a Facebook Ads copywriter. Write scroll-stopping ad copy. "
            "Headlines must be under 40 characters. Descriptions under 125 characters. "
            "Focus on emotional hooks, social proof, and clear CTAs. "
            "Return ONLY a JSON array — no markdown fences, no commentary."
        ),
    },
}


class AdCopyGenerator:
    """Generates platform-specific ad copy using LLM."""

    def __init__(self, llm):
        self.llm = llm

    async def generate(
        self,
        platform: str,
        topic: str,
        num_variants: int = 3,
        site_context: dict | None = None,
        tone: str = "professional",
        keywords: list[str] | None = None,
    ) -> list[dict]:
        config = AD_PLATFORM_CONFIGS.get(platform)
        if not config:
            raise ValueError(f"Unsupported ad platform: {platform}")

        prompt = self._build_prompt(
            platform=platform,
            topic=topic,
            num_variants=num_variants,
            site_context=site_context or {},
            tone=tone,
            keywords=keywords or [],
            config=config,
        )

        response = await self.llm.generate(prompt=prompt)
        return self._parse_response(response)

    def _build_prompt(
        self,
        platform: str,
        topic: str,
        num_variants: int,
        site_context: dict,
        tone: str,
        keywords: list[str],
        config: dict,
    ) -> str:
        parts = [config["system_prompt"], ""]

        if site_context:
            context_str = ", ".join(f"{k}: {v}" for k, v in site_context.items())
            parts.append(f"Product context: {context_str}")

        parts.append(f"Platform: {platform}")
        parts.append(f"Topic: {topic}")
        parts.append(f"Tone: {tone}")
        parts.append(f"Headline max length: {config['headline_max']} characters")
        parts.append(f"Description max length: {config['description_max']} characters")

        if keywords:
            parts.append(f"Target keywords: {', '.join(keywords)}")

        fields = ["headline", "description"]
        if config["num_headlines"] > 1:
            fields.extend(f"headline_{i}" for i in range(2, config["num_headlines"] + 1))
        if config["num_descriptions"] > 1:
            fields.extend(f"description_{i}" for i in range(2, config["num_descriptions"] + 1))

        parts.append("")
        parts.append(
            f"Generate exactly {num_variants} ad variant(s) as a JSON array. "
            f"Each object must have these keys: {', '.join(fields)}. "
            f"Return ONLY the JSON array, no other text."
        )

        return "\n".join(parts)

    def _parse_response(self, response: str) -> list[dict]:
        text = response.strip()
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
        if match:
            text = match.group(1).strip()
        return json.loads(text)

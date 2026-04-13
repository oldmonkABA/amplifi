from openai import AsyncOpenAI


class ImageGenerator:
    """Generates ad images using OpenAI DALL-E."""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        n: int = 1,
    ) -> list[str]:
        """Generate images and return list of URLs."""
        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            n=n,
            quality="standard",
        )
        return [img.url for img in response.data]

    @staticmethod
    def build_ad_image_prompt(
        topic: str,
        platform: str,
        site_name: str,
        tone: str = "professional",
    ) -> str:
        """Build a DALL-E prompt for an ad image."""
        style_map = {
            "professional": "clean, corporate, modern design with subtle gradients",
            "casual": "friendly, warm, approachable lifestyle imagery",
            "persuasive": "bold, high-contrast, attention-grabbing design",
            "informative": "clean infographic style with data visualization elements",
            "friendly": "warm colors, inviting, people-focused imagery",
        }
        style = style_map.get(tone, style_map["professional"])

        return (
            f"Create a professional digital advertisement image for {site_name}. "
            f"Topic: {topic}. "
            f"Style: {style}. "
            f"The image should be suitable for {platform} ads. "
            f"No text or words in the image — just visual design, imagery, and graphics. "
            f"High quality, photorealistic or polished illustration style. "
            f"Finance and investment themed with modern aesthetics."
        )

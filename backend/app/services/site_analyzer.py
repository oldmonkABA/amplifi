import json
import re
from html.parser import HTMLParser


class _TextExtractor(HTMLParser):
    """Extract visible text from HTML, ignoring script/style tags."""

    def __init__(self):
        super().__init__()
        self.text_parts: list[str] = []
        self._skip = False
        self._skip_tags = {"script", "style", "noscript"}

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self._skip_tags:
            self._skip = True

    def handle_endtag(self, tag):
        if tag.lower() in self._skip_tags:
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text:
                self.text_parts.append(text)

    def get_text(self) -> str:
        return "\n".join(self.text_parts)


class _MetadataExtractor(HTMLParser):
    """Extract metadata from HTML head tags."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self._in_title = False
        self.meta_description = ""
        self.meta_keywords = ""
        self.og_title = ""
        self.og_description = ""

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self._in_title = True
        elif tag.lower() == "meta":
            attrs_dict = dict(attrs)
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")

            if name == "description":
                self.meta_description = content
            elif name == "keywords":
                self.meta_keywords = content
            elif prop == "og:title":
                self.og_title = content
            elif prop == "og:description":
                self.og_description = content

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


class SiteAnalyzer:
    """Analyzes website content using LLM to extract product/niche information."""

    def __init__(self, llm):
        self.llm = llm

    def _extract_text(self, html: str) -> str:
        extractor = _TextExtractor()
        extractor.feed(html)
        return extractor.get_text()

    def extract_metadata(self, html: str) -> dict:
        extractor = _MetadataExtractor()
        extractor.feed(html)
        keywords = [
            k.strip()
            for k in extractor.meta_keywords.split(",")
            if k.strip()
        ]
        return {
            "title": extractor.title.strip(),
            "meta_description": extractor.meta_description,
            "meta_keywords": keywords,
            "og_title": extractor.og_title,
            "og_description": extractor.og_description,
        }

    async def analyze_html(self, html: str, url: str) -> dict:
        text_content = self._extract_text(html)
        metadata = self.extract_metadata(html)

        # Truncate to avoid token limits
        max_chars = 4000
        if len(text_content) > max_chars:
            text_content = text_content[:max_chars] + "..."

        prompt = f"""Analyze this website and return a JSON object with the following fields:
- product_name: the name of the product or company
- description: a one-sentence description
- niche: the market niche (e.g., "marketing_technology", "finance", "health")
- key_features: list of main features (up to 5)
- target_audience: who this product is for
- competitors: list of likely competitors (up to 5)
- tone: the brand tone (e.g., "professional", "casual", "technical")
- unique_selling_points: what makes this product different (up to 3)

URL: {url}
Page title: {metadata.get('title', 'N/A')}
Meta description: {metadata.get('meta_description', 'N/A')}

Page content:
{text_content}

Return ONLY valid JSON, no markdown fences or explanation."""

        response = await self.llm.generate(prompt=prompt)

        try:
            # Try to extract JSON from the response
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
                cleaned = re.sub(r"\s*```$", "", cleaned)
            return json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            return {"raw_response": response, "error": "Failed to parse LLM response as JSON"}

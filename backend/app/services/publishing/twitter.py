import httpx

from app.services.publishing.base import PlatformPublisher, PublishResult


TWITTER_API_BASE = "https://api.twitter.com/2"


class TwitterPublisher(PlatformPublisher):
    """Publisher for Twitter/X using the v2 API."""

    platform = "twitter"

    def _build_auth_header(self) -> str:
        bearer = self.credentials.get("bearer_token")
        if bearer:
            return f"Bearer {bearer}"
        # Fallback: could implement OAuth 1.0a signing here
        return f"Bearer {self.credentials.get('api_key', '')}"

    async def publish(
        self, content_body: str, title: str | None = None, **kwargs
    ) -> PublishResult:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{TWITTER_API_BASE}/tweets",
                    headers={
                        "Authorization": self._build_auth_header(),
                        "Content-Type": "application/json",
                    },
                    json={"text": content_body},
                )

            if response.status_code == 201:
                data = response.json().get("data", {})
                tweet_id = data.get("id", "")
                return PublishResult(
                    success=True,
                    platform="twitter",
                    post_id=tweet_id,
                    url=f"https://twitter.com/i/status/{tweet_id}",
                    raw_response=response.json(),
                )
            else:
                return PublishResult(
                    success=False,
                    platform="twitter",
                    error=f"Twitter API error {response.status_code}: {response.text}",
                )
        except Exception as e:
            return PublishResult(
                success=False,
                platform="twitter",
                error=str(e),
            )

    async def delete(self, post_id: str) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{TWITTER_API_BASE}/tweets/{post_id}",
                    headers={
                        "Authorization": self._build_auth_header(),
                        "Content-Type": "application/json",
                    },
                )
            return response.status_code == 200
        except Exception:
            return False

    async def validate_credentials(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{TWITTER_API_BASE}/users/me",
                    headers={"Authorization": self._build_auth_header()},
                )
            return response.status_code == 200
        except Exception:
            return False

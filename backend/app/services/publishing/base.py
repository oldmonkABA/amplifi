from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class PublishResult:
    success: bool
    platform: str
    post_id: str | None = None
    url: str | None = None
    error: str | None = None
    raw_response: dict | None = field(default=None, repr=False)


class PlatformPublisher(ABC):
    """Abstract base class for platform publishers."""

    platform: str = ""

    def __init__(self, credentials: dict):
        self.credentials = credentials

    @abstractmethod
    async def publish(
        self, content_body: str, title: str | None = None, **kwargs
    ) -> PublishResult:
        """Publish content to the platform. Returns a PublishResult."""
        ...

    @abstractmethod
    async def delete(self, post_id: str) -> bool:
        """Delete a published post. Returns True if successful."""
        ...

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Check if the stored credentials are valid."""
        ...

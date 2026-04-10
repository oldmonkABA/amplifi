from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class AdPlatformResult:
    success: bool
    platform: str
    ad_id: str | None = None
    error: str | None = None
    raw_response: dict | None = field(default=None, repr=False)


class AdPlatformManager(ABC):
    """Abstract base class for ad platform managers."""

    platform: str = ""

    def __init__(self, credentials: dict):
        self.credentials = credentials

    @abstractmethod
    async def create_ad(
        self, headline: str, description: str, final_url: str, **kwargs
    ) -> AdPlatformResult:
        ...

    @abstractmethod
    async def pause_ad(self, ad_id: str) -> AdPlatformResult:
        ...

    @abstractmethod
    async def resume_ad(self, ad_id: str) -> AdPlatformResult:
        ...

    @abstractmethod
    async def delete_ad(self, ad_id: str) -> bool:
        ...

    @abstractmethod
    async def validate_credentials(self) -> bool:
        ...

from app.services.ad_platforms.base import AdPlatformManager


class AdPlatformFactory:
    """Registry and factory for ad platform managers."""

    def __init__(self):
        self._registry: dict[str, type[AdPlatformManager]] = {}

    def register(self, platform: str, manager_class: type[AdPlatformManager]):
        self._registry[platform] = manager_class

    def create(self, platform: str, credentials: dict) -> AdPlatformManager:
        manager_class = self._registry.get(platform)
        if not manager_class:
            raise ValueError(
                f"No ad platform manager registered for '{platform}'. "
                f"Available: {', '.join(self._registry.keys())}"
            )
        return manager_class(credentials=credentials)

    def list_platforms(self) -> list[str]:
        return list(self._registry.keys())

from app.services.publishing.base import PlatformPublisher


class PublisherFactory:
    """Registry and factory for platform publishers."""

    def __init__(self):
        self._registry: dict[str, type[PlatformPublisher]] = {}

    def register(self, platform: str, publisher_class: type[PlatformPublisher]):
        self._registry[platform] = publisher_class

    def create(self, platform: str, credentials: dict) -> PlatformPublisher:
        publisher_class = self._registry.get(platform)
        if not publisher_class:
            raise ValueError(
                f"No publisher registered for platform '{platform}'. "
                f"Available: {', '.join(self._registry.keys())}"
            )
        return publisher_class(credentials=credentials)

    def list_platforms(self) -> list[str]:
        return list(self._registry.keys())

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Content
from app.services.publishing.base import PlatformPublisher
from app.services.publishing.factory import PublisherFactory


async def find_due_content(db: AsyncSession) -> list[Content]:
    """Find all content that is scheduled and due for publishing."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Content)
        .where(Content.status == "scheduled")
        .where(Content.scheduled_at <= now)
        .order_by(Content.scheduled_at.asc())
    )
    return list(result.scalars().all())


async def publish_content_item(
    db: AsyncSession,
    content: Content,
    publisher: PlatformPublisher,
) -> bool:
    """Publish a single content item using the provided publisher.

    Returns True if published successfully, False otherwise.
    On success, updates the content status to 'published' and records the post ID.
    On failure, the content remains 'scheduled' for retry.
    """
    result = await publisher.publish(
        content_body=content.body,
        title=content.title,
    )

    if result.success:
        content.status = "published"
        content.published_at = datetime.now(timezone.utc)
        content.platform_post_id = result.post_id
        await db.commit()
        return True
    else:
        # Leave as scheduled for retry; could store error in meta_data
        if content.meta_data is None:
            content.meta_data = {}
        content.meta_data["last_publish_error"] = result.error
        await db.commit()
        return False


async def process_scheduled_content(
    db: AsyncSession,
    publisher_factory: PublisherFactory,
    credentials_by_platform: dict[str, dict] | None = None,
) -> dict:
    """Process all due scheduled content.

    Returns a summary dict with processed, succeeded, and failed counts.
    """
    credentials_by_platform = credentials_by_platform or {}
    due_items = await find_due_content(db)

    succeeded = 0
    failed = 0

    for content in due_items:
        try:
            creds = credentials_by_platform.get(content.platform, {})
            publisher = publisher_factory.create(content.platform, credentials=creds)
            result = await publish_content_item(db, content, publisher)
            if result:
                succeeded += 1
            else:
                failed += 1
        except ValueError:
            # No publisher registered for this platform
            failed += 1
            if content.meta_data is None:
                content.meta_data = {}
            content.meta_data["last_publish_error"] = (
                f"No publisher available for platform '{content.platform}'"
            )
            await db.commit()

    return {
        "processed": len(due_items),
        "succeeded": succeeded,
        "failed": failed,
    }

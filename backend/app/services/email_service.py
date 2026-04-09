import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscriber import Subscriber
from app.models.email_campaign import EmailCampaign


class EmailService:
    """Service for managing email subscribers and campaigns."""

    def __init__(self, llm=None):
        self.llm = llm

    async def add_subscriber(
        self,
        db: AsyncSession,
        site_id: uuid.UUID,
        email: str,
        source: str | None = None,
        tags: list[str] | None = None,
    ) -> Subscriber:
        """Add a subscriber. If already exists for this site, return existing."""
        result = await db.execute(
            select(Subscriber).where(
                Subscriber.site_id == site_id,
                Subscriber.email == email,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        subscriber = Subscriber(
            site_id=site_id,
            email=email,
            source=source,
            is_active=True,
            drip_status="not_started",
            tags=tags,
        )
        db.add(subscriber)
        await db.commit()
        await db.refresh(subscriber)
        return subscriber

    async def unsubscribe(
        self,
        db: AsyncSession,
        site_id: uuid.UUID,
        email: str,
        reason: str | None = None,
    ) -> bool:
        """Unsubscribe an email. Returns True if found and unsubscribed."""
        result = await db.execute(
            select(Subscriber).where(
                Subscriber.site_id == site_id,
                Subscriber.email == email,
            )
        )
        subscriber = result.scalar_one_or_none()
        if not subscriber:
            return False

        subscriber.is_active = False
        subscriber.unsubscribe_reason = reason
        await db.commit()
        return True

    async def list_subscribers(
        self,
        db: AsyncSession,
        site_id: uuid.UUID,
        active_only: bool = True,
        tags: list[str] | None = None,
    ) -> list[Subscriber]:
        """List subscribers for a site, optionally filtering by active status."""
        query = select(Subscriber).where(Subscriber.site_id == site_id)
        if active_only:
            query = query.where(Subscriber.is_active == True)  # noqa: E712
        query = query.order_by(Subscriber.created_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_subscriber_count(
        self,
        db: AsyncSession,
        site_id: uuid.UUID,
        active_only: bool = True,
    ) -> int:
        """Get the count of subscribers for a site."""
        query = select(func.count()).select_from(Subscriber).where(
            Subscriber.site_id == site_id
        )
        if active_only:
            query = query.where(Subscriber.is_active == True)  # noqa: E712
        result = await db.execute(query)
        return result.scalar()

    async def create_campaign(
        self,
        db: AsyncSession,
        site_id: uuid.UUID,
        user_id: uuid.UUID,
        subject: str,
        body: str,
        campaign_type: str,
        audience_segment: dict | None = None,
    ) -> EmailCampaign:
        """Create a new email campaign as draft."""
        campaign = EmailCampaign(
            site_id=site_id,
            user_id=user_id,
            subject=subject,
            body=body,
            campaign_type=campaign_type,
            status="draft",
            audience_segment=audience_segment,
        )
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)
        return campaign

    async def generate_campaign_content(
        self,
        topic: str,
        site_name: str,
        tone: str = "professional",
    ) -> dict:
        """Generate email campaign content using LLM.

        Returns a dict with 'subject' and 'body' keys.
        """
        if not self.llm:
            raise ValueError("LLM is required for content generation")

        prompt = f"""You are an email marketing expert writing for {site_name}.

Topic: {topic}
Tone: {tone}

Write an email newsletter with:
1. First line should be the subject line, prefixed with "Subject: "
2. Then the HTML email body

Keep the email concise, engaging, and mobile-friendly.
Include a clear call to action.
Use HTML formatting (<h1>, <p>, <ol>, <li>, etc.)."""

        response = await self.llm.generate(prompt=prompt)

        lines = response.strip().split("\n", 1)
        subject = lines[0]
        body = lines[1].strip() if len(lines) > 1 else response

        # Clean up subject line
        if subject.lower().startswith("subject:"):
            subject = subject[8:].strip()

        return {"subject": subject, "body": body}

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.content import Content, ContentGroup
from app.models.site import Site
from app.modules.auth.dependencies import get_current_user
from app.modules.content.schemas import (
    ContentCreateRequest,
    ContentUpdateRequest,
    ContentResponse,
    ContentListResponse,
    ContentGroupCreateRequest,
    ContentGroupResponse,
    ContentGenerateRequest,
)
from app.services.content_generator import ContentGenerator
from app.services.llm.factory import create_llm_factory

router = APIRouter(prefix="/api/content", tags=["content"])


@router.post("/", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    request: ContentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    content = Content(
        site_id=uuid.UUID(request.site_id),
        user_id=current_user.id,
        platform=request.platform,
        content_type=request.content_type,
        title=request.title,
        body=request.body,
        status=request.status,
        group_id=uuid.UUID(request.group_id) if request.group_id else None,
        scheduled_at=request.scheduled_at,
        target_timezone=request.target_timezone,
        meta_data=request.meta_data,
    )
    db.add(content)
    await db.commit()
    await db.refresh(content)
    return _content_to_response(content)


@router.get("/", response_model=ContentListResponse)
async def list_content(
    site_id: str = Query(...),
    platform: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = select(Content).where(Content.site_id == uuid.UUID(site_id))

    if platform:
        query = query.where(Content.platform == platform)
    if status_filter:
        query = query.where(Content.status == status_filter)

    # Get total count
    count_query = select(func.count()).select_from(
        query.subquery()
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(Content.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    items = result.scalars().all()

    return ContentListResponse(
        items=[_content_to_response(c) for c in items],
        total=total,
    )


@router.post("/generate", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def generate_content(
    request: ContentGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Fetch site for context
    site_result = await db.execute(
        select(Site).where(Site.id == uuid.UUID(request.site_id))
    )
    site = site_result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Build site context for the generator
    site_context = {
        "product_name": site.name,
        "url": site.url,
    }
    if site.description:
        site_context["description"] = site.description
    if site.niche:
        site_context["niche"] = site.niche

    # Create LLM and generate content
    factory = create_llm_factory()
    llm = factory.get(
        current_user.default_llm_provider,
        api_key=current_user.openai_api_key,
    )
    generator = ContentGenerator(llm=llm)

    generated = await generator.generate(
        platform=request.platform,
        content_type=request.content_type,
        topic=request.topic,
        site_context=site_context,
        tone=request.tone,
        keywords=request.keywords,
        additional_context=request.additional_context,
    )

    # Save as draft
    content = Content(
        site_id=uuid.UUID(request.site_id),
        user_id=current_user.id,
        platform=generated["platform"],
        content_type=generated["content_type"],
        title=generated["title"],
        body=generated["body"],
        status="draft",
    )
    db.add(content)
    await db.commit()
    await db.refresh(content)
    return _content_to_response(content)


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    content = await _get_content_or_404(db, content_id)
    return _content_to_response(content)


@router.patch("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: str,
    request: ContentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    content = await _get_content_or_404(db, content_id)

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)

    await db.commit()
    await db.refresh(content)
    return _content_to_response(content)


@router.post("/{content_id}/approve", response_model=ContentResponse)
async def approve_content(
    content_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    content = await _get_content_or_404(db, content_id)
    content.status = "approved"
    await db.commit()
    await db.refresh(content)
    return _content_to_response(content)


@router.post("/{content_id}/reject", response_model=ContentResponse)
async def reject_content(
    content_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    content = await _get_content_or_404(db, content_id)
    content.status = "rejected"
    await db.commit()
    await db.refresh(content)
    return _content_to_response(content)


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    content = await _get_content_or_404(db, content_id)
    await db.delete(content)
    await db.commit()


@router.post("/groups/", response_model=ContentGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_content_group(
    request: ContentGroupCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    group = ContentGroup(
        site_id=uuid.UUID(request.site_id),
        name=request.name,
        description=request.description,
    )
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return ContentGroupResponse(
        id=str(group.id),
        site_id=str(group.site_id),
        name=group.name,
        description=group.description,
        created_at=group.created_at,
        updated_at=group.updated_at,
    )


async def _get_content_or_404(db: AsyncSession, content_id: str) -> Content:
    result = await db.execute(
        select(Content).where(Content.id == uuid.UUID(content_id))
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


def _content_to_response(content: Content) -> ContentResponse:
    return ContentResponse(
        id=str(content.id),
        site_id=str(content.site_id),
        user_id=str(content.user_id),
        platform=content.platform,
        content_type=content.content_type,
        title=content.title,
        body=content.body,
        status=content.status,
        group_id=str(content.group_id) if content.group_id else None,
        scheduled_at=content.scheduled_at,
        published_at=content.published_at,
        target_timezone=content.target_timezone,
        platform_post_id=content.platform_post_id,
        meta_data=content.meta_data,
        created_at=content.created_at,
        updated_at=content.updated_at,
    )

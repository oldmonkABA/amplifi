import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.ad import AdCampaign, Ad
from app.models.site import Site
from app.modules.auth.dependencies import get_current_user
from app.modules.ads.schemas import (
    CampaignCreateRequest,
    CampaignUpdateRequest,
    CampaignResponse,
    CampaignListResponse,
    AdCreateRequest,
    AdUpdateRequest,
    AdResponse,
    AdListResponse,
    AdGenerateRequest,
    AdGenerateResponse,
)
from app.services.ad_copy_generator import AdCopyGenerator
from app.services.llm.factory import create_llm_factory

router = APIRouter(prefix="/api/ads", tags=["ads"])


# ── Campaign endpoints ──────────────────────────────────────────────

@router.post("/campaigns/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    request: CampaignCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    campaign = await _create_campaign_in_db(
        db=db,
        site_id=request.site_id,
        user_id=current_user.id,
        name=request.name,
        platform=request.platform,
        objective=request.objective,
        daily_budget_cents=request.daily_budget_cents,
        status=request.status,
        targeting=request.targeting,
        meta_data=request.meta_data,
    )
    return _campaign_to_response(campaign)


@router.get("/campaigns/", response_model=CampaignListResponse)
async def list_campaigns(
    site_id: str = Query(...),
    platform: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = select(AdCampaign).where(AdCampaign.site_id == uuid.UUID(site_id))

    if platform:
        query = query.where(AdCampaign.platform == platform)
    if status_filter:
        query = query.where(AdCampaign.status == status_filter)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(AdCampaign.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    items = result.scalars().all()

    return CampaignListResponse(
        items=[_campaign_to_response(c) for c in items],
        total=total,
    )


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    campaign = await _get_campaign_or_404(db, campaign_id)
    return _campaign_to_response(campaign)


@router.patch("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    request: CampaignUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    campaign = await _get_campaign_or_404(db, campaign_id)
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    await db.commit()
    await db.refresh(campaign)
    return _campaign_to_response(campaign)


@router.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    campaign = await _get_campaign_or_404(db, campaign_id)
    await db.delete(campaign)
    await db.commit()


# ── Ad endpoints ─────────────────────────────────────────────────────

@router.post("/ads/", response_model=AdResponse, status_code=status.HTTP_201_CREATED)
async def create_ad(
    request: AdCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ad = await _create_ad_in_db(
        db=db,
        campaign_id=request.campaign_id,
        headline=request.headline,
        headline_2=request.headline_2,
        headline_3=request.headline_3,
        description=request.description,
        description_2=request.description_2,
        display_url=request.display_url,
        final_url=request.final_url,
        image_url=request.image_url,
        status=request.status,
        meta_data=request.meta_data,
    )
    return _ad_to_response(ad)


@router.get("/ads/", response_model=AdListResponse)
async def list_ads(
    campaign_id: str = Query(...),
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = select(Ad).where(Ad.campaign_id == uuid.UUID(campaign_id))

    if status_filter:
        query = query.where(Ad.status == status_filter)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(Ad.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    items = result.scalars().all()

    return AdListResponse(
        items=[_ad_to_response(a) for a in items],
        total=total,
    )


@router.get("/ads/{ad_id}", response_model=AdResponse)
async def get_ad(
    ad_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ad = await _get_ad_or_404(db, ad_id)
    return _ad_to_response(ad)


@router.patch("/ads/{ad_id}", response_model=AdResponse)
async def update_ad(
    ad_id: str,
    request: AdUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ad = await _get_ad_or_404(db, ad_id)
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ad, field, value)
    await db.commit()
    await db.refresh(ad)
    return _ad_to_response(ad)


@router.delete("/ads/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad_endpoint(
    ad_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ad = await _get_ad_or_404(db, ad_id)
    await db.delete(ad)
    await db.commit()


# ── Ad generation endpoint ───────────────────────────────────────────

@router.post("/generate", response_model=AdGenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate_ads(
    request: AdGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Verify site exists
    site_result = await db.execute(
        select(Site).where(Site.id == uuid.UUID(request.site_id))
    )
    site = site_result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Verify campaign exists
    await _get_campaign_or_404(db, request.campaign_id)

    site_context = {"product_name": site.name, "url": site.url}
    if site.description:
        site_context["description"] = site.description
    if site.niche:
        site_context["niche"] = site.niche

    factory = create_llm_factory()
    llm = factory.get(
        current_user.default_llm_provider,
        api_key=current_user.openai_api_key,
    )
    generator = AdCopyGenerator(llm=llm)

    variants = await generator.generate(
        platform=request.platform,
        topic=request.topic,
        num_variants=request.num_variants,
        site_context=site_context,
        tone=request.tone,
        keywords=request.keywords,
    )

    # Save each variant as a draft ad
    ads = []
    for v in variants:
        ad = Ad(
            campaign_id=uuid.UUID(request.campaign_id),
            headline=v.get("headline", ""),
            headline_2=v.get("headline_2"),
            headline_3=v.get("headline_3"),
            description=v.get("description", ""),
            description_2=v.get("description_2"),
            final_url=site.url,
            status="draft",
        )
        db.add(ad)
        ads.append(ad)

    await db.commit()
    for ad in ads:
        await db.refresh(ad)

    return AdGenerateResponse(ads=[_ad_to_response(a) for a in ads])


# ── Helpers ──────────────────────────────────────────────────────────

async def _create_campaign_in_db(
    db: AsyncSession,
    site_id: str,
    user_id: uuid.UUID,
    name: str,
    platform: str,
    objective: str,
    daily_budget_cents: int,
    status: str,
    targeting: dict | None = None,
    meta_data: dict | None = None,
) -> AdCampaign:
    campaign = AdCampaign(
        site_id=uuid.UUID(site_id),
        user_id=user_id,
        name=name,
        platform=platform,
        objective=objective,
        daily_budget_cents=daily_budget_cents,
        status=status,
        targeting=targeting,
        meta_data=meta_data,
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


async def _create_ad_in_db(
    db: AsyncSession,
    campaign_id: str,
    headline: str,
    description: str,
    final_url: str,
    status: str = "draft",
    headline_2: str | None = None,
    headline_3: str | None = None,
    description_2: str | None = None,
    display_url: str | None = None,
    image_url: str | None = None,
    meta_data: dict | None = None,
) -> Ad:
    ad = Ad(
        campaign_id=uuid.UUID(campaign_id),
        headline=headline,
        headline_2=headline_2,
        headline_3=headline_3,
        description=description,
        description_2=description_2,
        display_url=display_url,
        final_url=final_url,
        image_url=image_url,
        status=status,
        meta_data=meta_data,
    )
    db.add(ad)
    await db.commit()
    await db.refresh(ad)
    return ad


async def _get_campaign_or_404(db: AsyncSession, campaign_id: str) -> AdCampaign:
    result = await db.execute(
        select(AdCampaign).where(AdCampaign.id == uuid.UUID(campaign_id))
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


async def _get_ad_or_404(db: AsyncSession, ad_id: str) -> Ad:
    result = await db.execute(
        select(Ad).where(Ad.id == uuid.UUID(ad_id))
    )
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad


def _campaign_to_response(campaign: AdCampaign) -> CampaignResponse:
    return CampaignResponse(
        id=str(campaign.id),
        site_id=str(campaign.site_id),
        user_id=str(campaign.user_id),
        name=campaign.name,
        platform=campaign.platform,
        objective=campaign.objective,
        daily_budget_cents=campaign.daily_budget_cents,
        status=campaign.status,
        targeting=campaign.targeting,
        meta_data=campaign.meta_data,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
    )


def _ad_to_response(ad: Ad) -> AdResponse:
    return AdResponse(
        id=str(ad.id),
        campaign_id=str(ad.campaign_id),
        headline=ad.headline,
        headline_2=ad.headline_2,
        headline_3=ad.headline_3,
        description=ad.description,
        description_2=ad.description_2,
        display_url=ad.display_url,
        final_url=ad.final_url,
        image_url=ad.image_url,
        status=ad.status,
        platform_ad_id=ad.platform_ad_id,
        meta_data=ad.meta_data,
        created_at=ad.created_at,
        updated_at=ad.updated_at,
    )

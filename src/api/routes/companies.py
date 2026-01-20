"""Company management API routes."""

from datetime import datetime

from fastapi import APIRouter, HTTPException

from src.api.schemas import CompanyCreateRequest, CompanyResponse
from src.domain import Company, CompanySize, Industry
from src.services import get_redis_client
from src.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyResponse)
async def create_company(request: CompanyCreateRequest) -> CompanyResponse:
    """Create a new company profile."""
    # Map industry
    industry_map = {
        "consulting": Industry.CONSULTING,
        "saas": Industry.SAAS,
        "light_freight": Industry.LIGHT_FREIGHT,
        "コンサルティング": Industry.CONSULTING,
        "SaaS": Industry.SAAS,
        "軽貨物運送業": Industry.LIGHT_FREIGHT,
    }
    industry = industry_map.get(request.industry.lower(), Industry.OTHER)

    # Determine size
    if request.employee_count <= 50:
        size = CompanySize.STARTUP
    elif request.employee_count <= 100:
        size = CompanySize.SMALL
    elif request.employee_count <= 300:
        size = CompanySize.MEDIUM
    else:
        size = CompanySize.LARGE

    company = Company(
        name=request.name,
        industry=industry,
        size=size,
        employee_count=request.employee_count,
        founding_year=request.founding_year,
        mission=request.mission,
        vision=request.vision,
        values=request.values,
        current_grade_count=request.current_grade_count,
        has_existing_hr_system=request.has_existing_hr_system,
        existing_system_description=request.existing_system_description,
        business_model=request.business_model,
        target_market=request.target_market,
        growth_stage=request.growth_stage,
        design_goals=request.design_goals,
        constraints=request.constraints,
    )

    # Store in Redis
    redis = await get_redis_client()
    await redis.set_json(
        f"company:{company.company_id}",
        company.model_dump(mode="json"),
        expire_seconds=86400 * 30,  # 30 days
    )

    logger.info("company_created", company_id=company.company_id, name=company.name)

    return CompanyResponse(
        company_id=company.company_id,
        name=company.name,
        industry=company.industry.value,
        size=company.size.value,
        employee_count=company.employee_count,
        created_at=company.created_at,
    )


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: str) -> CompanyResponse:
    """Get a company by ID."""
    redis = await get_redis_client()
    data = await redis.get_json(f"company:{company_id}")

    if not data:
        raise HTTPException(status_code=404, detail="Company not found")

    return CompanyResponse(
        company_id=data["company_id"],
        name=data["name"],
        industry=data["industry"],
        size=data["size"],
        employee_count=data["employee_count"],
        created_at=datetime.fromisoformat(data["created_at"]),
    )


@router.delete("/{company_id}")
async def delete_company(company_id: str) -> dict[str, str]:
    """Delete a company."""
    redis = await get_redis_client()

    if not await redis.exists(f"company:{company_id}"):
        raise HTTPException(status_code=404, detail="Company not found")

    await redis.delete(f"company:{company_id}")
    logger.info("company_deleted", company_id=company_id)

    return {"status": "deleted", "company_id": company_id}

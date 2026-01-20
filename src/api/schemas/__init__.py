"""API request and response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# Company schemas
class CompanyCreateRequest(BaseModel):
    """Request to create a company."""

    name: str
    industry: str
    employee_count: int = Field(ge=1)
    founding_year: int | None = None
    mission: str = ""
    vision: str = ""
    values: list[str] = Field(default_factory=list)
    current_grade_count: int | None = None
    has_existing_hr_system: bool = False
    existing_system_description: str = ""
    business_model: str = ""
    target_market: str = ""
    growth_stage: str = ""
    design_goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class CompanyResponse(BaseModel):
    """Company response."""

    company_id: str
    name: str
    industry: str
    size: str
    employee_count: int
    created_at: datetime


# Workflow schemas
class WorkflowStartRequest(BaseModel):
    """Request to start a policy generation workflow."""

    company_id: str


class WorkflowResponse(BaseModel):
    """Workflow status response."""

    workflow_id: str
    status: str
    progress: str
    percent: int
    current_step: str | None
    steps: list[dict[str, str]]


# HITL schemas
class HITLRequestResponse(BaseModel):
    """HITL request response."""

    request_id: str
    gate_id: str
    title: str
    description: str
    data: dict[str, Any]
    status: str
    expires_at: datetime | None
    requested_at: datetime


class HITLDecisionRequest(BaseModel):
    """Request to submit a HITL decision."""

    approved: bool
    feedback: str | None = None


class HITLDecisionResponse(BaseModel):
    """HITL decision response."""

    request_id: str
    approved: bool
    decided_at: datetime


# Policy output schemas
class PolicyOutputResponse(BaseModel):
    """Complete policy output response."""

    company_id: str
    company_name: str
    ideal_talent_profile: dict[str, Any] | None = None
    grading_system: dict[str, Any] | None = None
    evaluation_system: dict[str, Any] | None = None
    compensation_system: dict[str, Any] | None = None
    generated_at: datetime


# Health check
class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    environment: str


__all__ = [
    "CompanyCreateRequest",
    "CompanyResponse",
    "WorkflowStartRequest",
    "WorkflowResponse",
    "HITLRequestResponse",
    "HITLDecisionRequest",
    "HITLDecisionResponse",
    "PolicyOutputResponse",
    "HealthResponse",
]

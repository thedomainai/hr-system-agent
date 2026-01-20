"""
Company and Ideal Talent Profile domain models.

Defines the core company context and talent profile structures
that serve as the foundation for HR policy design.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Industry(str, Enum):
    """Supported industry types."""

    CONSULTING = "consulting"
    SAAS = "saas"
    LIGHT_FREIGHT = "light_freight"  # 軽貨物運送業
    OTHER = "other"


class CompanySize(str, Enum):
    """Company size categories."""

    STARTUP = "startup"  # 1-50
    SMALL = "small"  # 51-100
    MEDIUM = "medium"  # 101-300
    LARGE = "large"  # 301+


class CompetencyElement(BaseModel):
    """
    A single element within a competency.

    Each competency has 2 elements that define specific behaviors
    or capabilities expected from employees.
    """

    element_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    behavioral_indicators: list[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "戦略的思考",
                "description": "事業目標達成のための戦略を構築する能力",
                "behavioral_indicators": [
                    "市場動向を分析し、機会を特定できる",
                    "長期的な視点で計画を立てられる",
                ],
            }
        }


class Competency(BaseModel):
    """
    A competency required for the ideal talent profile.

    Each competency consists of 2 elements that define specific
    skills or behaviors expected from employees.
    """

    competency_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    elements: list[CompetencyElement] = Field(
        default_factory=list,
        min_length=2,
        max_length=2,
    )
    weight: float = Field(default=1.0, ge=0.0, le=1.0)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "問題解決力",
                "description": "複雑な課題を分析し、効果的な解決策を導き出す能力",
                "elements": [
                    {
                        "name": "課題分析",
                        "description": "問題の本質を見極める力",
                    },
                    {
                        "name": "解決策立案",
                        "description": "実行可能な解決策を提案する力",
                    },
                ],
                "weight": 0.33,
            }
        }


class GraduationRequirement(BaseModel):
    """
    Graduation requirements for advancing to the next grade.

    Defines the criteria employees must meet to be promoted
    from one grade to the next.
    """

    requirement_id: str = Field(default_factory=lambda: str(uuid4()))
    from_grade: str
    to_grade: str
    competency_requirements: dict[str, int] = Field(default_factory=dict)
    experience_months: int = Field(default=12)
    performance_threshold: str = Field(default="B")
    additional_criteria: list[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "from_grade": "J1",
                "to_grade": "J2",
                "competency_requirements": {
                    "問題解決力": 3,
                    "コミュニケーション力": 3,
                },
                "experience_months": 18,
                "performance_threshold": "B",
                "additional_criteria": ["担当プロジェクトを完遂している"],
            }
        }


class IdealTalentProfile(BaseModel):
    """
    Ideal Talent Profile (求める人材像).

    This is the foundational model that defines the ideal employee
    characteristics for a company. It consists of 3 competencies,
    each with 2 elements.
    """

    profile_id: str = Field(default_factory=lambda: str(uuid4()))
    company_id: str
    version: int = 1
    name: str = "求める人材像"
    vision_statement: str = ""
    competencies: list[Competency] = Field(
        default_factory=list,
        min_length=3,
        max_length=3,
    )
    graduation_requirements: list[GraduationRequirement] = Field(default_factory=list)
    approved: bool = False
    approved_at: datetime | None = None
    approved_by: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def total_elements(self) -> int:
        """Get total number of competency elements (should be 6)."""
        return sum(len(c.elements) for c in self.competencies)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "求める人材像",
                "vision_statement": "お客様の課題を自律的に解決し、持続的な価値を創造する人材",
                "competencies": [
                    {"name": "問題解決力", "elements": ["課題分析", "解決策立案"]},
                    {"name": "コミュニケーション力", "elements": ["傾聴", "説明力"]},
                    {"name": "自律性", "elements": ["主体性", "継続学習"]},
                ],
            }
        }


class Company(BaseModel):
    """
    Company profile and context for HR policy design.

    Contains all the information needed to generate
    appropriate HR policies for the organization.
    """

    company_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    industry: Industry
    size: CompanySize
    employee_count: int = Field(ge=1)
    founding_year: int | None = None

    # Company philosophy and culture
    mission: str = ""
    vision: str = ""
    values: list[str] = Field(default_factory=list)

    # Current HR state
    current_grade_count: int | None = None
    has_existing_hr_system: bool = False
    existing_system_description: str = ""

    # Business context
    business_model: str = ""
    target_market: str = ""
    growth_stage: str = ""  # startup, growth, mature, etc.

    # Specific requirements
    design_goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)

    # Reference to ideal talent profile
    ideal_talent_profile_id: str | None = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "株式会社サンプル",
                "industry": "consulting",
                "size": "small",
                "employee_count": 80,
                "mission": "クライアントの成長を支援する",
                "vision": "日本を代表するコンサルティングファーム",
                "values": ["誠実", "挑戦", "協働"],
                "design_goals": [
                    "従業員の可能性を最大化する",
                    "運用がシンプルな制度",
                ],
            }
        }

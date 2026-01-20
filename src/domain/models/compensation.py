"""
Compensation System domain models.

Defines the salary structure, benefits, and reward systems
for the HR policy system.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class SalaryType(str, Enum):
    """Types of salary components."""

    BASE = "base"  # 基本給
    GRADE = "grade"  # 等級給
    PERFORMANCE = "performance"  # 業績給
    ALLOWANCE = "allowance"  # 手当


class BonusType(str, Enum):
    """Types of bonus payments."""

    PERFORMANCE = "performance"  # 業績賞与
    PROFIT_SHARING = "profit_sharing"  # 決算賞与
    SPOT = "spot"  # スポット賞与
    SIGN_ON = "sign_on"  # 入社時賞与


class SalaryBand(BaseModel):
    """Salary range for a grade level."""

    band_id: str = Field(default_factory=lambda: str(uuid4()))
    grade_level: str
    track: str = "general"

    # Salary range (annual, in JPY)
    min_salary: int = Field(ge=0)
    mid_salary: int = Field(ge=0)
    max_salary: int = Field(ge=0)

    # Band width percentage
    @property
    def band_width(self) -> float:
        """Calculate band width as percentage."""
        if self.mid_salary == 0:
            return 0.0
        return (self.max_salary - self.min_salary) / self.mid_salary * 100

    class Config:
        json_schema_extra = {
            "example": {
                "grade_level": "S1",
                "min_salary": 5000000,
                "mid_salary": 6000000,
                "max_salary": 7200000,
            }
        }


class SalaryComponent(BaseModel):
    """A component of the salary structure."""

    component_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    salary_type: SalaryType
    description: str = ""

    # Configuration
    is_fixed: bool = True
    calculation_method: str = ""
    percentage_of_base: float | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "基本給",
                "salary_type": "base",
                "description": "等級に基づく固定給与",
                "is_fixed": True,
            }
        }


class BonusStructure(BaseModel):
    """Bonus payment structure."""

    structure_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    bonus_type: BonusType
    description: str = ""

    # Payment configuration
    frequency: str = "semi_annual"  # annual, semi_annual, quarterly
    base_months: float = Field(default=2.0)  # Number of months as base
    performance_multiplier_min: float = Field(default=0.0)
    performance_multiplier_max: float = Field(default=2.0)

    # Rating to multiplier mapping
    rating_multipliers: dict[str, float] = Field(
        default_factory=lambda: {
            "S": 1.5,
            "A": 1.2,
            "B": 1.0,
            "C": 0.8,
            "D": 0.0,
        }
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "業績賞与",
                "bonus_type": "performance",
                "frequency": "semi_annual",
                "base_months": 2.0,
            }
        }


class Allowance(BaseModel):
    """Allowance definition."""

    allowance_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str = ""
    amount: int = Field(ge=0)  # Monthly amount in JPY
    is_taxable: bool = True
    eligibility_criteria: str = ""

    class Config:
        json_schema_extra = {
            "example": {
                "name": "通勤手当",
                "description": "実費支給（上限5万円）",
                "amount": 50000,
                "is_taxable": False,
            }
        }


class CompensationSystem(BaseModel):
    """
    Complete compensation system for a company.

    Defines salary structure, bonus schemes, and allowances
    aligned with the grading and evaluation systems.
    """

    system_id: str = Field(default_factory=lambda: str(uuid4()))
    company_id: str
    version: int = 1
    name: str = "報酬制度"

    # Salary structure
    salary_bands: list[SalaryBand] = Field(default_factory=list)
    salary_components: list[SalaryComponent] = Field(default_factory=list)

    # Bonus structure
    bonus_structures: list[BonusStructure] = Field(default_factory=list)
    total_bonus_months: float = Field(default=4.0)

    # Allowances
    allowances: list[Allowance] = Field(default_factory=list)

    # Salary increase policy
    annual_increase_budget_percent: float = Field(default=3.0)
    promotion_increase_percent: float = Field(default=10.0)

    # Pay philosophy
    market_position: str = "50th percentile"  # e.g., 50th, 75th percentile
    pay_for_performance_ratio: float = Field(default=0.3)  # Variable pay ratio

    # Design rationale
    design_principles: list[str] = Field(default_factory=list)
    market_data_sources: list[str] = Field(default_factory=list)

    # Approval status
    approved: bool = False
    approved_at: datetime | None = None
    approved_by: str | None = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def get_salary_band(self, grade_level: str, track: str = "general") -> SalaryBand | None:
        """Get salary band for a specific grade and track."""
        for band in self.salary_bands:
            if band.grade_level == grade_level and band.track == track:
                return band
        return None

    def calculate_total_compensation(
        self,
        base_salary: int,
        performance_rating: str = "B",
    ) -> dict[str, int]:
        """Calculate total compensation including bonuses."""
        # Calculate bonus
        total_bonus = 0
        for bonus in self.bonus_structures:
            multiplier = bonus.rating_multipliers.get(performance_rating, 1.0)
            monthly_salary = base_salary / 12
            bonus_amount = int(monthly_salary * bonus.base_months * multiplier)
            total_bonus += bonus_amount

        # Calculate allowances
        total_allowances = sum(a.amount * 12 for a in self.allowances)

        return {
            "base_salary": base_salary,
            "bonus": total_bonus,
            "allowances": total_allowances,
            "total": base_salary + total_bonus + total_allowances,
        }

    class Config:
        json_schema_extra = {
            "example": {
                "name": "報酬制度",
                "market_position": "50th percentile",
                "pay_for_performance_ratio": 0.3,
                "design_principles": [
                    "成果に応じた報酬",
                    "市場競争力のある水準",
                    "透明性のある制度",
                ],
            }
        }

"""
Evaluation System domain models.

Defines the performance evaluation structure and criteria
for the HR policy system.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EvaluationPeriod(str, Enum):
    """Evaluation cycle periods."""

    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"


class EvaluationType(str, Enum):
    """Types of evaluation."""

    COMPETENCY = "competency"  # 能力評価
    PERFORMANCE = "performance"  # 業績評価
    BEHAVIOR = "behavior"  # 行動評価
    MBO = "mbo"  # 目標管理


class RatingScale(str, Enum):
    """Standard rating scale."""

    S = "S"  # Outstanding / 卓越
    A = "A"  # Exceeds Expectations / 期待以上
    B = "B"  # Meets Expectations / 期待通り
    C = "C"  # Below Expectations / 期待以下
    D = "D"  # Unsatisfactory / 不十分


class EvaluationCriterion(BaseModel):
    """A single evaluation criterion."""

    criterion_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    evaluation_type: EvaluationType
    weight: float = Field(default=1.0, ge=0.0, le=1.0)

    # Linked to competency (if applicable)
    competency_id: str | None = None
    competency_element_id: str | None = None

    # Rating descriptors for each level
    rating_descriptors: dict[str, str] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "課題分析力",
                "description": "問題の本質を見極め、適切に分析する能力",
                "evaluation_type": "competency",
                "weight": 0.15,
                "rating_descriptors": {
                    "S": "複雑な課題を独自の視点で分析し、組織に新たな気づきをもたらす",
                    "A": "複雑な課題を正確に分析し、適切な解決策を導出できる",
                    "B": "標準的な課題を正確に分析できる",
                },
            }
        }


class EvaluationTemplate(BaseModel):
    """Template for evaluation forms."""

    template_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    grade_levels: list[str] = Field(default_factory=list)
    criteria: list[EvaluationCriterion] = Field(default_factory=list)
    total_weight: float = Field(default=1.0)

    def validate_weights(self) -> bool:
        """Validate that criterion weights sum to 1.0."""
        return abs(sum(c.weight for c in self.criteria) - 1.0) < 0.001


class EvaluationSystem(BaseModel):
    """
    Complete evaluation system for a company.

    Defines evaluation criteria, rating scales, and processes
    aligned with the company's competency model.
    """

    system_id: str = Field(default_factory=lambda: str(uuid4()))
    company_id: str
    version: int = 1
    name: str = "評価制度"

    # Evaluation structure
    evaluation_period: EvaluationPeriod = EvaluationPeriod.SEMI_ANNUAL
    evaluation_types: list[EvaluationType] = Field(
        default_factory=lambda: [EvaluationType.COMPETENCY, EvaluationType.PERFORMANCE]
    )

    # Rating configuration
    rating_scale: list[RatingScale] = Field(
        default_factory=lambda: list(RatingScale)
    )
    competency_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    performance_weight: float = Field(default=0.5, ge=0.0, le=1.0)

    # Evaluation templates by grade
    templates: list[EvaluationTemplate] = Field(default_factory=list)

    # Process configuration
    has_self_evaluation: bool = True
    has_peer_evaluation: bool = False
    has_360_feedback: bool = False
    calibration_required: bool = True

    # Design rationale
    design_principles: list[str] = Field(default_factory=list)
    evaluation_guidelines: str = ""

    # Approval status
    approved: bool = False
    approved_at: datetime | None = None
    approved_by: str | None = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def get_template_for_grade(self, grade_level: str) -> EvaluationTemplate | None:
        """Get the evaluation template for a specific grade."""
        for template in self.templates:
            if grade_level in template.grade_levels:
                return template
        return None

    def calculate_overall_rating(
        self,
        competency_rating: float,
        performance_rating: float,
    ) -> float:
        """Calculate overall rating from component ratings."""
        return (
            competency_rating * self.competency_weight
            + performance_rating * self.performance_weight
        )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "評価制度",
                "evaluation_period": "semi_annual",
                "competency_weight": 0.6,
                "performance_weight": 0.4,
                "design_principles": [
                    "求める人材像に基づく評価",
                    "成長を促す建設的フィードバック",
                    "公平性と透明性の確保",
                ],
            }
        }


class EvaluationResult(BaseModel):
    """Individual evaluation result."""

    result_id: str = Field(default_factory=lambda: str(uuid4()))
    employee_id: str
    evaluator_id: str
    evaluation_period_start: datetime
    evaluation_period_end: datetime
    template_id: str

    # Ratings
    criterion_ratings: dict[str, RatingScale] = Field(default_factory=dict)
    competency_rating: RatingScale | None = None
    performance_rating: RatingScale | None = None
    overall_rating: RatingScale | None = None

    # Feedback
    strengths: list[str] = Field(default_factory=list)
    areas_for_improvement: list[str] = Field(default_factory=list)
    comments: str = ""

    # Status
    is_draft: bool = True
    is_calibrated: bool = False
    submitted_at: datetime | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

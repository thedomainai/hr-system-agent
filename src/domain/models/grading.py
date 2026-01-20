"""
Grading System domain models.

Defines the grade structure and level definitions
for the HR policy system.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class GradeTrack(str, Enum):
    """Career track types."""

    MANAGEMENT = "management"  # マネジメント
    SPECIALIST = "specialist"  # スペシャリスト
    GENERAL = "general"  # 一般職


class GradeLevel(str, Enum):
    """Standard grade level identifiers."""

    # Junior levels
    J1 = "J1"
    J2 = "J2"
    J3 = "J3"

    # Senior levels
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"

    # Manager levels
    M1 = "M1"
    M2 = "M2"

    # Executive levels
    E1 = "E1"
    E2 = "E2"


class CompetencyLevel(BaseModel):
    """Expected competency level for a grade."""

    competency_id: str
    competency_name: str
    required_level: int = Field(ge=1, le=5)
    description: str = ""


class Grade(BaseModel):
    """
    A single grade in the grading system.

    Defines the expectations, responsibilities, and requirements
    for employees at this grade level.
    """

    grade_id: str = Field(default_factory=lambda: str(uuid4()))
    level: str  # e.g., "J1", "S2", "M1"
    name: str  # e.g., "ジュニアコンサルタント"
    track: GradeTrack = GradeTrack.GENERAL
    order: int = Field(ge=1)

    # Grade definition
    description: str = ""
    role_expectations: list[str] = Field(default_factory=list)
    responsibility_scope: str = ""

    # Competency requirements
    competency_levels: list[CompetencyLevel] = Field(default_factory=list)

    # Typical tenure
    min_tenure_months: int = Field(default=12)
    typical_tenure_months: int = Field(default=24)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "level": "J2",
                "name": "ジュニアコンサルタント II",
                "track": "general",
                "order": 2,
                "description": "自立して業務を遂行できるレベル",
                "role_expectations": [
                    "担当領域の業務を独力で完遂できる",
                    "後輩への基本的な指導ができる",
                ],
                "competency_levels": [
                    {"competency_name": "問題解決力", "required_level": 3},
                ],
            }
        }


class GradingSystem(BaseModel):
    """
    Complete grading system for a company.

    Defines the grade structure, tracks, and progression paths
    for employee career development.
    """

    system_id: str = Field(default_factory=lambda: str(uuid4()))
    company_id: str
    version: int = 1
    name: str = "等級制度"

    # Grade structure
    grades: list[Grade] = Field(default_factory=list)
    tracks: list[GradeTrack] = Field(default_factory=lambda: [GradeTrack.GENERAL])

    # System configuration
    has_dual_ladder: bool = False  # Management + Specialist tracks
    max_grade_level: int = Field(default=6, ge=3, le=10)

    # Design rationale
    design_principles: list[str] = Field(default_factory=list)
    industry_considerations: str = ""

    # Approval status
    approved: bool = False
    approved_at: datetime | None = None
    approved_by: str | None = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def get_grade_by_level(self, level: str) -> Grade | None:
        """Get a grade by its level identifier."""
        for grade in self.grades:
            if grade.level == level:
                return grade
        return None

    def get_grades_by_track(self, track: GradeTrack) -> list[Grade]:
        """Get all grades in a specific track."""
        return [g for g in self.grades if g.track == track]

    def get_progression_path(self, from_level: str) -> list[Grade]:
        """Get the progression path from a given grade level."""
        current_grade = self.get_grade_by_level(from_level)
        if not current_grade:
            return []

        return sorted(
            [g for g in self.grades if g.order > current_grade.order and g.track == current_grade.track],
            key=lambda g: g.order,
        )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "等級制度",
                "has_dual_ladder": True,
                "max_grade_level": 6,
                "design_principles": [
                    "能力と成果の両面で評価",
                    "明確な昇格基準",
                    "キャリアパスの可視化",
                ],
                "grades": [
                    {"level": "J1", "name": "ジュニア I"},
                    {"level": "J2", "name": "ジュニア II"},
                ],
            }
        }

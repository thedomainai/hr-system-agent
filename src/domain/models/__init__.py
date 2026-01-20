"""Domain models for HR policy design."""

from .company import (
    Company,
    CompanySize,
    Competency,
    CompetencyElement,
    GraduationRequirement,
    IdealTalentProfile,
    Industry,
)
from .compensation import (
    Allowance,
    BonusStructure,
    BonusType,
    CompensationSystem,
    SalaryBand,
    SalaryComponent,
    SalaryType,
)
from .evaluation import (
    EvaluationCriterion,
    EvaluationPeriod,
    EvaluationResult,
    EvaluationSystem,
    EvaluationTemplate,
    EvaluationType,
    RatingScale,
)
from .grading import (
    CompetencyLevel,
    Grade,
    GradeLevel,
    GradeTrack,
    GradingSystem,
)

__all__ = [
    # Company
    "Company",
    "Industry",
    "CompanySize",
    "IdealTalentProfile",
    "Competency",
    "CompetencyElement",
    "GraduationRequirement",
    # Grading
    "GradingSystem",
    "Grade",
    "GradeLevel",
    "GradeTrack",
    "CompetencyLevel",
    # Evaluation
    "EvaluationSystem",
    "EvaluationTemplate",
    "EvaluationCriterion",
    "EvaluationResult",
    "EvaluationType",
    "EvaluationPeriod",
    "RatingScale",
    # Compensation
    "CompensationSystem",
    "SalaryBand",
    "SalaryComponent",
    "SalaryType",
    "BonusStructure",
    "BonusType",
    "Allowance",
]

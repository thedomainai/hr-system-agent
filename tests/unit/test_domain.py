"""
Unit tests for domain models.

Tests validation, business logic, and serialization of domain models.
"""

import pytest
from pydantic import ValidationError

from src.domain.models.company import (
    Company,
    CompanySize,
    Competency,
    CompetencyElement,
    IdealTalentProfile,
    Industry,
)
from src.domain.models.compensation import (
    Allowance,
    BonusStructure,
    BonusType,
    CompensationSystem,
    SalaryBand,
)
from src.domain.models.evaluation import (
    EvaluationCriterion,
    EvaluationPeriod,
    EvaluationSystem,
    EvaluationType,
)
from src.domain.models.grading import (
    CompetencyLevel,
    Grade,
    GradeTrack,
    GradingSystem,
)

# =============================================================================
# Company Model Tests
# =============================================================================


class TestIndustryEnum:
    """Test Industry enum."""

    def test_valid_industries(self) -> None:
        """Test valid industry values."""
        assert Industry.CONSULTING.value == "consulting"
        assert Industry.SAAS.value == "saas"
        assert Industry.LIGHT_FREIGHT.value == "light_freight"
        assert Industry.OTHER.value == "other"

    def test_industry_from_string(self) -> None:
        """Test creating industry from string."""
        assert Industry("consulting") == Industry.CONSULTING


class TestCompanySizeEnum:
    """Test CompanySize enum."""

    def test_valid_sizes(self) -> None:
        """Test valid company size values."""
        assert CompanySize.STARTUP.value == "startup"
        assert CompanySize.SMALL.value == "small"
        assert CompanySize.MEDIUM.value == "medium"
        assert CompanySize.LARGE.value == "large"


class TestCompany:
    """Test Company model."""

    def test_create_valid_company(self) -> None:
        """Test creating a valid company."""
        company = Company(
            name="Test Company",
            industry=Industry.CONSULTING,
            size=CompanySize.SMALL,
            employee_count=50,
        )
        assert company.name == "Test Company"
        assert company.industry == Industry.CONSULTING
        assert company.size == CompanySize.SMALL
        assert company.employee_count == 50
        assert company.company_id is not None

    def test_company_with_all_fields(self) -> None:
        """Test creating company with all fields."""
        company = Company(
            name="Full Company",
            industry=Industry.SAAS,
            size=CompanySize.MEDIUM,
            employee_count=200,
            founding_year=2020,
            mission="Our mission",
            vision="Our vision",
            values=["Value1", "Value2"],
            design_goals=["Goal1", "Goal2"],
            constraints=["Constraint1"],
        )
        assert company.mission == "Our mission"
        assert company.values == ["Value1", "Value2"]

    def test_company_requires_positive_employee_count(self) -> None:
        """Test that employee count must be positive."""
        with pytest.raises(ValidationError):
            Company(
                name="Test",
                industry=Industry.OTHER,
                size=CompanySize.STARTUP,
                employee_count=0,
            )

    def test_company_serialization(self) -> None:
        """Test company JSON serialization."""
        company = Company(
            name="Test",
            industry=Industry.CONSULTING,
            size=CompanySize.SMALL,
            employee_count=50,
        )
        data = company.model_dump(mode="json")
        assert data["name"] == "Test"
        assert data["industry"] == "consulting"
        assert "company_id" in data


class TestCompetencyElement:
    """Test CompetencyElement model."""

    def test_create_valid_element(self) -> None:
        """Test creating a valid competency element."""
        element = CompetencyElement(
            name="Analysis",
            description="Ability to analyze data",
        )
        assert element.name == "Analysis"
        assert element.element_id is not None

    def test_element_with_behavioral_indicators(self) -> None:
        """Test element with behavioral indicators."""
        element = CompetencyElement(
            name="Analysis",
            description="Analysis ability",
            behavioral_indicators=["Can identify patterns", "Makes data-driven decisions"],
        )
        assert len(element.behavioral_indicators) == 2


class TestCompetency:
    """Test Competency model."""

    def test_create_valid_competency(self) -> None:
        """Test creating a valid competency."""
        competency = Competency(
            name="Problem Solving",
            description="Ability to solve problems",
            elements=[
                CompetencyElement(name="Analysis", description="Analyze"),
                CompetencyElement(name="Solution", description="Solve"),
            ],
        )
        assert competency.name == "Problem Solving"
        assert len(competency.elements) == 2

    def test_competency_weight_bounds(self) -> None:
        """Test competency weight must be between 0 and 1."""
        # Valid weight
        competency = Competency(
            name="Test",
            description="Test",
            elements=[
                CompetencyElement(name="E1", description="D1"),
                CompetencyElement(name="E2", description="D2"),
            ],
            weight=0.5,
        )
        assert competency.weight == 0.5

        # Invalid weight (negative)
        with pytest.raises(ValidationError):
            Competency(
                name="Test",
                description="Test",
                elements=[
                    CompetencyElement(name="E1", description="D1"),
                    CompetencyElement(name="E2", description="D2"),
                ],
                weight=-0.1,
            )


class TestIdealTalentProfile:
    """Test IdealTalentProfile model."""

    def _create_competencies(self) -> list[Competency]:
        """Create 3 competencies with 2 elements each."""
        return [
            Competency(
                name=f"Competency {i}",
                description=f"Description {i}",
                elements=[
                    CompetencyElement(name=f"Element {i}A", description=f"Desc {i}A"),
                    CompetencyElement(name=f"Element {i}B", description=f"Desc {i}B"),
                ],
            )
            for i in range(1, 4)
        ]

    def test_create_valid_profile(self) -> None:
        """Test creating a valid ideal talent profile."""
        profile = IdealTalentProfile(
            company_id="test-company",
            competencies=self._create_competencies(),
        )
        assert profile.company_id == "test-company"
        assert len(profile.competencies) == 3

    def test_total_elements(self) -> None:
        """Test total_elements method."""
        profile = IdealTalentProfile(
            company_id="test-company",
            competencies=self._create_competencies(),
        )
        assert profile.total_elements() == 6


# =============================================================================
# Grading Model Tests
# =============================================================================


class TestGradeTrack:
    """Test GradeTrack enum."""

    def test_valid_tracks(self) -> None:
        """Test valid track values."""
        assert GradeTrack.MANAGEMENT.value == "management"
        assert GradeTrack.SPECIALIST.value == "specialist"
        assert GradeTrack.GENERAL.value == "general"


class TestGrade:
    """Test Grade model."""

    def test_create_valid_grade(self) -> None:
        """Test creating a valid grade."""
        grade = Grade(
            level="J1",
            name="Junior I",
            order=1,
            description="Entry level position",
        )
        assert grade.level == "J1"
        assert grade.name == "Junior I"
        assert grade.track == GradeTrack.GENERAL

    def test_grade_with_competency_levels(self) -> None:
        """Test grade with competency levels."""
        grade = Grade(
            level="S1",
            name="Senior I",
            order=3,
            competency_levels=[
                CompetencyLevel(
                    competency_id="comp-1",
                    competency_name="Problem Solving",
                    required_level=3,
                ),
            ],
        )
        assert len(grade.competency_levels) == 1
        assert grade.competency_levels[0].required_level == 3

    def test_grade_order_must_be_positive(self) -> None:
        """Test that grade order must be >= 1."""
        with pytest.raises(ValidationError):
            Grade(level="J1", name="Junior", order=0)


class TestCompetencyLevel:
    """Test CompetencyLevel model."""

    def test_valid_required_level(self) -> None:
        """Test valid required level values (1-5)."""
        for level in range(1, 6):
            cl = CompetencyLevel(
                competency_id="test",
                competency_name="Test",
                required_level=level,
            )
            assert cl.required_level == level

    def test_invalid_required_level(self) -> None:
        """Test invalid required level values."""
        with pytest.raises(ValidationError):
            CompetencyLevel(
                competency_id="test",
                competency_name="Test",
                required_level=0,
            )
        with pytest.raises(ValidationError):
            CompetencyLevel(
                competency_id="test",
                competency_name="Test",
                required_level=6,
            )


class TestGradingSystem:
    """Test GradingSystem model."""

    def _create_grades(self) -> list[Grade]:
        """Create sample grades."""
        return [
            Grade(level="J1", name="Junior I", order=1),
            Grade(level="J2", name="Junior II", order=2),
            Grade(level="S1", name="Senior I", order=3),
        ]

    def test_create_valid_system(self) -> None:
        """Test creating a valid grading system."""
        system = GradingSystem(
            company_id="test-company",
            grades=self._create_grades(),
        )
        assert system.company_id == "test-company"
        assert len(system.grades) == 3

    def test_get_grade_by_level(self) -> None:
        """Test get_grade_by_level method."""
        system = GradingSystem(
            company_id="test-company",
            grades=self._create_grades(),
        )
        grade = system.get_grade_by_level("J2")
        assert grade is not None
        assert grade.name == "Junior II"

        not_found = system.get_grade_by_level("X1")
        assert not_found is None

    def test_get_grades_by_track(self) -> None:
        """Test get_grades_by_track method."""
        grades = self._create_grades()
        grades[2] = Grade(
            level="M1",
            name="Manager I",
            order=3,
            track=GradeTrack.MANAGEMENT,
        )
        system = GradingSystem(company_id="test", grades=grades)

        general_grades = system.get_grades_by_track(GradeTrack.GENERAL)
        assert len(general_grades) == 2

        management_grades = system.get_grades_by_track(GradeTrack.MANAGEMENT)
        assert len(management_grades) == 1

    def test_get_progression_path(self) -> None:
        """Test get_progression_path method."""
        system = GradingSystem(
            company_id="test-company",
            grades=self._create_grades(),
        )
        path = system.get_progression_path("J1")
        assert len(path) == 2
        assert path[0].level == "J2"
        assert path[1].level == "S1"


# =============================================================================
# Evaluation Model Tests
# =============================================================================


class TestEvaluationType:
    """Test EvaluationType enum."""

    def test_valid_types(self) -> None:
        """Test valid evaluation type values."""
        assert EvaluationType.COMPETENCY.value == "competency"
        assert EvaluationType.PERFORMANCE.value == "performance"
        assert EvaluationType.BEHAVIOR.value == "behavior"


class TestEvaluationPeriod:
    """Test EvaluationPeriod enum."""

    def test_valid_periods(self) -> None:
        """Test valid evaluation period values."""
        assert EvaluationPeriod.QUARTERLY.value == "quarterly"
        assert EvaluationPeriod.SEMI_ANNUAL.value == "semi_annual"
        assert EvaluationPeriod.ANNUAL.value == "annual"


class TestEvaluationCriterion:
    """Test EvaluationCriterion model."""

    def test_create_valid_criterion(self) -> None:
        """Test creating a valid evaluation criterion."""
        criterion = EvaluationCriterion(
            name="Problem Solving",
            description="Ability to solve problems",
            evaluation_type=EvaluationType.COMPETENCY,
            weight=0.3,
        )
        assert criterion.name == "Problem Solving"
        assert criterion.weight == 0.3

    def test_criterion_with_rating_descriptors(self) -> None:
        """Test criterion with rating descriptors."""
        criterion = EvaluationCriterion(
            name="Performance",
            description="Goal achievement",
            evaluation_type=EvaluationType.PERFORMANCE,
            weight=0.4,
            rating_descriptors={
                "S": "Exceeds expectations",
                "A": "Meets expectations",
                "B": "Needs improvement",
            },
        )
        assert len(criterion.rating_descriptors) == 3


class TestEvaluationSystem:
    """Test EvaluationSystem model."""

    def test_create_valid_system(self) -> None:
        """Test creating a valid evaluation system."""
        system = EvaluationSystem(
            company_id="test-company",
            evaluation_period=EvaluationPeriod.SEMI_ANNUAL,
            competency_weight=0.6,
            performance_weight=0.4,
        )
        assert system.company_id == "test-company"
        assert system.evaluation_period == EvaluationPeriod.SEMI_ANNUAL


# =============================================================================
# Compensation Model Tests
# =============================================================================


class TestSalaryBand:
    """Test SalaryBand model."""

    def test_create_valid_band(self) -> None:
        """Test creating a valid salary band."""
        band = SalaryBand(
            grade_level="J1",
            min_salary=3500000,
            mid_salary=4000000,
            max_salary=4500000,
        )
        assert band.grade_level == "J1"
        assert band.min_salary == 3500000

    def test_salary_band_serialization(self) -> None:
        """Test salary band JSON serialization."""
        band = SalaryBand(
            grade_level="S1",
            min_salary=5000000,
            mid_salary=6000000,
            max_salary=7000000,
        )
        data = band.model_dump()
        assert data["grade_level"] == "S1"
        assert data["min_salary"] == 5000000


class TestBonusStructure:
    """Test BonusStructure model."""

    def test_create_valid_structure(self) -> None:
        """Test creating a valid bonus structure."""
        bonus = BonusStructure(
            name="Performance Bonus",
            bonus_type=BonusType.PERFORMANCE,
            base_months=2.0,
        )
        assert bonus.name == "Performance Bonus"
        assert bonus.base_months == 2.0


class TestCompensationSystem:
    """Test CompensationSystem model."""

    def test_create_valid_system(self) -> None:
        """Test creating a valid compensation system."""
        system = CompensationSystem(
            company_id="test-company",
            salary_bands=[
                SalaryBand(
                    grade_level="J1",
                    min_salary=3500000,
                    mid_salary=4000000,
                    max_salary=4500000,
                ),
            ],
            total_bonus_months=4.0,
        )
        assert system.company_id == "test-company"
        assert len(system.salary_bands) == 1

    def test_system_with_allowances(self) -> None:
        """Test system with allowances."""
        system = CompensationSystem(
            company_id="test-company",
            allowances=[
                Allowance(
                    name="Commute",
                    amount=50000,
                    description="Commute allowance",
                ),
            ],
        )
        assert len(system.allowances) == 1
        assert system.allowances[0].amount == 50000

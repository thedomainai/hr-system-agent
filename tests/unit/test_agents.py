"""
Unit tests for agent classes.

Tests agent execution, state management, and HITL integration.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.compensation_designer import CompensationDesignerAgent
from src.agents.context_collector import ContextCollectorAgent
from src.agents.evaluation_designer import EvaluationDesignerAgent
from src.agents.grading_designer import GradingDesignerAgent
from src.core.agent_base import AgentResult, AgentState, AgentStatus, BaseAgent

# =============================================================================
# AgentResult Tests
# =============================================================================


class TestAgentResult:
    """Test AgentResult model."""

    def test_successful_result(self) -> None:
        """Test creating a successful result."""
        result = AgentResult(
            success=True,
            data={"key": "value"},
        )
        assert result.success is True
        assert result.data["key"] == "value"
        assert result.error is None

    def test_failed_result(self) -> None:
        """Test creating a failed result."""
        result = AgentResult(
            success=False,
            error="Something went wrong",
        )
        assert result.success is False
        assert result.error == "Something went wrong"

    def test_result_with_hitl(self) -> None:
        """Test result requiring HITL approval."""
        result = AgentResult(
            success=True,
            data={"generated": "content"},
            requires_hitl=True,
            hitl_gate_id="HITL-001",
        )
        assert result.requires_hitl is True
        assert result.hitl_gate_id == "HITL-001"


class TestAgentState:
    """Test AgentState model."""

    def test_default_state(self) -> None:
        """Test default agent state."""
        state = AgentState(agent_type="test")
        assert state.status == AgentStatus.IDLE
        assert state.agent_id is not None
        assert state.error is None

    def test_state_serialization(self) -> None:
        """Test state JSON serialization."""
        state = AgentState(
            agent_type="test",
            company_id="company-123",
            current_step="processing",
        )
        data = state.model_dump(mode="json")
        assert data["agent_type"] == "test"
        assert data["company_id"] == "company-123"


# =============================================================================
# BaseAgent Tests
# =============================================================================


class ConcreteTestAgent(BaseAgent):
    """Concrete implementation for testing BaseAgent."""

    agent_type = "test_agent"

    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        """Simple test execution."""
        if input_data.get("should_fail"):
            return AgentResult(success=False, error="Test failure")
        return AgentResult(success=True, data={"processed": True})


class TestBaseAgent:
    """Test BaseAgent base class."""

    @pytest.fixture
    def mock_redis(self) -> MagicMock:
        """Create mock Redis client."""
        mock = MagicMock()
        mock.set_agent_state = AsyncMock()
        mock.update_agent_heartbeat = AsyncMock()
        return mock

    @pytest.fixture
    def mock_rabbitmq(self) -> MagicMock:
        """Create mock RabbitMQ client."""
        mock = MagicMock()
        mock.publish_hitl_request = AsyncMock()
        return mock

    @pytest.fixture
    def agent(self) -> ConcreteTestAgent:
        """Create test agent instance."""
        return ConcreteTestAgent(company_id="test-company")

    def test_agent_initialization(self, agent: ConcreteTestAgent) -> None:
        """Test agent initialization."""
        assert agent.agent_type == "test_agent"
        assert agent.state.company_id == "test-company"
        assert agent.state.status == AgentStatus.IDLE

    @pytest.mark.asyncio
    async def test_agent_run_success(self, agent: ConcreteTestAgent, mock_redis: MagicMock) -> None:
        """Test successful agent execution."""
        with patch(
            "src.core.agent_base.get_redis_client",
            return_value=mock_redis,
        ):
            result = await agent.run({"test": "data"})

            assert result.success is True
            assert result.data["processed"] is True
            assert agent.state.status == AgentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_agent_run_failure(self, agent: ConcreteTestAgent, mock_redis: MagicMock) -> None:
        """Test failed agent execution."""
        with patch(
            "src.core.agent_base.get_redis_client",
            return_value=mock_redis,
        ):
            result = await agent.run({"should_fail": True})

            assert result.success is False
            assert result.error == "Test failure"
            assert agent.state.status == AgentStatus.FAILED


# =============================================================================
# ContextCollectorAgent Tests
# =============================================================================


class TestContextCollectorAgent:
    """Test ContextCollectorAgent."""

    @pytest.fixture
    def mock_services(self) -> tuple[MagicMock, MagicMock]:
        """Create mock services."""
        mock_redis = MagicMock()
        mock_redis.set_agent_state = AsyncMock()
        mock_redis.update_agent_heartbeat = AsyncMock()

        mock_rabbitmq = MagicMock()
        mock_rabbitmq.publish_hitl_request = AsyncMock()

        return mock_redis, mock_rabbitmq

    @pytest.fixture
    def agent(self) -> ContextCollectorAgent:
        """Create agent instance."""
        return ContextCollectorAgent(company_id="test-company")

    @pytest.mark.asyncio
    async def test_execute_with_valid_data(
        self,
        agent: ContextCollectorAgent,
        mock_services: tuple[MagicMock, MagicMock],
        sample_company_data: dict[str, Any],
    ) -> None:
        """Test execution with valid company data."""
        mock_redis, mock_rabbitmq = mock_services

        # Mock LLM response
        llm_response = """{
            "industry_characteristics": "Consulting industry",
            "recommended_grade_count": 6,
            "key_competencies_for_industry": ["Problem Solving", "Communication"],
            "design_considerations": ["Clear career paths"],
            "potential_challenges": ["High turnover"]
        }"""

        with (
            patch(
                "src.core.agent_base.get_redis_client",
                return_value=mock_redis,
            ),
            patch(
                "src.core.agent_base.get_rabbitmq_client",
                return_value=mock_rabbitmq,
            ),
            patch.object(agent, "call_llm", return_value=llm_response),
        ):
            result = await agent.execute(sample_company_data)

            assert result.success is True
            assert result.requires_hitl is True
            assert "company" in result.data

    @pytest.mark.asyncio
    async def test_execute_missing_required_fields(self, agent: ContextCollectorAgent) -> None:
        """Test execution with missing required fields."""
        result = await agent.execute({"name": "Test"})  # Missing industry, employee_count

        assert result.success is False
        assert "Missing required fields" in result.error


# =============================================================================
# GradingDesignerAgent Tests
# =============================================================================


class TestGradingDesignerAgent:
    """Test GradingDesignerAgent."""

    @pytest.fixture
    def mock_services(self) -> tuple[MagicMock, MagicMock]:
        """Create mock services."""
        mock_redis = MagicMock()
        mock_redis.set_agent_state = AsyncMock()
        mock_redis.update_agent_heartbeat = AsyncMock()

        mock_rabbitmq = MagicMock()
        mock_rabbitmq.publish_hitl_request = AsyncMock()

        return mock_redis, mock_rabbitmq

    @pytest.fixture
    def agent(self) -> GradingDesignerAgent:
        """Create agent instance."""
        return GradingDesignerAgent(company_id="test-company")

    @pytest.mark.asyncio
    async def test_execute_with_valid_context(
        self,
        agent: GradingDesignerAgent,
        mock_services: tuple[MagicMock, MagicMock],
        sample_company_data: dict[str, Any],
        sample_talent_profile: dict[str, Any],
    ) -> None:
        """Test execution with valid context from previous steps."""
        mock_redis, mock_rabbitmq = mock_services

        input_data = {
            "collect_context": {"company": sample_company_data},
            "generate_talent_profile": {"talent_profile": sample_talent_profile},
        }

        # Mock LLM response for grading system
        llm_response = """{
            "recommended_grade_count": 6,
            "has_dual_ladder": true,
            "design_principles": ["Clear expectations", "Fair progression"],
            "grades": [
                {
                    "level": "J1",
                    "name": "Junior I",
                    "track": "general",
                    "order": 1,
                    "description": "Entry level",
                    "role_expectations": ["Learn fundamentals"],
                    "responsibility_scope": "Individual tasks",
                    "competency_levels": [{"competency_name": "Problem Solving", "required_level": 1}],
                    "min_tenure_months": 12
                },
                {
                    "level": "J2",
                    "name": "Junior II",
                    "track": "general",
                    "order": 2,
                    "description": "Developing",
                    "role_expectations": ["Work independently"],
                    "responsibility_scope": "Small projects",
                    "competency_levels": [{"competency_name": "Problem Solving", "required_level": 2}],
                    "min_tenure_months": 18
                }
            ]
        }"""

        with (
            patch(
                "src.core.agent_base.get_redis_client",
                return_value=mock_redis,
            ),
            patch(
                "src.core.agent_base.get_rabbitmq_client",
                return_value=mock_rabbitmq,
            ),
            patch.object(agent, "call_llm", return_value=llm_response),
        ):
            result = await agent.execute(input_data)

            assert result.success is True
            assert result.requires_hitl is True
            assert "grading_system" in result.data
            assert "grades" in result.data["grading_system"]

    @pytest.mark.asyncio
    async def test_execute_missing_company_context(self, agent: GradingDesignerAgent) -> None:
        """Test execution without company context."""
        result = await agent.execute({})

        assert result.success is False
        assert "Company context not found" in result.error

    @pytest.mark.asyncio
    async def test_execute_missing_talent_profile(
        self,
        agent: GradingDesignerAgent,
        sample_company_data: dict[str, Any],
    ) -> None:
        """Test execution without talent profile."""
        input_data = {
            "collect_context": {"company": sample_company_data},
        }
        result = await agent.execute(input_data)

        assert result.success is False
        assert "Talent profile not found" in result.error

    @pytest.mark.asyncio
    async def test_default_grading_system_fallback(
        self,
        agent: GradingDesignerAgent,
        mock_services: tuple[MagicMock, MagicMock],
        sample_company_data: dict[str, Any],
        sample_talent_profile: dict[str, Any],
    ) -> None:
        """Test fallback to default grading system when LLM fails."""
        mock_redis, mock_rabbitmq = mock_services

        input_data = {
            "collect_context": {"company": sample_company_data},
            "generate_talent_profile": {"talent_profile": sample_talent_profile},
        }

        with (
            patch(
                "src.core.agent_base.get_redis_client",
                return_value=mock_redis,
            ),
            patch(
                "src.core.agent_base.get_rabbitmq_client",
                return_value=mock_rabbitmq,
            ),
        ):
            # Make LLM return invalid JSON
            with patch.object(agent, "call_llm", return_value="Invalid JSON response"):
                result = await agent.execute(input_data)

                # Should still succeed with default system
                assert result.success is True
                assert "grading_system" in result.data


# =============================================================================
# EvaluationDesignerAgent Tests
# =============================================================================


class TestEvaluationDesignerAgent:
    """Test EvaluationDesignerAgent."""

    @pytest.fixture
    def mock_services(self) -> tuple[MagicMock, MagicMock]:
        """Create mock services."""
        mock_redis = MagicMock()
        mock_redis.set_agent_state = AsyncMock()
        mock_redis.update_agent_heartbeat = AsyncMock()

        mock_rabbitmq = MagicMock()
        mock_rabbitmq.publish_hitl_request = AsyncMock()

        return mock_redis, mock_rabbitmq

    @pytest.fixture
    def agent(self) -> EvaluationDesignerAgent:
        """Create agent instance."""
        return EvaluationDesignerAgent(company_id="test-company")

    @pytest.mark.asyncio
    async def test_execute_with_valid_context(
        self,
        agent: EvaluationDesignerAgent,
        mock_services: tuple[MagicMock, MagicMock],
        sample_company_data: dict[str, Any],
        sample_talent_profile: dict[str, Any],
        sample_grading_system: dict[str, Any],
    ) -> None:
        """Test execution with valid context from previous steps."""
        mock_redis, mock_rabbitmq = mock_services

        input_data = {
            "collect_context": {"company": sample_company_data},
            "generate_talent_profile": {"talent_profile": sample_talent_profile},
            "design_grading": {"grading_system": sample_grading_system},
        }

        llm_response = """{
            "evaluation_period": "semi_annual",
            "competency_weight": 0.6,
            "performance_weight": 0.4,
            "has_self_evaluation": true,
            "calibration_required": true,
            "design_principles": ["Fair evaluation", "Growth focused"],
            "criteria": [
                {
                    "name": "Problem Solving",
                    "description": "Ability to solve problems",
                    "evaluation_type": "competency",
                    "weight": 0.3,
                    "rating_descriptors": {
                        "S": "Exceptional",
                        "A": "Exceeds expectations",
                        "B": "Meets expectations"
                    }
                }
            ]
        }"""

        with (
            patch(
                "src.core.agent_base.get_redis_client",
                return_value=mock_redis,
            ),
            patch(
                "src.core.agent_base.get_rabbitmq_client",
                return_value=mock_rabbitmq,
            ),
            patch.object(agent, "call_llm", return_value=llm_response),
        ):
            result = await agent.execute(input_data)

            assert result.success is True
            assert result.requires_hitl is True
            assert "evaluation_system" in result.data

    @pytest.mark.asyncio
    async def test_execute_missing_context(self, agent: EvaluationDesignerAgent) -> None:
        """Test execution without required context."""
        result = await agent.execute({})

        assert result.success is False
        assert "Missing required context" in result.error


# =============================================================================
# CompensationDesignerAgent Tests
# =============================================================================


class TestCompensationDesignerAgent:
    """Test CompensationDesignerAgent."""

    @pytest.fixture
    def mock_services(self) -> tuple[MagicMock, MagicMock]:
        """Create mock services."""
        mock_redis = MagicMock()
        mock_redis.set_agent_state = AsyncMock()
        mock_redis.update_agent_heartbeat = AsyncMock()

        mock_rabbitmq = MagicMock()
        mock_rabbitmq.publish_hitl_request = AsyncMock()

        return mock_redis, mock_rabbitmq

    @pytest.fixture
    def agent(self) -> CompensationDesignerAgent:
        """Create agent instance."""
        return CompensationDesignerAgent(company_id="test-company")

    @pytest.mark.asyncio
    async def test_execute_with_valid_context(
        self,
        agent: CompensationDesignerAgent,
        mock_services: tuple[MagicMock, MagicMock],
        sample_company_data: dict[str, Any],
        sample_grading_system: dict[str, Any],
        sample_evaluation_system: dict[str, Any],
    ) -> None:
        """Test execution with valid context from previous steps."""
        mock_redis, mock_rabbitmq = mock_services

        input_data = {
            "collect_context": {"company": sample_company_data},
            "design_grading": {"grading_system": sample_grading_system},
            "design_evaluation": {"evaluation_system": sample_evaluation_system},
        }

        llm_response = """{
            "market_position": "50th percentile",
            "pay_for_performance_ratio": 0.3,
            "annual_increase_budget_percent": 3.0,
            "promotion_increase_percent": 10.0,
            "design_principles": ["Competitive", "Fair"],
            "salary_bands": [
                {
                    "grade_level": "J1",
                    "min_salary": 3500000,
                    "mid_salary": 4000000,
                    "max_salary": 4500000
                }
            ],
            "bonus_months": 4.0,
            "allowances": [
                {
                    "name": "Commute",
                    "amount": 50000,
                    "description": "Commute allowance"
                }
            ]
        }"""

        with (
            patch(
                "src.core.agent_base.get_redis_client",
                return_value=mock_redis,
            ),
            patch(
                "src.core.agent_base.get_rabbitmq_client",
                return_value=mock_rabbitmq,
            ),
            patch.object(agent, "call_llm", return_value=llm_response),
        ):
            result = await agent.execute(input_data)

            assert result.success is True
            assert result.requires_hitl is True
            assert "compensation_system" in result.data

    @pytest.mark.asyncio
    async def test_execute_missing_context(self, agent: CompensationDesignerAgent) -> None:
        """Test execution without required context."""
        result = await agent.execute({})

        assert result.success is False
        assert "Missing required context" in result.error

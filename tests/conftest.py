"""
Pytest configuration and fixtures for HR System Agent tests.

Provides common fixtures for mocking external services and creating test data.
"""

import asyncio
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

# =============================================================================
# Async Event Loop
# =============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Mock Settings
# =============================================================================


@pytest.fixture
def mock_settings() -> MagicMock:
    """Create mock settings for tests."""
    settings = MagicMock()
    settings.env = "development"
    settings.app_name = "hr-system-agent"
    settings.app_version = "0.1.0"
    settings.gemini_api_key = "test-api-key"
    settings.gemini_model = "gemini-2.0-flash"
    settings.redis_url = "redis://localhost:6379/0"
    settings.rabbitmq_url = "amqp://guest:guest@localhost:5672/"
    settings.hitl_default_timeout_hours = 72
    settings.agent_heartbeat_interval_seconds = 30
    settings.is_development = True
    settings.is_production = False
    return settings


@pytest.fixture(autouse=True)
def mock_get_settings(mock_settings: MagicMock) -> Generator[None, None, None]:
    """Automatically mock get_settings for all tests."""
    with patch("src.config.get_settings", return_value=mock_settings):
        yield


# =============================================================================
# Mock Redis Client
# =============================================================================


class MockRedisClient:
    """Mock Redis client for testing."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._sets: dict[str, set[str]] = {}
        self.client = self

    async def get_json(self, key: str) -> dict[str, Any] | None:
        """Get JSON data from mock storage."""
        return self._data.get(key)

    async def set_json(
        self, key: str, value: dict[str, Any], expire_seconds: int | None = None
    ) -> None:
        """Set JSON data in mock storage."""
        self._data[key] = value

    async def set_agent_state(self, agent_id: str, state: dict[str, Any]) -> None:
        """Set agent state."""
        self._data[f"agent:{agent_id}"] = state

    async def update_agent_heartbeat(self, agent_id: str) -> None:
        """Update agent heartbeat."""
        pass

    async def sadd(self, key: str, *values: str) -> None:
        """Add to set."""
        if key not in self._sets:
            self._sets[key] = set()
        self._sets[key].update(values)

    async def smembers(self, key: str) -> set[str]:
        """Get set members."""
        return self._sets.get(key, set())

    async def srem(self, key: str, *values: str) -> None:
        """Remove from set."""
        if key in self._sets:
            self._sets[key] -= set(values)

    def clear(self) -> None:
        """Clear all mock data."""
        self._data.clear()
        self._sets.clear()


@pytest.fixture
def mock_redis() -> MockRedisClient:
    """Create mock Redis client."""
    return MockRedisClient()


@pytest.fixture
def mock_redis_client(mock_redis: MockRedisClient) -> Generator[None, None, None]:
    """Mock get_redis_client for tests."""
    async def get_mock_redis() -> MockRedisClient:
        return mock_redis

    with patch("src.services.get_redis_client", side_effect=get_mock_redis):
        with patch("src.services.redis_client.get_redis_client", side_effect=get_mock_redis):
            yield


# =============================================================================
# Mock RabbitMQ Client
# =============================================================================


class MockRabbitMQClient:
    """Mock RabbitMQ client for testing."""

    def __init__(self) -> None:
        self.published_messages: list[dict[str, Any]] = []

    async def publish_agent_task(
        self, agent_type: str, task_data: dict[str, Any]
    ) -> None:
        """Record published agent task."""
        self.published_messages.append({
            "type": "agent_task",
            "agent_type": agent_type,
            "data": task_data,
        })

    async def publish_hitl_request(self, request_data: dict[str, Any]) -> None:
        """Record published HITL request."""
        self.published_messages.append({
            "type": "hitl_request",
            "data": request_data,
        })

    async def publish_hitl_response(self, response_data: dict[str, Any]) -> None:
        """Record published HITL response."""
        self.published_messages.append({
            "type": "hitl_response",
            "data": response_data,
        })

    async def publish_orchestrator_event(self, event_data: dict[str, Any]) -> None:
        """Record published orchestrator event."""
        self.published_messages.append({
            "type": "orchestrator_event",
            "data": event_data,
        })


@pytest.fixture
def mock_rabbitmq() -> MockRabbitMQClient:
    """Create mock RabbitMQ client."""
    return MockRabbitMQClient()


@pytest.fixture
def mock_rabbitmq_client(
    mock_rabbitmq: MockRabbitMQClient,
) -> Generator[None, None, None]:
    """Mock get_rabbitmq_client for tests."""
    async def get_mock_rabbitmq() -> MockRabbitMQClient:
        return mock_rabbitmq

    with patch("src.services.get_rabbitmq_client", side_effect=get_mock_rabbitmq), patch(
        "src.services.rabbitmq_client.get_rabbitmq_client",
        side_effect=get_mock_rabbitmq,
    ):
        yield


# =============================================================================
# Mock LLM
# =============================================================================


@pytest.fixture
def mock_llm_response() -> str:
    """Default mock LLM response."""
    return '{"result": "success"}'


@pytest.fixture
def mock_gemini(mock_llm_response: str) -> Generator[MagicMock, None, None]:
    """Mock Gemini API for tests."""
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = mock_llm_response

    async def mock_generate(*args: Any, **kwargs: Any) -> MagicMock:
        return mock_response

    mock_model.generate_content_async = mock_generate

    with patch("google.generativeai.GenerativeModel", return_value=mock_model):
        with patch("google.generativeai.configure"):
            yield mock_model


# =============================================================================
# Test Data Factories
# =============================================================================


@pytest.fixture
def sample_company_data() -> dict[str, Any]:
    """Create sample company data for tests."""
    return {
        "company_id": str(uuid4()),
        "name": "Test Company Inc.",
        "industry": "consulting",
        "employee_count": 100,
        "founding_year": 2020,
        "mission": "Deliver value through innovation",
        "vision": "Be the industry leader",
        "values": ["Integrity", "Innovation", "Collaboration"],
        "growth_stage": "growth",
        "has_existing_hr_system": False,
        "design_goals": ["Clear career paths", "Fair compensation"],
    }


@pytest.fixture
def sample_talent_profile() -> dict[str, Any]:
    """Create sample talent profile for tests."""
    return {
        "competencies": [
            {
                "name": "Problem Solving",
                "description": "Ability to analyze and solve complex problems",
                "elements": [
                    {"name": "Analytical Thinking", "description": "Breaking down problems"},
                    {"name": "Creative Solutions", "description": "Finding innovative answers"},
                ],
            },
            {
                "name": "Communication",
                "description": "Clear and effective communication",
                "elements": [
                    {"name": "Written Communication", "description": "Clear writing"},
                    {"name": "Verbal Communication", "description": "Effective speaking"},
                ],
            },
        ],
    }


@pytest.fixture
def sample_grading_system() -> dict[str, Any]:
    """Create sample grading system for tests."""
    return {
        "grades": [
            {
                "level": "J1",
                "name": "Junior I",
                "track": "general",
                "order": 1,
                "description": "Entry level",
                "role_expectations": ["Learn fundamentals"],
                "min_tenure_months": 12,
            },
            {
                "level": "J2",
                "name": "Junior II",
                "track": "general",
                "order": 2,
                "description": "Developing",
                "role_expectations": ["Work independently"],
                "min_tenure_months": 18,
            },
            {
                "level": "S1",
                "name": "Senior I",
                "track": "general",
                "order": 3,
                "description": "Experienced",
                "role_expectations": ["Lead projects"],
                "min_tenure_months": 24,
            },
        ],
        "has_dual_ladder": False,
        "recommended_grade_count": 6,
    }


@pytest.fixture
def sample_evaluation_system() -> dict[str, Any]:
    """Create sample evaluation system for tests."""
    return {
        "evaluation_period": "semi_annual",
        "competency_weight": 0.6,
        "performance_weight": 0.4,
        "has_self_evaluation": True,
        "calibration_required": True,
        "criteria": [
            {
                "name": "Problem Solving",
                "description": "Ability to solve problems",
                "evaluation_type": "competency",
                "weight": 0.3,
            },
            {
                "name": "Goal Achievement",
                "description": "Achievement of set goals",
                "evaluation_type": "performance",
                "weight": 0.4,
            },
        ],
    }


# =============================================================================
# Test Helpers
# =============================================================================


@pytest.fixture
def anyio_backend() -> str:
    """Specify anyio backend for async tests."""
    return "asyncio"

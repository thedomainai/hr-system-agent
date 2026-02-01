"""
Pytest configuration and fixtures for HR System Agent tests.

Provides shared fixtures for unit, integration, and E2E tests
with proper mocking of external services.
"""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator, Generator
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")


# ============================================================================
# Mock Service Classes
# ============================================================================

class MockRedisClient:
    """Mock Redis client for testing with full state management."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self._sets: dict[str, set[str]] = {}
        self.client = self  # For compatibility with sadd/smembers calls

    async def connect(self) -> None:
        """Mock connect."""
        pass

    async def disconnect(self) -> None:
        """Mock disconnect."""
        pass

    async def get(self, key: str) -> str | None:
        """Get a value by key."""
        return self._data.get(key)

    async def set(
        self, key: str, value: str, expire_seconds: int | None = None
    ) -> None:
        """Set a value."""
        self._data[key] = value

    async def setex(self, key: str, expire: int, value: str) -> None:
        """Set with expiration."""
        self._data[key] = value

    async def delete(self, key: str) -> None:
        """Delete a key."""
        self._data.pop(key, None)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return key in self._data

    async def get_json(self, key: str) -> dict[str, Any] | None:
        """Get and parse JSON value."""
        value = self._data.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(
        self, key: str, value: dict[str, Any], expire_seconds: int | None = None
    ) -> None:
        """Serialize and set JSON value."""
        self._data[key] = json.dumps(value, default=str)

    async def get_agent_state(self, agent_id: str) -> dict[str, Any] | None:
        """Get agent state."""
        return await self.get_json(f"agent:state:{agent_id}")

    async def set_agent_state(
        self, agent_id: str, state: dict[str, Any], ttl: int = 3600
    ) -> None:
        """Set agent state."""
        await self.set_json(f"agent:state:{agent_id}", state, ttl)

    async def update_agent_heartbeat(self, agent_id: str) -> None:
        """Update agent heartbeat."""
        self._data[f"agent:heartbeat:{agent_id}"] = "1"

    async def is_agent_alive(self, agent_id: str) -> bool:
        """Check if agent is alive."""
        return f"agent:heartbeat:{agent_id}" in self._data

    # Set operations for HITL pending requests
    async def sadd(self, key: str, *values: str) -> int:
        """Add members to a set."""
        if key not in self._sets:
            self._sets[key] = set()
        before = len(self._sets[key])
        self._sets[key].update(values)
        return len(self._sets[key]) - before

    async def smembers(self, key: str) -> set[str]:
        """Get all members of a set."""
        return self._sets.get(key, set())

    async def srem(self, key: str, *values: str) -> int:
        """Remove members from a set."""
        if key not in self._sets:
            return 0
        removed = 0
        for v in values:
            if v in self._sets[key]:
                self._sets[key].discard(v)
                removed += 1
        return removed

    def clear(self) -> None:
        """Clear all data (for test cleanup)."""
        self._data.clear()
        self._sets.clear()


class MockRabbitMQClient:
    """Mock RabbitMQ client for testing with message tracking."""

    def __init__(self) -> None:
        self._messages: dict[str, list[dict[str, Any]]] = {}
        self._consumers: dict[str, Any] = {}

    async def connect(self) -> None:
        """Mock connect."""
        pass

    async def disconnect(self) -> None:
        """Mock disconnect."""
        pass

    async def declare_queue(self, queue_name: str, durable: bool = True) -> None:
        """Declare a queue."""
        if queue_name not in self._messages:
            self._messages[queue_name] = []

    async def publish(
        self, queue_name: str, message: dict[str, Any], priority: int = 0
    ) -> None:
        """Publish a message."""
        if queue_name not in self._messages:
            self._messages[queue_name] = []
        self._messages[queue_name].append(message)

    async def publish_agent_task(
        self, agent_type: str, task: dict[str, Any]
    ) -> None:
        """Publish a task to an agent's queue."""
        await self.publish(f"agent.{agent_type}.tasks", task)

    async def publish_hitl_request(self, request: dict[str, Any]) -> None:
        """Publish a HITL approval request."""
        await self.publish("hitl.requests", request)

    async def publish_hitl_response(self, response: dict[str, Any]) -> None:
        """Publish a HITL approval response."""
        await self.publish("hitl.responses", response)

    async def publish_orchestrator_event(self, event: dict[str, Any]) -> None:
        """Publish an event to the orchestrator."""
        await self.publish("orchestrator.events", event)

    def get_messages(self, queue_name: str) -> list[dict[str, Any]]:
        """Get messages from a queue (for testing)."""
        return self._messages.get(queue_name, [])

    def clear(self) -> None:
        """Clear all messages (for test cleanup)."""
        self._messages.clear()


class MockVaultClient:
    """Mock Vault client for testing."""

    def __init__(self) -> None:
        self._secrets: dict[str, dict[str, Any]] = {}

    async def connect(self) -> None:
        """Mock connect."""
        pass

    async def disconnect(self) -> None:
        """Mock disconnect."""
        pass

    async def get_secret(self, path: str) -> dict[str, Any] | None:
        """Get a secret."""
        return self._secrets.get(path)

    async def set_secret(self, path: str, value: dict[str, Any]) -> None:
        """Set a secret."""
        self._secrets[path] = value


# ============================================================================
# Mock LLM Responses
# ============================================================================

def mock_llm_response(content_type: str) -> str:
    """Generate mock LLM responses for different agent types."""
    responses = {
        "talent_profile": """{
            "vision_statement": "Self-driven problem solvers who create value",
            "competencies": [
                {
                    "name": "Problem Solving",
                    "description": "Ability to analyze and solve complex problems",
                    "elements": [
                        {
                            "name": "Analysis",
                            "description": "Breaking down problems into components",
                            "behavioral_indicators": ["Collects relevant data", "Identifies root causes"]
                        },
                        {
                            "name": "Solution Design",
                            "description": "Creating effective solutions",
                            "behavioral_indicators": ["Proposes multiple options", "Considers risks"]
                        }
                    ],
                    "weight": 0.33
                },
                {
                    "name": "Communication",
                    "description": "Ability to communicate effectively",
                    "elements": [
                        {
                            "name": "Listening",
                            "description": "Understanding others accurately",
                            "behavioral_indicators": ["Asks clarifying questions", "Summarizes key points"]
                        },
                        {
                            "name": "Explaining",
                            "description": "Conveying ideas clearly",
                            "behavioral_indicators": ["Structures information logically", "Adapts to audience"]
                        }
                    ],
                    "weight": 0.33
                },
                {
                    "name": "Autonomy",
                    "description": "Ability to work independently and grow",
                    "elements": [
                        {
                            "name": "Initiative",
                            "description": "Taking action proactively",
                            "behavioral_indicators": ["Acts without being asked", "Proposes improvements"]
                        },
                        {
                            "name": "Learning",
                            "description": "Continuous self-improvement",
                            "behavioral_indicators": ["Seeks feedback", "Acquires new skills"]
                        }
                    ],
                    "weight": 0.34
                }
            ]
        }""",
        "grading_system": """{
            "type": "role_based",
            "grades": [
                {"level": 1, "name": "G1", "title": "Staff", "salary_min": 3000000, "salary_max": 4000000},
                {"level": 2, "name": "G2", "title": "Senior Staff", "salary_min": 4000000, "salary_max": 5500000},
                {"level": 3, "name": "G3", "title": "Leader", "salary_min": 5500000, "salary_max": 7000000},
                {"level": 4, "name": "G4", "title": "Manager", "salary_min": 7000000, "salary_max": 9000000},
                {"level": 5, "name": "G5", "title": "Senior Manager", "salary_min": 9000000, "salary_max": 12000000}
            ],
            "graduation_requirements": [
                {"grade_level": 1, "requirement": "Can perform basic tasks independently"},
                {"grade_level": 2, "requirement": "Can guide team members"},
                {"grade_level": 3, "requirement": "Can lead projects"},
                {"grade_level": 4, "requirement": "Can contribute to strategy"}
            ]
        }""",
        "evaluation_system": """{
            "type": "hybrid",
            "periods": [
                {"name": "First Half", "start_month": 4, "end_month": 9},
                {"name": "Second Half", "start_month": 10, "end_month": 3}
            ],
            "criteria": [
                {"name": "Goal Achievement", "weight": 0.5, "type": "mbo"},
                {"name": "Competency", "weight": 0.3, "type": "competency"},
                {"name": "360 Degree", "weight": 0.2, "type": "360_degree"}
            ],
            "rating_scale": {
                "levels": 5,
                "labels": ["Below", "Slightly Below", "Meets", "Exceeds", "Outstanding"]
            }
        }""",
        "compensation_system": """{
            "base_salary": {
                "type": "grade_based",
                "structure": "single_rate"
            },
            "bonus": {
                "type": "performance_linked",
                "base_months": 4,
                "performance_range": {"min": 0.5, "max": 1.5}
            },
            "allowances": [
                {"name": "Commuting", "type": "actual_expense", "max_amount": 50000},
                {"name": "Housing", "type": "fixed", "amount": 30000}
            ]
        }""",
        "context": """{
            "industry_analysis": {
                "characteristics": "Consulting is knowledge-intensive, requiring expertise and client focus",
                "key_success_factors": ["Expertise", "Client orientation", "Problem solving"],
                "market_trends": ["Digital transformation", "ESG", "HR strategy"]
            },
            "benchmarks": {
                "avg_salary_by_grade": {
                    "junior": 4500000,
                    "mid": 6500000,
                    "senior": 9000000,
                    "manager": 12000000
                }
            },
            "recommendations": {
                "grading_type": "role_based",
                "evaluation_type": "hybrid"
            }
        }"""
    }
    return responses.get(content_type, "{}")


# ============================================================================
# Basic Fixtures
# ============================================================================

@pytest.fixture
def mock_settings():
    """Mock settings for tests."""
    with patch("src.config.settings.get_settings") as mock:
        settings = MagicMock()
        settings.gemini_api_key = "test-api-key"
        settings.gemini_model = "gemini-2.0-flash"
        settings.hitl_default_timeout_hours = 72
        settings.hitl_critical_timeout_hours = 48
        settings.agent_heartbeat_interval_seconds = 30
        settings.redis_url = "redis://localhost:6379/0"
        settings.rabbitmq_url = "amqp://guest:guest@localhost:5672/"
        settings.app_name = "HR System Agent"
        settings.app_version = "0.1.0"
        settings.env = "test"
        settings.is_development = True
        settings.host = "0.0.0.0"
        settings.port = 8000
        settings.log_level = "DEBUG"
        mock.return_value = settings
        yield settings


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for tests (simple mock)."""
    with patch("src.services.redis_client.get_redis_client") as mock:
        client = AsyncMock()
        client.set_json = AsyncMock()
        client.get_json = AsyncMock(return_value=None)
        client.set_agent_state = AsyncMock()
        client.update_agent_heartbeat = AsyncMock()
        client.client = AsyncMock()
        client.client.sadd = AsyncMock()
        client.client.srem = AsyncMock()
        client.client.smembers = AsyncMock(return_value=set())
        mock.return_value = client
        yield client


@pytest.fixture
def mock_rabbitmq_client():
    """Mock RabbitMQ client for tests (simple mock)."""
    with patch("src.services.rabbitmq_client.get_rabbitmq_client") as mock:
        client = AsyncMock()
        client.publish_hitl_request = AsyncMock()
        client.publish_hitl_response = AsyncMock()
        client.publish_agent_task = AsyncMock()
        client.publish_orchestrator_event = AsyncMock()
        mock.return_value = client
        yield client


# ============================================================================
# E2E Fixtures
# ============================================================================

@pytest.fixture
def e2e_mock_redis() -> MockRedisClient:
    """Create a stateful mock Redis client for E2E tests."""
    return MockRedisClient()


@pytest.fixture
def e2e_mock_rabbitmq() -> MockRabbitMQClient:
    """Create a stateful mock RabbitMQ client for E2E tests."""
    return MockRabbitMQClient()


@pytest.fixture
def e2e_mock_vault() -> MockVaultClient:
    """Create a mock Vault client for E2E tests."""
    return MockVaultClient()


@pytest.fixture
def e2e_mock_settings() -> MagicMock:
    """Create mock settings for E2E tests."""
    settings = MagicMock()
    settings.gemini_api_key = "test-api-key"
    settings.gemini_model = "gemini-2.0-flash"
    settings.hitl_default_timeout_hours = 72
    settings.hitl_critical_timeout_hours = 48
    settings.agent_heartbeat_interval_seconds = 30
    settings.redis_url = "redis://localhost:6379/0"
    settings.rabbitmq_url = "amqp://guest:guest@localhost:5672/"
    settings.app_name = "HR System Agent"
    settings.app_version = "0.1.0"
    settings.env = "test"
    settings.is_development = True
    settings.host = "0.0.0.0"
    settings.port = 8000
    settings.log_level = "DEBUG"
    return settings


@pytest.fixture
def e2e_mock_services(
    e2e_mock_redis: MockRedisClient,
    e2e_mock_rabbitmq: MockRabbitMQClient,
    e2e_mock_vault: MockVaultClient,
    e2e_mock_settings: MagicMock,
) -> Generator[tuple[MockRedisClient, MockRabbitMQClient, MockVaultClient], None, None]:
    """
    Patch all service clients with stateful mocks for E2E tests.

    Returns a tuple of (redis, rabbitmq, vault) mocks.
    """
    patches = [
        patch("src.services.redis_client._redis_client", e2e_mock_redis),
        patch("src.services.rabbitmq_client._rabbitmq_client", e2e_mock_rabbitmq),
        patch("src.services.vault_client._vault_client", e2e_mock_vault),
        patch("src.services.get_redis_client", AsyncMock(return_value=e2e_mock_redis)),
        patch("src.services.get_rabbitmq_client", AsyncMock(return_value=e2e_mock_rabbitmq)),
        patch("src.services.get_vault_client", AsyncMock(return_value=e2e_mock_vault)),
        patch("src.api.routes.companies.get_redis_client", AsyncMock(return_value=e2e_mock_redis)),
        patch("src.api.routes.policies.get_redis_client", AsyncMock(return_value=e2e_mock_redis)),
        patch("src.core.orchestrator.get_redis_client", AsyncMock(return_value=e2e_mock_redis)),
        patch("src.core.orchestrator.get_rabbitmq_client", AsyncMock(return_value=e2e_mock_rabbitmq)),
        patch("src.core.hitl_manager.get_redis_client", AsyncMock(return_value=e2e_mock_redis)),
        patch("src.core.hitl_manager.get_rabbitmq_client", AsyncMock(return_value=e2e_mock_rabbitmq)),
        patch("src.core.agent_base.get_redis_client", AsyncMock(return_value=e2e_mock_redis)),
        patch("src.core.agent_base.get_rabbitmq_client", AsyncMock(return_value=e2e_mock_rabbitmq)),
        patch("src.config.get_settings", return_value=e2e_mock_settings),
        patch("src.config.settings.get_settings", return_value=e2e_mock_settings),
    ]

    for p in patches:
        p.start()

    yield e2e_mock_redis, e2e_mock_rabbitmq, e2e_mock_vault

    for p in patches:
        p.stop()


@pytest.fixture
def e2e_mock_llm() -> Generator[MagicMock, None, None]:
    """Mock the LLM (Gemini) calls for E2E tests."""
    with patch("src.core.agent_base.genai") as mock_genai:
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = mock_llm_response("talent_profile")

        async def mock_generate(*args: Any, **kwargs: Any) -> MagicMock:
            return mock_response

        mock_model.generate_content_async = mock_generate
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.GenerationConfig = MagicMock

        yield mock_genai


@pytest.fixture
async def e2e_client(
    e2e_mock_services: tuple[MockRedisClient, MockRabbitMQClient, MockVaultClient],
) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for E2E testing."""
    from src.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_company_data():
    """Sample company data for tests."""
    return {
        "name": "Test Company",
        "industry": "consulting",
        "employee_count": 80,
        "founding_year": 2015,
        "mission": "To provide excellent consulting services",
        "vision": "To be the leading consulting firm",
        "values": ["integrity", "excellence", "innovation"],
        "business_model": "B2B consulting",
        "target_market": "Enterprise",
        "growth_stage": "growth",
        "has_existing_hr_system": False,
        "existing_system_description": "",
        "design_goals": ["Clear career paths", "Performance-based rewards"],
        "constraints": ["Budget limitations"],
    }


@pytest.fixture
def sample_company_response() -> dict[str, Any]:
    """Sample company response for testing."""
    return {
        "company_id": str(uuid4()),
        "name": "Test Company",
        "industry": "consulting",
        "size": "small",
        "employee_count": 80,
        "created_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_talent_profile_data():
    """Sample talent profile data for tests."""
    return {
        "company_id": "test-company-id",
        "vision_statement": "Self-driven problem solvers who create value",
        "competencies": [
            {
                "name": "Problem Solving",
                "description": "Ability to analyze and solve complex problems",
                "elements": [
                    {"name": "Analysis", "description": "Breaking down problems"},
                    {"name": "Solution Design", "description": "Creating solutions"},
                ],
                "weight": 0.33,
            },
            {
                "name": "Communication",
                "description": "Ability to communicate effectively",
                "elements": [
                    {"name": "Listening", "description": "Understanding others"},
                    {"name": "Explaining", "description": "Conveying ideas clearly"},
                ],
                "weight": 0.33,
            },
            {
                "name": "Autonomy",
                "description": "Ability to work independently",
                "elements": [
                    {"name": "Initiative", "description": "Taking action proactively"},
                    {"name": "Learning", "description": "Continuous self-improvement"},
                ],
                "weight": 0.34,
            },
        ],
    }


@pytest.fixture
def sample_grading_system_data():
    """Sample grading system data for tests."""
    return {
        "company_id": "test-company-id",
        "name": "Grading System",
        "grades": [
            {
                "level": "J1",
                "name": "Junior I",
                "track": "general",
                "order": 1,
                "description": "Entry level",
            },
            {
                "level": "J2",
                "name": "Junior II",
                "track": "general",
                "order": 2,
                "description": "Developing level",
            },
            {
                "level": "S1",
                "name": "Senior I",
                "track": "general",
                "order": 3,
                "description": "Senior level",
            },
        ],
        "has_dual_ladder": False,
        "max_grade_level": 6,
    }


@pytest.fixture
def sample_evaluation_system_data():
    """Sample evaluation system data for tests."""
    return {
        "company_id": "test-company-id",
        "name": "Evaluation System",
        "evaluation_period": "semi_annual",
        "competency_weight": 0.6,
        "performance_weight": 0.4,
        "has_self_evaluation": True,
        "has_peer_evaluation": False,
    }


@pytest.fixture
def sample_compensation_system_data():
    """Sample compensation system data for tests."""
    return {
        "company_id": "test-company-id",
        "name": "Compensation System",
        "salary_bands": [
            {
                "grade_level": "J1",
                "min_salary": 3000000,
                "mid_salary": 3500000,
                "max_salary": 4000000,
            },
            {
                "grade_level": "J2",
                "min_salary": 4000000,
                "mid_salary": 4500000,
                "max_salary": 5000000,
            },
        ],
        "total_bonus_months": 4.0,
        "market_position": "50th percentile",
    }


# ============================================================================
# Helper Functions
# ============================================================================

async def create_test_company(
    client: AsyncClient,
    company_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Helper to create a company for testing."""
    data = company_data or {
        "name": "Test Company",
        "industry": "consulting",
        "employee_count": 80,
        "mission": "Test mission",
        "vision": "Test vision",
        "values": ["Test value"],
    }
    response = await client.post("/api/v1/companies", json=data)
    assert response.status_code == 200
    return response.json()


async def start_workflow(
    client: AsyncClient,
    company_id: str,
) -> dict[str, Any]:
    """Helper to start a policy workflow."""
    response = await client.post(
        "/api/v1/policies/workflows",
        json={"company_id": company_id},
    )
    assert response.status_code == 200
    return response.json()


async def get_workflow_status(
    client: AsyncClient,
    workflow_id: str,
) -> dict[str, Any]:
    """Helper to get workflow status."""
    response = await client.get(f"/api/v1/policies/workflows/{workflow_id}")
    assert response.status_code == 200
    return response.json()


async def get_pending_reviews(
    client: AsyncClient,
    company_id: str,
) -> list[dict[str, Any]]:
    """Helper to get pending HITL reviews for a company."""
    response = await client.get(f"/api/v1/reviews/pending/{company_id}")
    assert response.status_code == 200
    return response.json()


async def submit_hitl_decision(
    client: AsyncClient,
    request_id: str,
    approved: bool = True,
    feedback: str | None = None,
) -> dict[str, Any]:
    """Helper to submit a HITL decision."""
    response = await client.post(
        f"/api/v1/reviews/{request_id}/decision",
        json={"approved": approved, "feedback": feedback},
    )
    assert response.status_code == 200
    return response.json()

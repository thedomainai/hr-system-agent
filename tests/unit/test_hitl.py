"""
Unit tests for HITL (Human-in-the-Loop) Manager.

Tests approval workflow creation, decision handling, and state management.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.hitl_manager import (
    HITLDecision,
    HITLGateId,
    HITLManager,
    HITLRequest,
    HITLStatus,
)


# =============================================================================
# HITLGateId Tests
# =============================================================================


class TestHITLGateId:
    """Test HITL gate identifiers."""

    def test_all_gates_defined(self) -> None:
        """Test all expected gates are defined."""
        expected_gates = [
            "HITL-001",  # Company context
            "HITL-002",  # Talent profile
            "HITL-003",  # Grading system
            "HITL-004",  # Evaluation system
            "HITL-005",  # Compensation system
            "HITL-006",  # Final review
            "HITL-007",  # Output confirmation
        ]
        actual_gates = [g.value for g in HITLGateId]
        for expected in expected_gates:
            assert expected in actual_gates


class TestHITLStatus:
    """Test HITL status values."""

    def test_valid_statuses(self) -> None:
        """Test all expected statuses are defined."""
        assert HITLStatus.PENDING.value == "pending"
        assert HITLStatus.APPROVED.value == "approved"
        assert HITLStatus.REJECTED.value == "rejected"
        assert HITLStatus.EXPIRED.value == "expired"
        assert HITLStatus.CANCELLED.value == "cancelled"


# =============================================================================
# HITLRequest Tests
# =============================================================================


class TestHITLRequest:
    """Test HITL request model."""

    def test_create_valid_request(self) -> None:
        """Test creating a valid HITL request."""
        request = HITLRequest(
            gate_id="HITL-001",
            agent_id="agent-123",
            agent_type="context_collector",
            company_id="company-456",
            title="Test Approval",
            description="Please review",
            timeout_hours=72,
        )
        assert request.gate_id == "HITL-001"
        assert request.status == HITLStatus.PENDING
        assert request.request_id is not None

    def test_request_default_values(self) -> None:
        """Test request default values."""
        request = HITLRequest(
            gate_id="HITL-001",
            agent_id="agent-123",
            agent_type="test",
            company_id="company-456",
            title="Test",
            description="Test",
            timeout_hours=24,
        )
        assert request.status == HITLStatus.PENDING
        assert request.decided_at is None
        assert request.feedback is None

    def test_request_serialization(self) -> None:
        """Test request JSON serialization."""
        request = HITLRequest(
            gate_id="HITL-001",
            agent_id="agent-123",
            agent_type="test",
            company_id="company-456",
            title="Test",
            description="Test",
            timeout_hours=24,
            data={"key": "value"},
        )
        data = request.model_dump(mode="json")
        assert data["gate_id"] == "HITL-001"
        assert data["data"]["key"] == "value"


class TestHITLDecision:
    """Test HITL decision model."""

    def test_create_approval_decision(self) -> None:
        """Test creating an approval decision."""
        decision = HITLDecision(
            request_id="req-123",
            approved=True,
            decided_by="user@example.com",
        )
        assert decision.approved is True
        assert decision.feedback is None

    def test_create_rejection_decision(self) -> None:
        """Test creating a rejection decision."""
        decision = HITLDecision(
            request_id="req-123",
            approved=False,
            feedback="Needs more detail",
            decided_by="reviewer@example.com",
        )
        assert decision.approved is False
        assert decision.feedback == "Needs more detail"


# =============================================================================
# HITLManager Tests
# =============================================================================


class TestHITLManager:
    """Test HITL Manager functionality."""

    @pytest.fixture
    def manager(self) -> HITLManager:
        """Create a fresh HITL manager for each test."""
        return HITLManager()

    @pytest.fixture
    def mock_redis(self) -> MagicMock:
        """Create mock Redis client."""
        mock = MagicMock()
        mock.set_json = AsyncMock()
        mock.get_json = AsyncMock()
        mock.client = MagicMock()
        mock.client.sadd = AsyncMock()
        mock.client.smembers = AsyncMock(return_value=set())
        mock.client.srem = AsyncMock()
        return mock

    @pytest.fixture
    def mock_rabbitmq(self) -> MagicMock:
        """Create mock RabbitMQ client."""
        mock = MagicMock()
        mock.publish_hitl_response = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_create_request(
        self, manager: HITLManager, mock_redis: MagicMock
    ) -> None:
        """Test creating a HITL request."""
        with patch("src.core.hitl_manager.get_redis_client", return_value=mock_redis):
            with patch("src.core.hitl_manager.get_settings") as mock_settings:
                mock_settings.return_value.hitl_default_timeout_hours = 72

                request = await manager.create_request(
                    gate_id="HITL-001",
                    agent_id="agent-123",
                    agent_type="context_collector",
                    company_id="company-456",
                    title="Test Approval",
                    description="Please review",
                    data={"test": "data"},
                )

                assert request.gate_id == "HITL-001"
                assert request.company_id == "company-456"
                assert request.status == HITLStatus.PENDING
                assert request.expires_at is not None

                # Verify Redis was called
                mock_redis.set_json.assert_called_once()
                mock_redis.client.sadd.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_request(
        self, manager: HITLManager, mock_redis: MagicMock
    ) -> None:
        """Test retrieving a HITL request."""
        stored_request = {
            "request_id": "req-123",
            "gate_id": "HITL-001",
            "agent_id": "agent-123",
            "agent_type": "test",
            "company_id": "company-456",
            "title": "Test",
            "description": "Test",
            "status": "pending",
            "timeout_hours": 72,
            "requested_at": datetime.utcnow().isoformat(),
        }
        mock_redis.get_json.return_value = stored_request

        with patch("src.core.hitl_manager.get_redis_client", return_value=mock_redis):
            request = await manager.get_request("req-123")

            assert request is not None
            assert request.request_id == "req-123"
            assert request.gate_id == "HITL-001"

    @pytest.mark.asyncio
    async def test_get_request_not_found(
        self, manager: HITLManager, mock_redis: MagicMock
    ) -> None:
        """Test retrieving a non-existent request."""
        mock_redis.get_json.return_value = None

        with patch("src.core.hitl_manager.get_redis_client", return_value=mock_redis):
            request = await manager.get_request("non-existent")
            assert request is None

    @pytest.mark.asyncio
    async def test_submit_approval_decision(
        self,
        manager: HITLManager,
        mock_redis: MagicMock,
        mock_rabbitmq: MagicMock,
    ) -> None:
        """Test submitting an approval decision."""
        stored_request = {
            "request_id": "req-123",
            "gate_id": "HITL-001",
            "agent_id": "agent-123",
            "agent_type": "test",
            "company_id": "company-456",
            "title": "Test",
            "description": "Test",
            "status": "pending",
            "timeout_hours": 72,
            "requested_at": datetime.utcnow().isoformat(),
        }
        mock_redis.get_json.return_value = stored_request

        with patch("src.core.hitl_manager.get_redis_client", return_value=mock_redis):
            with patch(
                "src.core.hitl_manager.get_rabbitmq_client", return_value=mock_rabbitmq
            ):
                decision = await manager.submit_decision(
                    request_id="req-123",
                    approved=True,
                    decided_by="reviewer@example.com",
                )

                assert decision is not None
                assert decision.approved is True
                assert decision.decided_by == "reviewer@example.com"

                # Verify Redis was updated
                mock_redis.set_json.assert_called()
                mock_redis.client.srem.assert_called()

                # Verify RabbitMQ message was published
                mock_rabbitmq.publish_hitl_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_submit_rejection_decision(
        self,
        manager: HITLManager,
        mock_redis: MagicMock,
        mock_rabbitmq: MagicMock,
    ) -> None:
        """Test submitting a rejection decision."""
        stored_request = {
            "request_id": "req-123",
            "gate_id": "HITL-001",
            "agent_id": "agent-123",
            "agent_type": "test",
            "company_id": "company-456",
            "title": "Test",
            "description": "Test",
            "status": "pending",
            "timeout_hours": 72,
            "requested_at": datetime.utcnow().isoformat(),
        }
        mock_redis.get_json.return_value = stored_request

        with patch("src.core.hitl_manager.get_redis_client", return_value=mock_redis):
            with patch(
                "src.core.hitl_manager.get_rabbitmq_client", return_value=mock_rabbitmq
            ):
                decision = await manager.submit_decision(
                    request_id="req-123",
                    approved=False,
                    feedback="Needs more detail on grading criteria",
                    decided_by="reviewer@example.com",
                )

                assert decision is not None
                assert decision.approved is False
                assert decision.feedback == "Needs more detail on grading criteria"

    @pytest.mark.asyncio
    async def test_submit_decision_request_not_found(
        self, manager: HITLManager, mock_redis: MagicMock
    ) -> None:
        """Test submitting decision for non-existent request."""
        mock_redis.get_json.return_value = None

        with patch("src.core.hitl_manager.get_redis_client", return_value=mock_redis):
            decision = await manager.submit_decision(
                request_id="non-existent",
                approved=True,
                decided_by="reviewer",
            )
            assert decision is None

    @pytest.mark.asyncio
    async def test_submit_decision_not_pending(
        self, manager: HITLManager, mock_redis: MagicMock
    ) -> None:
        """Test submitting decision for already decided request."""
        stored_request = {
            "request_id": "req-123",
            "gate_id": "HITL-001",
            "agent_id": "agent-123",
            "agent_type": "test",
            "company_id": "company-456",
            "title": "Test",
            "description": "Test",
            "status": "approved",  # Already decided
            "timeout_hours": 72,
            "requested_at": datetime.utcnow().isoformat(),
        }
        mock_redis.get_json.return_value = stored_request

        with patch("src.core.hitl_manager.get_redis_client", return_value=mock_redis):
            decision = await manager.submit_decision(
                request_id="req-123",
                approved=True,
                decided_by="reviewer",
            )
            assert decision is None

    @pytest.mark.asyncio
    async def test_cancel_request(
        self, manager: HITLManager, mock_redis: MagicMock
    ) -> None:
        """Test cancelling a pending request."""
        stored_request = {
            "request_id": "req-123",
            "gate_id": "HITL-001",
            "agent_id": "agent-123",
            "agent_type": "test",
            "company_id": "company-456",
            "title": "Test",
            "description": "Test",
            "status": "pending",
            "timeout_hours": 72,
            "requested_at": datetime.utcnow().isoformat(),
        }
        mock_redis.get_json.return_value = stored_request

        with patch("src.core.hitl_manager.get_redis_client", return_value=mock_redis):
            result = await manager.cancel_request("req-123")

            assert result is True
            mock_redis.set_json.assert_called()
            mock_redis.client.srem.assert_called()

    @pytest.mark.asyncio
    async def test_cancel_non_pending_request(
        self, manager: HITLManager, mock_redis: MagicMock
    ) -> None:
        """Test cancelling a non-pending request."""
        stored_request = {
            "request_id": "req-123",
            "gate_id": "HITL-001",
            "agent_id": "agent-123",
            "agent_type": "test",
            "company_id": "company-456",
            "title": "Test",
            "description": "Test",
            "status": "approved",
            "timeout_hours": 72,
            "requested_at": datetime.utcnow().isoformat(),
        }
        mock_redis.get_json.return_value = stored_request

        with patch("src.core.hitl_manager.get_redis_client", return_value=mock_redis):
            result = await manager.cancel_request("req-123")
            assert result is False

    def test_get_gate_info(self, manager: HITLManager) -> None:
        """Test getting gate information."""
        info = manager.get_gate_info(HITLGateId.GRADING_SYSTEM.value)

        assert info["name"] == "Grading System Approval"
        assert info["required"] is True

    def test_get_gate_info_unknown(self, manager: HITLManager) -> None:
        """Test getting info for unknown gate."""
        info = manager.get_gate_info("UNKNOWN-GATE")

        assert info["name"] == "UNKNOWN-GATE"
        assert info["required"] is False

    @pytest.mark.asyncio
    async def test_get_pending_requests(
        self, manager: HITLManager, mock_redis: MagicMock
    ) -> None:
        """Test getting pending requests for a company."""
        mock_redis.client.smembers.return_value = {"req-1", "req-2"}

        stored_request_1 = {
            "request_id": "req-1",
            "gate_id": "HITL-001",
            "agent_id": "agent-123",
            "agent_type": "test",
            "company_id": "company-456",
            "title": "Test 1",
            "description": "Test",
            "status": "pending",
            "timeout_hours": 72,
            "requested_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=72)).isoformat(),
        }
        stored_request_2 = {
            "request_id": "req-2",
            "gate_id": "HITL-002",
            "agent_id": "agent-456",
            "agent_type": "test",
            "company_id": "company-456",
            "title": "Test 2",
            "description": "Test",
            "status": "pending",
            "timeout_hours": 72,
            "requested_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=72)).isoformat(),
        }

        async def get_json_side_effect(key: str) -> dict | None:
            if "req-1" in key:
                return stored_request_1
            if "req-2" in key:
                return stored_request_2
            return None

        mock_redis.get_json.side_effect = get_json_side_effect

        with patch("src.core.hitl_manager.get_redis_client", return_value=mock_redis):
            requests = await manager.get_pending_requests("company-456")

            assert len(requests) == 2
            request_ids = [r.request_id for r in requests]
            assert "req-1" in request_ids
            assert "req-2" in request_ids

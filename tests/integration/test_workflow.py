"""
Integration tests for workflow execution.

Tests the complete workflow from start to finish.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.orchestrator import Orchestrator, WorkflowStatus


class TestWorkflowIntegration:
    """Integration tests for the workflow orchestrator."""

    @pytest.fixture
    def mock_redis(self) -> MagicMock:
        """Create mock Redis client."""
        mock = MagicMock()
        mock.set_json = AsyncMock()
        mock.get_json = AsyncMock(return_value=None)
        return mock

    @pytest.fixture
    def mock_rabbitmq(self) -> MagicMock:
        """Create mock RabbitMQ client."""
        mock = MagicMock()
        mock.publish_orchestrator_event = AsyncMock()
        mock.publish_agent_task = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_workflow_initialization(
        self, mock_redis: MagicMock, mock_rabbitmq: MagicMock
    ) -> None:
        """Test workflow initialization creates correct steps."""
        orchestrator = Orchestrator(company_id="test-company")

        assert orchestrator.state.company_id == "test-company"
        assert len(orchestrator.state.steps) == 5

        step_ids = [s.step_id for s in orchestrator.state.steps]
        expected_steps = [
            "collect_context",
            "generate_talent_profile",
            "design_grading",
            "design_evaluation",
            "design_compensation",
        ]
        assert step_ids == expected_steps

    @pytest.mark.asyncio
    async def test_workflow_start(
        self, mock_redis: MagicMock, mock_rabbitmq: MagicMock
    ) -> None:
        """Test starting a workflow."""
        with patch("src.core.orchestrator.get_redis_client", return_value=mock_redis):
            with patch(
                "src.core.orchestrator.get_rabbitmq_client", return_value=mock_rabbitmq
            ):
                orchestrator = Orchestrator(company_id="test-company")
                initial_data = {"name": "Test Company", "industry": "consulting"}

                await orchestrator.start(initial_data)

                assert orchestrator.state.status == WorkflowStatus.RUNNING
                mock_redis.set_json.assert_called()
                mock_rabbitmq.publish_orchestrator_event.assert_called()

    @pytest.mark.asyncio
    async def test_workflow_step_execution(
        self, mock_redis: MagicMock, mock_rabbitmq: MagicMock
    ) -> None:
        """Test executing a workflow step."""
        with patch("src.core.orchestrator.get_redis_client", return_value=mock_redis):
            with patch(
                "src.core.orchestrator.get_rabbitmq_client", return_value=mock_rabbitmq
            ):
                orchestrator = Orchestrator(company_id="test-company")
                await orchestrator.start({})

                result = await orchestrator.execute_step("collect_context")

                assert result is True
                mock_rabbitmq.publish_agent_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_workflow_progress(
        self, mock_redis: MagicMock, mock_rabbitmq: MagicMock
    ) -> None:
        """Test getting workflow progress."""
        orchestrator = Orchestrator(company_id="test-company")

        progress = orchestrator.get_progress()

        assert progress["status"] == "pending"
        assert progress["progress"] == "0/5"
        assert progress["percent"] == 0

    @pytest.mark.asyncio
    async def test_workflow_step_completion(
        self, mock_redis: MagicMock, mock_rabbitmq: MagicMock
    ) -> None:
        """Test handling step completion."""
        with patch("src.core.orchestrator.get_redis_client", return_value=mock_redis):
            with patch(
                "src.core.orchestrator.get_rabbitmq_client", return_value=mock_rabbitmq
            ):
                orchestrator = Orchestrator(company_id="test-company")
                await orchestrator.start({})

                await orchestrator.on_step_completed(
                    step_id="collect_context",
                    output_data={"company": {"name": "Test"}},
                    requires_hitl=False,
                )

                step = orchestrator._get_step("collect_context")
                assert step.status == WorkflowStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_workflow_hitl_waiting(
        self, mock_redis: MagicMock, mock_rabbitmq: MagicMock
    ) -> None:
        """Test workflow waiting for HITL approval."""
        with patch("src.core.orchestrator.get_redis_client", return_value=mock_redis):
            with patch(
                "src.core.orchestrator.get_rabbitmq_client", return_value=mock_rabbitmq
            ):
                orchestrator = Orchestrator(company_id="test-company")
                await orchestrator.start({})

                await orchestrator.on_step_completed(
                    step_id="collect_context",
                    output_data={"company": {"name": "Test"}},
                    requires_hitl=True,
                )

                step = orchestrator._get_step("collect_context")
                assert step.status == WorkflowStatus.WAITING_HITL
                assert orchestrator.state.status == WorkflowStatus.WAITING_HITL

    @pytest.mark.asyncio
    async def test_workflow_hitl_approval(
        self, mock_redis: MagicMock, mock_rabbitmq: MagicMock
    ) -> None:
        """Test HITL approval continues workflow."""
        with patch("src.core.orchestrator.get_redis_client", return_value=mock_redis):
            with patch(
                "src.core.orchestrator.get_rabbitmq_client", return_value=mock_rabbitmq
            ):
                orchestrator = Orchestrator(company_id="test-company")
                await orchestrator.start({})

                # Complete step with HITL
                await orchestrator.on_step_completed(
                    step_id="collect_context",
                    output_data={"company": {"name": "Test"}},
                    requires_hitl=True,
                )

                # Approve HITL
                await orchestrator.on_hitl_decision(
                    step_id="collect_context",
                    approved=True,
                )

                step = orchestrator._get_step("collect_context")
                assert step.status == WorkflowStatus.COMPLETED
                assert orchestrator.state.status == WorkflowStatus.RUNNING

    @pytest.mark.asyncio
    async def test_workflow_hitl_rejection(
        self, mock_redis: MagicMock, mock_rabbitmq: MagicMock
    ) -> None:
        """Test HITL rejection fails workflow."""
        with patch("src.core.orchestrator.get_redis_client", return_value=mock_redis):
            with patch(
                "src.core.orchestrator.get_rabbitmq_client", return_value=mock_rabbitmq
            ):
                orchestrator = Orchestrator(company_id="test-company")
                await orchestrator.start({})

                await orchestrator.on_step_completed(
                    step_id="collect_context",
                    output_data={"company": {"name": "Test"}},
                    requires_hitl=True,
                )

                await orchestrator.on_hitl_decision(
                    step_id="collect_context",
                    approved=False,
                    feedback="Needs more detail",
                )

                step = orchestrator._get_step("collect_context")
                assert step.status == WorkflowStatus.FAILED
                assert orchestrator.state.status == WorkflowStatus.FAILED

    @pytest.mark.asyncio
    async def test_workflow_step_failure(
        self, mock_redis: MagicMock, mock_rabbitmq: MagicMock
    ) -> None:
        """Test handling step failure."""
        with patch("src.core.orchestrator.get_redis_client", return_value=mock_redis):
            with patch(
                "src.core.orchestrator.get_rabbitmq_client", return_value=mock_rabbitmq
            ):
                orchestrator = Orchestrator(company_id="test-company")
                await orchestrator.start({})

                await orchestrator.on_step_failed(
                    step_id="collect_context",
                    error="Connection timeout",
                )

                step = orchestrator._get_step("collect_context")
                assert step.status == WorkflowStatus.FAILED
                assert step.error == "Connection timeout"
                assert orchestrator.state.status == WorkflowStatus.FAILED

    @pytest.mark.asyncio
    async def test_workflow_load_from_redis(
        self, mock_redis: MagicMock
    ) -> None:
        """Test loading workflow from Redis."""
        stored_state = {
            "workflow_id": "wf-123",
            "company_id": "test-company",
            "session_id": "session-456",
            "status": "running",
            "steps": [
                {
                    "step_id": "collect_context",
                    "agent_type": "context_collector",
                    "status": "completed",
                    "depends_on": [],
                    "input_data": {},
                    "output_data": {"company": {}},
                }
            ],
            "current_step_id": "generate_talent_profile",
            "context": {},
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
        mock_redis.get_json.return_value = stored_state

        with patch("src.core.orchestrator.get_redis_client", return_value=mock_redis):
            orchestrator = await Orchestrator.load("wf-123")

            assert orchestrator is not None
            assert orchestrator.state.workflow_id == "wf-123"
            assert orchestrator.state.company_id == "test-company"

"""
Orchestrator for coordinating multi-agent workflows.

Manages agent lifecycle, task distribution, and workflow state
for HR policy generation processes.
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from src.services import get_rabbitmq_client, get_redis_client
from src.utils import get_logger

logger = get_logger(__name__)


class WorkflowStatus(str, Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    WAITING_HITL = "waiting_hitl"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStep(BaseModel):
    """A step in the workflow."""

    step_id: str
    agent_type: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    depends_on: list[str] = Field(default_factory=list)
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None


class WorkflowState(BaseModel):
    """Complete workflow state."""

    workflow_id: str = Field(default_factory=lambda: str(uuid4()))
    company_id: str
    session_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    steps: list[WorkflowStep] = Field(default_factory=list)
    current_step_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Orchestrator:
    """
    Workflow orchestrator for HR policy generation.

    Manages the execution flow:
    1. Company context collection
    2. Ideal talent profile generation
    3. Grading system design
    4. Evaluation system design
    5. Compensation system design
    """

    # Default workflow definition
    DEFAULT_WORKFLOW_STEPS = [
        WorkflowStep(
            step_id="collect_context",
            agent_type="context_collector",
            input_data={},
        ),
        WorkflowStep(
            step_id="generate_talent_profile",
            agent_type="talent_profile_generator",
            depends_on=["collect_context"],
        ),
        WorkflowStep(
            step_id="design_grading",
            agent_type="grading_designer",
            depends_on=["generate_talent_profile"],
        ),
        WorkflowStep(
            step_id="design_evaluation",
            agent_type="evaluation_designer",
            depends_on=["design_grading"],
        ),
        WorkflowStep(
            step_id="design_compensation",
            agent_type="compensation_designer",
            depends_on=["design_evaluation"],
        ),
    ]

    def __init__(self, company_id: str, session_id: str | None = None) -> None:
        self.state = WorkflowState(
            company_id=company_id,
            session_id=session_id or str(uuid4()),
            steps=[step.model_copy() for step in self.DEFAULT_WORKFLOW_STEPS],
        )
        self._agent_instances: dict[str, Any] = {}

    @property
    def workflow_id(self) -> str:
        """Get the workflow ID."""
        return self.state.workflow_id

    async def _save_state(self) -> None:
        """Save workflow state to Redis."""
        self.state.updated_at = datetime.utcnow()
        redis = await get_redis_client()
        await redis.set_json(
            f"workflow:{self.workflow_id}",
            self.state.model_dump(mode="json"),
            expire_seconds=86400 * 7,  # 7 days
        )

    @classmethod
    async def load(cls, workflow_id: str) -> "Orchestrator | None":
        """Load an existing workflow from Redis."""
        redis = await get_redis_client()
        data = await redis.get_json(f"workflow:{workflow_id}")
        if not data:
            return None

        state = WorkflowState(**data)
        orchestrator = cls(state.company_id, state.session_id)
        orchestrator.state = state
        return orchestrator

    def _get_step(self, step_id: str) -> WorkflowStep | None:
        """Get a step by ID."""
        for step in self.state.steps:
            if step.step_id == step_id:
                return step
        return None

    def _get_next_steps(self) -> list[WorkflowStep]:
        """Get steps that are ready to execute."""
        ready_steps = []
        for step in self.state.steps:
            if step.status != WorkflowStatus.PENDING:
                continue

            # Check if all dependencies are completed
            deps_completed = all(
                self._get_step(dep_id)
                and self._get_step(dep_id).status == WorkflowStatus.COMPLETED
                for dep_id in step.depends_on
            )

            if deps_completed:
                ready_steps.append(step)

        return ready_steps

    def _collect_step_outputs(self, step: WorkflowStep) -> dict[str, Any]:
        """Collect outputs from dependency steps."""
        outputs: dict[str, Any] = {}
        for dep_id in step.depends_on:
            dep_step = self._get_step(dep_id)
            if dep_step and dep_step.output_data:
                outputs[dep_id] = dep_step.output_data
        return outputs

    async def start(self, initial_data: dict[str, Any]) -> None:
        """Start the workflow with initial data."""
        self.state.status = WorkflowStatus.RUNNING
        self.state.context["initial_data"] = initial_data

        # Set initial data for first step
        if self.state.steps:
            self.state.steps[0].input_data = initial_data

        await self._save_state()

        logger.info(
            "workflow_started",
            workflow_id=self.workflow_id,
            company_id=self.state.company_id,
        )

        # Publish start event
        rabbitmq = await get_rabbitmq_client()
        await rabbitmq.publish_orchestrator_event(
            {
                "event": "workflow_started",
                "workflow_id": self.workflow_id,
                "company_id": self.state.company_id,
                "session_id": self.state.session_id,
            }
        )

    async def execute_step(self, step_id: str) -> bool:
        """Execute a single workflow step."""
        step = self._get_step(step_id)
        if not step:
            logger.error("step_not_found", step_id=step_id)
            return False

        step.status = WorkflowStatus.RUNNING
        step.started_at = datetime.utcnow()
        self.state.current_step_id = step_id
        await self._save_state()

        logger.info(
            "step_started",
            workflow_id=self.workflow_id,
            step_id=step_id,
            agent_type=step.agent_type,
        )

        # Collect inputs from dependencies
        dep_outputs = self._collect_step_outputs(step)
        step.input_data.update(dep_outputs)

        # Dispatch task to agent
        rabbitmq = await get_rabbitmq_client()
        await rabbitmq.publish_agent_task(
            step.agent_type,
            {
                "workflow_id": self.workflow_id,
                "step_id": step_id,
                "company_id": self.state.company_id,
                "session_id": self.state.session_id,
                "input_data": step.input_data,
            },
        )

        return True

    async def on_step_completed(
        self,
        step_id: str,
        output_data: dict[str, Any],
        requires_hitl: bool = False,
    ) -> None:
        """Handle step completion."""
        step = self._get_step(step_id)
        if not step:
            return

        step.output_data = output_data
        step.completed_at = datetime.utcnow()

        if requires_hitl:
            step.status = WorkflowStatus.WAITING_HITL
            self.state.status = WorkflowStatus.WAITING_HITL
        else:
            step.status = WorkflowStatus.COMPLETED

        await self._save_state()

        logger.info(
            "step_completed",
            workflow_id=self.workflow_id,
            step_id=step_id,
            requires_hitl=requires_hitl,
        )

        # Check if workflow is complete
        if not requires_hitl:
            await self._check_workflow_completion()

    async def on_step_failed(self, step_id: str, error: str) -> None:
        """Handle step failure."""
        step = self._get_step(step_id)
        if not step:
            return

        step.status = WorkflowStatus.FAILED
        step.error = error
        step.completed_at = datetime.utcnow()
        self.state.status = WorkflowStatus.FAILED

        await self._save_state()

        logger.error(
            "step_failed",
            workflow_id=self.workflow_id,
            step_id=step_id,
            error=error,
        )

    async def on_hitl_decision(
        self, step_id: str, approved: bool, feedback: str | None = None
    ) -> None:
        """Handle HITL decision."""
        step = self._get_step(step_id)
        if not step:
            return

        if approved:
            step.status = WorkflowStatus.COMPLETED
            self.state.status = WorkflowStatus.RUNNING
            logger.info(
                "hitl_approved",
                workflow_id=self.workflow_id,
                step_id=step_id,
            )
            await self._check_workflow_completion()
        else:
            step.status = WorkflowStatus.FAILED
            step.error = f"HITL rejected: {feedback or 'No feedback'}"
            self.state.status = WorkflowStatus.FAILED
            logger.info(
                "hitl_rejected",
                workflow_id=self.workflow_id,
                step_id=step_id,
                feedback=feedback,
            )

        await self._save_state()

    async def _check_workflow_completion(self) -> None:
        """Check if workflow is complete and start next steps."""
        # Check if all steps are completed
        all_completed = all(
            step.status == WorkflowStatus.COMPLETED for step in self.state.steps
        )

        if all_completed:
            self.state.status = WorkflowStatus.COMPLETED
            await self._save_state()
            logger.info(
                "workflow_completed",
                workflow_id=self.workflow_id,
            )
            return

        # Start next available steps
        next_steps = self._get_next_steps()
        for step in next_steps:
            await self.execute_step(step.step_id)

    async def run_to_completion(self) -> WorkflowState:
        """
        Run the workflow to completion (or until HITL pause).

        This is a simplified synchronous execution for testing.
        In production, steps would be executed via message queue.
        """
        while self.state.status == WorkflowStatus.RUNNING:
            next_steps = self._get_next_steps()
            if not next_steps:
                break

            for step in next_steps:
                await self.execute_step(step.step_id)

            # Wait for step completion (in real implementation, this would be event-driven)
            await asyncio.sleep(0.1)

        return self.state

    def get_progress(self) -> dict[str, Any]:
        """Get workflow progress summary."""
        completed = sum(
            1 for s in self.state.steps if s.status == WorkflowStatus.COMPLETED
        )
        total = len(self.state.steps)

        return {
            "workflow_id": self.workflow_id,
            "status": self.state.status.value,
            "progress": f"{completed}/{total}",
            "percent": round(completed / total * 100) if total > 0 else 0,
            "current_step": self.state.current_step_id,
            "steps": [
                {
                    "step_id": s.step_id,
                    "agent_type": s.agent_type,
                    "status": s.status.value,
                }
                for s in self.state.steps
            ],
        }

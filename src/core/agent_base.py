"""
Base agent class for all HR policy agents.

Provides common functionality for agent lifecycle, state management,
LLM interaction, and HITL integration.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

import google.generativeai as genai
from pydantic import BaseModel, Field

from src.config import get_settings
from src.services import get_rabbitmq_client, get_redis_client
from src.utils import get_logger

logger = get_logger(__name__)


class AgentStatus(str, Enum):
    """Agent execution status."""

    IDLE = "idle"
    RUNNING = "running"
    WAITING_HITL = "waiting_hitl"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentState(BaseModel):
    """Agent state model."""

    agent_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_type: str
    status: AgentStatus = AgentStatus.IDLE
    company_id: str | None = None
    session_id: str | None = None
    current_step: str = ""
    context: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error: str | None = None


class AgentResult(BaseModel):
    """Result from agent execution."""

    success: bool
    data: dict[str, Any] = Field(default_factory=dict)
    requires_hitl: bool = False
    hitl_gate_id: str | None = None
    error: str | None = None


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    agent_type: str = "base"

    def __init__(self, company_id: str, session_id: str | None = None) -> None:
        self.state = AgentState(
            agent_type=self.agent_type,
            company_id=company_id,
            session_id=session_id,
        )
        self._gemini_model: genai.GenerativeModel | None = None
        self._heartbeat_task: asyncio.Task[None] | None = None

    @property
    def agent_id(self) -> str:
        """Get the agent ID."""
        return self.state.agent_id

    def _get_gemini_model(self) -> genai.GenerativeModel:
        """Get or create Gemini model."""
        if self._gemini_model is None:
            settings = get_settings()
            genai.configure(api_key=settings.gemini_api_key)
            self._gemini_model = genai.GenerativeModel(settings.gemini_model)
        return self._gemini_model

    async def _save_state(self) -> None:
        """Save agent state to Redis."""
        self.state.updated_at = datetime.utcnow()
        redis = await get_redis_client()
        await redis.set_agent_state(
            self.agent_id,
            self.state.model_dump(mode="json"),
        )

    async def _start_heartbeat(self) -> None:
        """Start heartbeat loop."""
        settings = get_settings()

        async def heartbeat_loop() -> None:
            redis = await get_redis_client()
            while True:
                await redis.update_agent_heartbeat(self.agent_id)
                await asyncio.sleep(settings.agent_heartbeat_interval_seconds)

        self._heartbeat_task = asyncio.create_task(heartbeat_loop())

    async def _stop_heartbeat(self) -> None:
        """Stop heartbeat loop."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None

    async def call_llm(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """Call Gemini API with the given prompts."""
        model = self._get_gemini_model()

        # Combine system prompt and user message for Gemini
        full_prompt = f"{system_prompt}\n\n{user_message}"

        generation_config = genai.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        response = await model.generate_content_async(
            full_prompt,
            generation_config=generation_config,
        )
        return response.text

    async def request_hitl_approval(
        self,
        gate_id: str,
        title: str,
        description: str,
        data: dict[str, Any],
        timeout_hours: int | None = None,
    ) -> None:
        """Request HITL approval and wait."""
        settings = get_settings()
        timeout = timeout_hours or settings.hitl_default_timeout_hours

        self.state.status = AgentStatus.WAITING_HITL
        self.state.current_step = f"waiting_hitl:{gate_id}"
        await self._save_state()

        rabbitmq = await get_rabbitmq_client()
        await rabbitmq.publish_hitl_request(
            {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "company_id": self.state.company_id,
                "session_id": self.state.session_id,
                "gate_id": gate_id,
                "title": title,
                "description": description,
                "data": data,
                "timeout_hours": timeout,
                "requested_at": datetime.utcnow().isoformat(),
            }
        )

        logger.info(
            "hitl_requested",
            agent_id=self.agent_id,
            gate_id=gate_id,
            timeout_hours=timeout,
        )

    @abstractmethod
    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        """Execute the agent's main logic. Must be implemented by subclasses."""
        ...

    async def run(self, input_data: dict[str, Any]) -> AgentResult:
        """Run the agent with lifecycle management."""
        try:
            await self._start_heartbeat()
            self.state.status = AgentStatus.RUNNING
            self.state.context["input"] = input_data
            await self._save_state()

            logger.info(
                "agent_started",
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                company_id=self.state.company_id,
            )

            result = await self.execute(input_data)

            if result.requires_hitl:
                self.state.status = AgentStatus.WAITING_HITL
            elif result.success:
                self.state.status = AgentStatus.COMPLETED
            else:
                self.state.status = AgentStatus.FAILED
                self.state.error = result.error

            self.state.context["output"] = result.data
            await self._save_state()

            logger.info(
                "agent_finished",
                agent_id=self.agent_id,
                status=self.state.status.value,
                success=result.success,
            )

            return result

        except Exception as e:
            self.state.status = AgentStatus.FAILED
            self.state.error = str(e)
            await self._save_state()

            logger.error(
                "agent_error",
                agent_id=self.agent_id,
                error=str(e),
            )

            return AgentResult(success=False, error=str(e))

        finally:
            await self._stop_heartbeat()

    async def resume_after_hitl(
        self, approved: bool, feedback: str | None = None
    ) -> AgentResult:
        """Resume agent execution after HITL decision."""
        self.state.context["hitl_approved"] = approved
        self.state.context["hitl_feedback"] = feedback

        if not approved:
            self.state.status = AgentStatus.FAILED
            self.state.error = f"HITL rejected: {feedback or 'No feedback provided'}"
            await self._save_state()
            return AgentResult(success=False, error=self.state.error)

        self.state.status = AgentStatus.RUNNING
        await self._save_state()

        # Continue execution - subclasses should override this if needed
        return AgentResult(success=True, data=self.state.context.get("output", {}))

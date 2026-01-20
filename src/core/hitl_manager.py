"""
Human-in-the-Loop (HITL) manager for approval workflows.

Manages approval gates, notifications, and decision tracking
for critical HR policy decisions.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from src.config import get_settings
from src.services import get_rabbitmq_client, get_redis_client
from src.utils import get_logger

logger = get_logger(__name__)


class HITLGateId(str, Enum):
    """Predefined HITL approval gates."""

    # Company context approval
    COMPANY_CONTEXT = "HITL-001"

    # Ideal talent profile approval
    IDEAL_TALENT_PROFILE = "HITL-002"

    # Grading system approval
    GRADING_SYSTEM = "HITL-003"

    # Evaluation system approval
    EVALUATION_SYSTEM = "HITL-004"

    # Compensation system approval
    COMPENSATION_SYSTEM = "HITL-005"

    # Final review before generation
    FINAL_REVIEW = "HITL-006"

    # Output confirmation
    OUTPUT_CONFIRMATION = "HITL-007"


class HITLStatus(str, Enum):
    """HITL request status."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class HITLRequest(BaseModel):
    """HITL approval request."""

    request_id: str = Field(default_factory=lambda: str(uuid4()))
    gate_id: str
    agent_id: str
    agent_type: str
    workflow_id: str | None = None
    step_id: str | None = None
    company_id: str
    session_id: str | None = None
    title: str
    description: str
    data: dict[str, Any] = Field(default_factory=dict)
    status: HITLStatus = HITLStatus.PENDING
    timeout_hours: int
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    decided_at: datetime | None = None
    decided_by: str | None = None
    feedback: str | None = None


class HITLDecision(BaseModel):
    """HITL decision record."""

    request_id: str
    approved: bool
    feedback: str | None = None
    decided_by: str
    decided_at: datetime = Field(default_factory=datetime.utcnow)


class HITLManager:
    """Manages Human-in-the-Loop approval workflows."""

    def __init__(self) -> None:
        self._pending_requests: dict[str, HITLRequest] = {}

    async def create_request(
        self,
        gate_id: str,
        agent_id: str,
        agent_type: str,
        company_id: str,
        title: str,
        description: str,
        data: dict[str, Any],
        workflow_id: str | None = None,
        step_id: str | None = None,
        session_id: str | None = None,
        timeout_hours: int | None = None,
    ) -> HITLRequest:
        """Create a new HITL approval request."""
        settings = get_settings()
        timeout = timeout_hours or settings.hitl_default_timeout_hours

        request = HITLRequest(
            gate_id=gate_id,
            agent_id=agent_id,
            agent_type=agent_type,
            workflow_id=workflow_id,
            step_id=step_id,
            company_id=company_id,
            session_id=session_id,
            title=title,
            description=description,
            data=data,
            timeout_hours=timeout,
            expires_at=datetime.utcnow() + timedelta(hours=timeout),
        )

        # Store in Redis
        redis = await get_redis_client()
        await redis.set_json(
            f"hitl:request:{request.request_id}",
            request.model_dump(mode="json"),
            expire_seconds=timeout * 3600 + 86400,  # timeout + 1 day buffer
        )

        # Add to pending list for company
        await redis.client.sadd(
            f"hitl:pending:{company_id}",
            request.request_id,
        )

        logger.info(
            "hitl_request_created",
            request_id=request.request_id,
            gate_id=gate_id,
            company_id=company_id,
            expires_at=request.expires_at.isoformat() if request.expires_at else None,
        )

        return request

    async def get_request(self, request_id: str) -> HITLRequest | None:
        """Get a HITL request by ID."""
        redis = await get_redis_client()
        data = await redis.get_json(f"hitl:request:{request_id}")
        if data:
            return HITLRequest(**data)
        return None

    async def get_pending_requests(self, company_id: str) -> list[HITLRequest]:
        """Get all pending requests for a company."""
        redis = await get_redis_client()
        request_ids = await redis.client.smembers(f"hitl:pending:{company_id}")

        requests = []
        for request_id in request_ids:
            request = await self.get_request(request_id)
            if request and request.status == HITLStatus.PENDING:
                # Check expiration
                if request.expires_at and datetime.utcnow() > request.expires_at:
                    await self._expire_request(request)
                else:
                    requests.append(request)

        return sorted(requests, key=lambda r: r.requested_at, reverse=True)

    async def submit_decision(
        self,
        request_id: str,
        approved: bool,
        feedback: str | None = None,
        decided_by: str = "system",
    ) -> HITLDecision | None:
        """Submit a decision for a HITL request."""
        request = await self.get_request(request_id)
        if not request:
            logger.warning("hitl_request_not_found", request_id=request_id)
            return None

        if request.status != HITLStatus.PENDING:
            logger.warning(
                "hitl_request_not_pending",
                request_id=request_id,
                status=request.status.value,
            )
            return None

        # Update request
        request.status = HITLStatus.APPROVED if approved else HITLStatus.REJECTED
        request.decided_at = datetime.utcnow()
        request.decided_by = decided_by
        request.feedback = feedback

        # Save updated request
        redis = await get_redis_client()
        await redis.set_json(
            f"hitl:request:{request_id}",
            request.model_dump(mode="json"),
        )

        # Remove from pending
        await redis.client.srem(f"hitl:pending:{request.company_id}", request_id)

        # Create decision record
        decision = HITLDecision(
            request_id=request_id,
            approved=approved,
            feedback=feedback,
            decided_by=decided_by,
        )

        # Publish decision event
        rabbitmq = await get_rabbitmq_client()
        await rabbitmq.publish_hitl_response(
            {
                "request_id": request_id,
                "agent_id": request.agent_id,
                "workflow_id": request.workflow_id,
                "step_id": request.step_id,
                "approved": approved,
                "feedback": feedback,
                "decided_by": decided_by,
                "decided_at": decision.decided_at.isoformat(),
            }
        )

        logger.info(
            "hitl_decision_submitted",
            request_id=request_id,
            approved=approved,
            decided_by=decided_by,
        )

        return decision

    async def _expire_request(self, request: HITLRequest) -> None:
        """Mark a request as expired."""
        request.status = HITLStatus.EXPIRED
        request.decided_at = datetime.utcnow()

        redis = await get_redis_client()
        await redis.set_json(
            f"hitl:request:{request.request_id}",
            request.model_dump(mode="json"),
        )
        await redis.client.srem(
            f"hitl:pending:{request.company_id}",
            request.request_id,
        )

        logger.info(
            "hitl_request_expired",
            request_id=request.request_id,
            gate_id=request.gate_id,
        )

    async def cancel_request(self, request_id: str) -> bool:
        """Cancel a pending HITL request."""
        request = await self.get_request(request_id)
        if not request or request.status != HITLStatus.PENDING:
            return False

        request.status = HITLStatus.CANCELLED
        request.decided_at = datetime.utcnow()

        redis = await get_redis_client()
        await redis.set_json(
            f"hitl:request:{request_id}",
            request.model_dump(mode="json"),
        )
        await redis.client.srem(
            f"hitl:pending:{request.company_id}",
            request_id,
        )

        logger.info("hitl_request_cancelled", request_id=request_id)
        return True

    def get_gate_info(self, gate_id: str) -> dict[str, Any]:
        """Get information about a HITL gate."""
        gate_info = {
            HITLGateId.COMPANY_CONTEXT.value: {
                "name": "Company Context Approval",
                "description": "企業情報と要件の確認",
                "required": True,
            },
            HITLGateId.IDEAL_TALENT_PROFILE.value: {
                "name": "Ideal Talent Profile Approval",
                "description": "求める人材像の承認",
                "required": True,
            },
            HITLGateId.GRADING_SYSTEM.value: {
                "name": "Grading System Approval",
                "description": "等級制度案の承認",
                "required": True,
            },
            HITLGateId.EVALUATION_SYSTEM.value: {
                "name": "Evaluation System Approval",
                "description": "評価制度案の承認",
                "required": True,
            },
            HITLGateId.COMPENSATION_SYSTEM.value: {
                "name": "Compensation System Approval",
                "description": "報酬制度案の承認",
                "required": True,
            },
            HITLGateId.FINAL_REVIEW.value: {
                "name": "Final Review",
                "description": "最終確認",
                "required": True,
            },
            HITLGateId.OUTPUT_CONFIRMATION.value: {
                "name": "Output Confirmation",
                "description": "出力確認",
                "required": False,
            },
        }
        return gate_info.get(gate_id, {"name": gate_id, "description": "", "required": False})


# Singleton instance
_hitl_manager: HITLManager | None = None


def get_hitl_manager() -> HITLManager:
    """Get HITL manager singleton."""
    global _hitl_manager
    if _hitl_manager is None:
        _hitl_manager = HITLManager()
    return _hitl_manager

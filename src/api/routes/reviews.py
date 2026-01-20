"""HITL review API routes."""

from fastapi import APIRouter, HTTPException

from src.api.schemas import HITLDecisionRequest, HITLDecisionResponse, HITLRequestResponse
from src.core import Orchestrator, get_hitl_manager
from src.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/pending/{company_id}", response_model=list[HITLRequestResponse])
async def get_pending_reviews(company_id: str) -> list[HITLRequestResponse]:
    """Get all pending HITL requests for a company."""
    hitl_manager = get_hitl_manager()
    requests = await hitl_manager.get_pending_requests(company_id)

    return [
        HITLRequestResponse(
            request_id=req.request_id,
            gate_id=req.gate_id,
            title=req.title,
            description=req.description,
            data=req.data,
            status=req.status.value,
            expires_at=req.expires_at,
            requested_at=req.requested_at,
        )
        for req in requests
    ]


@router.get("/{request_id}", response_model=HITLRequestResponse)
async def get_review(request_id: str) -> HITLRequestResponse:
    """Get a specific HITL request."""
    hitl_manager = get_hitl_manager()
    request = await hitl_manager.get_request(request_id)

    if not request:
        raise HTTPException(status_code=404, detail="Review request not found")

    return HITLRequestResponse(
        request_id=request.request_id,
        gate_id=request.gate_id,
        title=request.title,
        description=request.description,
        data=request.data,
        status=request.status.value,
        expires_at=request.expires_at,
        requested_at=request.requested_at,
    )


@router.post("/{request_id}/decision", response_model=HITLDecisionResponse)
async def submit_decision(
    request_id: str,
    decision: HITLDecisionRequest,
) -> HITLDecisionResponse:
    """Submit a decision for a HITL request."""
    hitl_manager = get_hitl_manager()

    # Get the request to find the workflow
    request = await hitl_manager.get_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Review request not found")

    # Submit decision
    result = await hitl_manager.submit_decision(
        request_id=request_id,
        approved=decision.approved,
        feedback=decision.feedback,
        decided_by="user",  # In production, get from auth context
    )

    if not result:
        raise HTTPException(status_code=400, detail="Could not process decision")

    # Update workflow if exists
    if request.workflow_id and request.step_id:
        orchestrator = await Orchestrator.load(request.workflow_id)
        if orchestrator:
            await orchestrator.on_hitl_decision(
                request.step_id,
                decision.approved,
                decision.feedback,
            )

    logger.info(
        "hitl_decision_submitted",
        request_id=request_id,
        approved=decision.approved,
    )

    return HITLDecisionResponse(
        request_id=request_id,
        approved=decision.approved,
        decided_at=result.decided_at,
    )


@router.post("/{request_id}/cancel")
async def cancel_review(request_id: str) -> dict[str, str]:
    """Cancel a pending HITL request."""
    hitl_manager = get_hitl_manager()

    success = await hitl_manager.cancel_request(request_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Could not cancel request (not found or not pending)",
        )

    logger.info("hitl_request_cancelled", request_id=request_id)

    return {"status": "cancelled", "request_id": request_id}

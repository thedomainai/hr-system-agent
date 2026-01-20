"""Policy generation workflow API routes."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException

from src.api.schemas import PolicyOutputResponse, WorkflowResponse, WorkflowStartRequest
from src.core import Orchestrator
from src.services import get_redis_client
from src.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/policies", tags=["policies"])


@router.post("/workflows", response_model=WorkflowResponse)
async def start_workflow(request: WorkflowStartRequest) -> WorkflowResponse:
    """Start a new policy generation workflow."""
    redis = await get_redis_client()

    # Verify company exists
    company_data = await redis.get_json(f"company:{request.company_id}")
    if not company_data:
        raise HTTPException(status_code=404, detail="Company not found")

    # Create orchestrator
    orchestrator = Orchestrator(request.company_id)

    # Start workflow with company data
    await orchestrator.start(company_data)

    # Execute first step
    if orchestrator.state.steps:
        await orchestrator.execute_step(orchestrator.state.steps[0].step_id)

    progress = orchestrator.get_progress()

    logger.info(
        "workflow_started",
        workflow_id=orchestrator.workflow_id,
        company_id=request.company_id,
    )

    return WorkflowResponse(
        workflow_id=progress["workflow_id"],
        status=progress["status"],
        progress=progress["progress"],
        percent=progress["percent"],
        current_step=progress["current_step"],
        steps=progress["steps"],
    )


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_status(workflow_id: str) -> WorkflowResponse:
    """Get workflow status."""
    orchestrator = await Orchestrator.load(workflow_id)

    if not orchestrator:
        raise HTTPException(status_code=404, detail="Workflow not found")

    progress = orchestrator.get_progress()

    return WorkflowResponse(
        workflow_id=progress["workflow_id"],
        status=progress["status"],
        progress=progress["progress"],
        percent=progress["percent"],
        current_step=progress["current_step"],
        steps=progress["steps"],
    )


@router.get("/workflows/{workflow_id}/output", response_model=PolicyOutputResponse)
async def get_workflow_output(workflow_id: str) -> PolicyOutputResponse:
    """Get the complete policy output from a workflow."""
    orchestrator = await Orchestrator.load(workflow_id)

    if not orchestrator:
        raise HTTPException(status_code=404, detail="Workflow not found")

    redis = await get_redis_client()
    company_data = await redis.get_json(f"company:{orchestrator.state.company_id}")
    company_name = company_data.get("name", "Unknown") if company_data else "Unknown"

    # Collect outputs from all steps
    output: dict[str, Any] = {
        "company_id": orchestrator.state.company_id,
        "company_name": company_name,
        "generated_at": datetime.utcnow(),
    }

    for step in orchestrator.state.steps:
        if step.output_data:
            if step.step_id == "generate_talent_profile":
                output["ideal_talent_profile"] = step.output_data.get("talent_profile")
            elif step.step_id == "design_grading":
                output["grading_system"] = step.output_data.get("grading_system")
            elif step.step_id == "design_evaluation":
                output["evaluation_system"] = step.output_data.get("evaluation_system")
            elif step.step_id == "design_compensation":
                output["compensation_system"] = step.output_data.get("compensation_system")

    return PolicyOutputResponse(**output)


@router.post("/workflows/{workflow_id}/steps/{step_id}/retry")
async def retry_workflow_step(workflow_id: str, step_id: str) -> WorkflowResponse:
    """Retry a failed workflow step."""
    orchestrator = await Orchestrator.load(workflow_id)

    if not orchestrator:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Find the step
    step = orchestrator._get_step(step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")

    # Reset step and re-execute
    from src.core import WorkflowStatus
    step.status = WorkflowStatus.PENDING
    step.error = None
    orchestrator.state.status = WorkflowStatus.RUNNING

    await orchestrator._save_state()
    await orchestrator.execute_step(step_id)

    progress = orchestrator.get_progress()

    logger.info(
        "workflow_step_retried",
        workflow_id=workflow_id,
        step_id=step_id,
    )

    return WorkflowResponse(
        workflow_id=progress["workflow_id"],
        status=progress["status"],
        progress=progress["progress"],
        percent=progress["percent"],
        current_step=progress["current_step"],
        steps=progress["steps"],
    )

"""
End-to-End tests for the complete HR Policy Advisor workflow.

These tests verify the entire flow from company registration through
all HITL gates to final policy output.
"""

import pytest
from httpx import AsyncClient

from tests.conftest import (
    create_test_company,
    get_workflow_status,
    start_workflow,
)

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]


# ============================================================================
# Test: Company Registration Flow
# ============================================================================

class TestCompanyRegistration:
    """Test company registration API."""

    async def test_create_company_success(
        self,
        e2e_client: AsyncClient,
        sample_company_data: dict,
    ) -> None:
        """Test successful company creation."""
        response = await e2e_client.post(
            "/api/v1/companies",
            json=sample_company_data,
        )

        assert response.status_code == 200
        data = response.json()

        assert "company_id" in data
        assert data["name"] == sample_company_data["name"]
        assert data["industry"] == sample_company_data["industry"]
        assert data["employee_count"] == sample_company_data["employee_count"]
        assert "created_at" in data

    async def test_create_company_with_minimal_data(
        self,
        e2e_client: AsyncClient,
    ) -> None:
        """Test company creation with minimal required data."""
        minimal_data = {
            "name": "Minimal Company",
            "industry": "consulting",
            "employee_count": 50,
        }

        response = await e2e_client.post(
            "/api/v1/companies",
            json=minimal_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Minimal Company"
        assert data["size"] == "startup"  # 50 employees = startup

    async def test_get_company_by_id(
        self,
        e2e_client: AsyncClient,
        sample_company_data: dict,
    ) -> None:
        """Test retrieving a company by ID."""
        # First create a company
        create_response = await e2e_client.post(
            "/api/v1/companies",
            json=sample_company_data,
        )
        company_id = create_response.json()["company_id"]

        # Then retrieve it
        get_response = await e2e_client.get(f"/api/v1/companies/{company_id}")

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["company_id"] == company_id
        assert data["name"] == sample_company_data["name"]

    async def test_get_company_not_found(
        self,
        e2e_client: AsyncClient,
    ) -> None:
        """Test 404 when company not found."""
        response = await e2e_client.get("/api/v1/companies/nonexistent-id")
        assert response.status_code == 404

    async def test_delete_company(
        self,
        e2e_client: AsyncClient,
        sample_company_data: dict,
    ) -> None:
        """Test deleting a company."""
        # Create a company
        create_response = await e2e_client.post(
            "/api/v1/companies",
            json=sample_company_data,
        )
        company_id = create_response.json()["company_id"]

        # Delete it
        delete_response = await e2e_client.delete(f"/api/v1/companies/{company_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["status"] == "deleted"

        # Verify it's gone
        get_response = await e2e_client.get(f"/api/v1/companies/{company_id}")
        assert get_response.status_code == 404


# ============================================================================
# Test: Workflow Start and Status
# ============================================================================

class TestWorkflowManagement:
    """Test workflow creation and status management."""

    async def test_start_workflow(
        self,
        e2e_client: AsyncClient,
        sample_company_data: dict,
    ) -> None:
        """Test starting a policy generation workflow."""
        # Create company
        company = await create_test_company(e2e_client, sample_company_data)
        company_id = company["company_id"]

        # Start workflow
        response = await e2e_client.post(
            "/api/v1/policies/workflows",
            json={"company_id": company_id},
        )

        assert response.status_code == 200
        data = response.json()

        assert "workflow_id" in data
        assert data["status"] in ["running", "pending"]
        assert "steps" in data
        assert len(data["steps"]) > 0

    async def test_start_workflow_company_not_found(
        self,
        e2e_client: AsyncClient,
    ) -> None:
        """Test workflow start with nonexistent company."""
        response = await e2e_client.post(
            "/api/v1/policies/workflows",
            json={"company_id": "nonexistent-company"},
        )
        assert response.status_code == 404

    async def test_get_workflow_status(
        self,
        e2e_client: AsyncClient,
        sample_company_data: dict,
    ) -> None:
        """Test getting workflow status."""
        # Create company and start workflow
        company = await create_test_company(e2e_client, sample_company_data)
        workflow = await start_workflow(e2e_client, company["company_id"])

        # Get status
        status = await get_workflow_status(e2e_client, workflow["workflow_id"])

        assert status["workflow_id"] == workflow["workflow_id"]
        assert "status" in status
        assert "progress" in status
        assert "percent" in status
        assert "steps" in status

    async def test_get_workflow_not_found(
        self,
        e2e_client: AsyncClient,
    ) -> None:
        """Test 404 when workflow not found."""
        response = await e2e_client.get(
            "/api/v1/policies/workflows/nonexistent-workflow"
        )
        assert response.status_code == 404


# ============================================================================
# Test: HITL Review Flow
# ============================================================================

class TestHITLReviewFlow:
    """Test Human-in-the-Loop review functionality."""

    async def test_get_pending_reviews_empty(
        self,
        e2e_client: AsyncClient,
    ) -> None:
        """Test getting pending reviews when none exist."""
        response = await e2e_client.get("/api/v1/reviews/pending/test-company-id")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_review_not_found(
        self,
        e2e_client: AsyncClient,
    ) -> None:
        """Test 404 when review not found."""
        response = await e2e_client.get("/api/v1/reviews/nonexistent-review")
        assert response.status_code == 404

    async def test_cancel_review_not_found(
        self,
        e2e_client: AsyncClient,
    ) -> None:
        """Test canceling nonexistent review."""
        response = await e2e_client.post("/api/v1/reviews/nonexistent-review/cancel")
        assert response.status_code == 400


# ============================================================================
# Test: Health Check
# ============================================================================

class TestHealthCheck:
    """Test health check endpoint."""

    async def test_health_check(
        self,
        e2e_client: AsyncClient,
    ) -> None:
        """Test health check returns healthy status."""
        response = await e2e_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data

    async def test_root_endpoint(
        self,
        e2e_client: AsyncClient,
    ) -> None:
        """Test root endpoint returns app info."""
        response = await e2e_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


# ============================================================================
# Test: Complete Workflow Integration
# ============================================================================

class TestCompleteWorkflowIntegration:
    """Test complete workflow from registration to output."""

    @pytest.mark.slow
    async def test_company_registration_to_workflow_start(
        self,
        e2e_client: AsyncClient,
        sample_company_data: dict,
    ) -> None:
        """Test flow from company registration to workflow start."""
        # Step 1: Register company
        company = await create_test_company(e2e_client, sample_company_data)
        assert company["company_id"]
        company_id = company["company_id"]

        # Step 2: Verify company exists
        get_response = await e2e_client.get(f"/api/v1/companies/{company_id}")
        assert get_response.status_code == 200

        # Step 3: Start workflow
        workflow = await start_workflow(e2e_client, company_id)
        assert workflow["workflow_id"]
        assert workflow["status"] in ["running", "pending"]

        # Step 4: Check workflow status
        status = await get_workflow_status(e2e_client, workflow["workflow_id"])
        assert status["workflow_id"] == workflow["workflow_id"]

    @pytest.mark.slow
    async def test_workflow_steps_defined(
        self,
        e2e_client: AsyncClient,
        sample_company_data: dict,
    ) -> None:
        """Test that workflow has all expected steps."""
        company = await create_test_company(e2e_client, sample_company_data)
        workflow = await start_workflow(e2e_client, company["company_id"])

        expected_steps = [
            "collect_context",
            "generate_talent_profile",
            "design_grading",
            "design_evaluation",
            "design_compensation",
        ]

        step_ids = [step["step_id"] for step in workflow["steps"]]

        for expected_step in expected_steps:
            assert expected_step in step_ids, f"Missing step: {expected_step}"


# ============================================================================
# Test: Workflow Output
# ============================================================================

class TestWorkflowOutput:
    """Test workflow output retrieval."""

    async def test_get_workflow_output(
        self,
        e2e_client: AsyncClient,
        sample_company_data: dict,
    ) -> None:
        """Test getting workflow output."""
        company = await create_test_company(e2e_client, sample_company_data)
        workflow = await start_workflow(e2e_client, company["company_id"])

        response = await e2e_client.get(
            f"/api/v1/policies/workflows/{workflow['workflow_id']}/output"
        )

        assert response.status_code == 200
        data = response.json()

        assert "company_id" in data
        assert "company_name" in data
        assert "generated_at" in data

    async def test_get_workflow_output_not_found(
        self,
        e2e_client: AsyncClient,
    ) -> None:
        """Test 404 when workflow output not found."""
        response = await e2e_client.get(
            "/api/v1/policies/workflows/nonexistent-workflow/output"
        )
        assert response.status_code == 404


# ============================================================================
# Test: Workflow Retry
# ============================================================================

class TestWorkflowRetry:
    """Test workflow step retry functionality."""

    async def test_retry_workflow_step(
        self,
        e2e_client: AsyncClient,
        sample_company_data: dict,
    ) -> None:
        """Test retrying a workflow step."""
        company = await create_test_company(e2e_client, sample_company_data)
        workflow = await start_workflow(e2e_client, company["company_id"])

        # Try to retry the first step
        step_id = workflow["steps"][0]["step_id"]
        response = await e2e_client.post(
            f"/api/v1/policies/workflows/{workflow['workflow_id']}/steps/{step_id}/retry"
        )

        assert response.status_code == 200
        data = response.json()
        assert "workflow_id" in data
        assert "status" in data

    async def test_retry_workflow_not_found(
        self,
        e2e_client: AsyncClient,
    ) -> None:
        """Test 404 when workflow not found for retry."""
        response = await e2e_client.post(
            "/api/v1/policies/workflows/nonexistent-workflow/steps/some-step/retry"
        )
        assert response.status_code == 404


# ============================================================================
# Test: Data Validation
# ============================================================================

class TestDataValidation:
    """Test request data validation."""

    async def test_create_company_missing_required_fields(
        self,
        e2e_client: AsyncClient,
    ) -> None:
        """Test validation error for missing required fields."""
        response = await e2e_client.post(
            "/api/v1/companies",
            json={"name": "Test"},  # Missing industry and employee_count
        )
        assert response.status_code == 422

    async def test_create_company_invalid_employee_count(
        self,
        e2e_client: AsyncClient,
    ) -> None:
        """Test validation error for invalid employee count."""
        response = await e2e_client.post(
            "/api/v1/companies",
            json={
                "name": "Test",
                "industry": "consulting",
                "employee_count": 0,  # Must be >= 1
            },
        )
        assert response.status_code == 422


# ============================================================================
# Test: Company Size Classification
# ============================================================================

class TestCompanySizeClassification:
    """Test company size classification based on employee count."""

    @pytest.mark.parametrize(
        "employee_count,expected_size",
        [
            (10, "startup"),
            (50, "startup"),
            (51, "small"),
            (100, "small"),
            (101, "medium"),
            (300, "medium"),
            (301, "large"),
            (1000, "large"),
        ],
    )
    async def test_company_size_classification(
        self,
        e2e_client: AsyncClient,
        employee_count: int,
        expected_size: str,
    ) -> None:
        """Test that company size is correctly classified."""
        response = await e2e_client.post(
            "/api/v1/companies",
            json={
                "name": f"Test Company {employee_count}",
                "industry": "consulting",
                "employee_count": employee_count,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["size"] == expected_size


# ============================================================================
# Test: Industry Mapping
# ============================================================================

class TestIndustryMapping:
    """Test industry string mapping."""

    @pytest.mark.parametrize(
        "industry_input,expected_industry",
        [
            ("consulting", "consulting"),
            ("CONSULTING", "consulting"),
            ("saas", "saas"),
            ("SaaS", "saas"),
            ("light_freight", "light_freight"),
            ("unknown", "other"),
        ],
    )
    async def test_industry_mapping(
        self,
        e2e_client: AsyncClient,
        industry_input: str,
        expected_industry: str,
    ) -> None:
        """Test that industry is correctly mapped."""
        response = await e2e_client.post(
            "/api/v1/companies",
            json={
                "name": f"Test Company {industry_input}",
                "industry": industry_input,
                "employee_count": 100,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["industry"] == expected_industry

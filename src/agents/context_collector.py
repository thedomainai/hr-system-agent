"""
Context Collector Agent.

Collects and validates company context information
as the first step in the HR policy design process.
"""

from typing import Any

from src.core import AgentResult, BaseAgent, HITLGateId
from src.domain import Company, CompanySize, Industry
from src.utils import get_logger

logger = get_logger(__name__)


class ContextCollectorAgent(BaseAgent):
    """
    Agent responsible for collecting and validating company context.

    This agent:
    1. Validates input company data
    2. Enriches context with industry-specific information
    3. Requests HITL approval for the collected context
    """

    agent_type = "context_collector"

    SYSTEM_PROMPT = """あなたは人事制度設計の専門家です。
企業情報を分析し、人事制度設計に必要なコンテキストを整理してください。

以下の観点で情報を整理してください：
1. 企業の基本情報（業界、規模、成長段階）
2. 企業文化・価値観
3. 現在の人事制度の状況
4. 制度設計の目標と制約

回答はJSON形式で提供してください。"""

    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        """Execute context collection and validation."""
        try:
            # Validate required fields
            required_fields = ["name", "industry", "employee_count"]
            missing = [f for f in required_fields if f not in input_data]
            if missing:
                return AgentResult(
                    success=False,
                    error=f"Missing required fields: {', '.join(missing)}",
                )

            # Parse and validate company data
            company = self._create_company(input_data)

            # Enrich context with AI
            enriched_context = await self._enrich_context(company, input_data)

            # Store in state
            self.state.context["company"] = company.model_dump(mode="json")
            self.state.context["enriched"] = enriched_context

            # Request HITL approval
            await self.request_hitl_approval(
                gate_id=HITLGateId.COMPANY_CONTEXT.value,
                title="企業コンテキストの確認",
                description="収集した企業情報が正しいことを確認してください。",
                data={
                    "company": company.model_dump(mode="json"),
                    "enriched_context": enriched_context,
                },
            )

            return AgentResult(
                success=True,
                data={
                    "company": company.model_dump(mode="json"),
                    "enriched_context": enriched_context,
                },
                requires_hitl=True,
                hitl_gate_id=HITLGateId.COMPANY_CONTEXT.value,
            )

        except Exception as e:
            logger.error("context_collection_failed", error=str(e))
            return AgentResult(success=False, error=str(e))

    def _create_company(self, data: dict[str, Any]) -> Company:
        """Create and validate Company model from input data."""
        # Map industry string to enum
        industry_map = {
            "consulting": Industry.CONSULTING,
            "saas": Industry.SAAS,
            "light_freight": Industry.LIGHT_FREIGHT,
            "コンサルティング": Industry.CONSULTING,
            "SaaS": Industry.SAAS,
            "軽貨物運送業": Industry.LIGHT_FREIGHT,
        }
        industry = industry_map.get(data.get("industry", ""), Industry.OTHER)

        # Determine company size
        employee_count = data.get("employee_count", 0)
        if employee_count <= 50:
            size = CompanySize.STARTUP
        elif employee_count <= 100:
            size = CompanySize.SMALL
        elif employee_count <= 300:
            size = CompanySize.MEDIUM
        else:
            size = CompanySize.LARGE

        return Company(
            name=data["name"],
            industry=industry,
            size=size,
            employee_count=employee_count,
            founding_year=data.get("founding_year"),
            mission=data.get("mission", ""),
            vision=data.get("vision", ""),
            values=data.get("values", []),
            current_grade_count=data.get("current_grade_count"),
            has_existing_hr_system=data.get("has_existing_hr_system", False),
            existing_system_description=data.get("existing_system_description", ""),
            business_model=data.get("business_model", ""),
            target_market=data.get("target_market", ""),
            growth_stage=data.get("growth_stage", ""),
            design_goals=data.get("design_goals", []),
            constraints=data.get("constraints", []),
        )

    async def _enrich_context(
        self, company: Company, raw_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Use AI to enrich and analyze company context."""
        user_message = f"""以下の企業情報を分析し、人事制度設計に必要なコンテキストを整理してください。

企業情報:
- 企業名: {company.name}
- 業界: {company.industry.value}
- 従業員数: {company.employee_count}名
- ミッション: {company.mission}
- ビジョン: {company.vision}
- 価値観: {', '.join(company.values)}
- 事業モデル: {company.business_model}
- 成長段階: {company.growth_stage}
- 既存の人事制度: {'あり' if company.has_existing_hr_system else 'なし'}
- 設計目標: {', '.join(company.design_goals)}

以下の形式でJSONを返してください：
{{
    "industry_characteristics": "業界特性の説明",
    "recommended_grade_count": 数値,
    "key_competencies_for_industry": ["コンピテンシー1", "コンピテンシー2", "コンピテンシー3"],
    "design_considerations": ["考慮事項1", "考慮事項2"],
    "potential_challenges": ["課題1", "課題2"]
}}"""

        try:
            response = await self.call_llm(
                system_prompt=self.SYSTEM_PROMPT,
                user_message=user_message,
                temperature=0.5,
            )

            # Parse JSON response
            import json

            # Extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])

            return {"raw_response": response}

        except Exception as e:
            logger.warning("context_enrichment_failed", error=str(e))
            return {
                "industry_characteristics": f"{company.industry.value}業界",
                "recommended_grade_count": 6,
                "key_competencies_for_industry": [],
                "design_considerations": [],
                "potential_challenges": [],
            }

"""
Compensation Designer Agent.

Designs the compensation system (報酬制度) based on
the grading and evaluation systems.
"""

from typing import Any

from src.core import AgentResult, BaseAgent, HITLGateId
from src.domain import (
    Allowance,
    BonusStructure,
    BonusType,
    CompensationSystem,
    SalaryBand,
    SalaryComponent,
    SalaryType,
)
from src.utils import get_logger

logger = get_logger(__name__)


class CompensationDesignerAgent(BaseAgent):
    """
    Agent responsible for designing the compensation system.

    This agent:
    1. Designs salary bands per grade
    2. Defines bonus structures
    3. Configures allowances
    4. Requests HITL approval
    """

    agent_type = "compensation_designer"

    SYSTEM_PROMPT = """あなたは人事制度設計の専門家です。
企業の報酬制度を設計してください。

報酬制度の設計原則:
1. 市場競争力のある水準
2. 成果に応じた報酬
3. 等級との整合性
4. 透明性と公平性

回答はJSON形式で提供してください。"""

    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        """Execute compensation system design."""
        try:
            # Get context from previous steps
            company_data = input_data.get("collect_context", {}).get("company", {})
            grading_system = input_data.get("design_grading", {}).get("grading_system", {})
            evaluation_system = input_data.get("design_evaluation", {}).get("evaluation_system", {})

            if not all([company_data, grading_system, evaluation_system]):
                return AgentResult(
                    success=False,
                    error="Missing required context from previous steps.",
                )

            # Design compensation system
            compensation_system = await self._design_compensation_system(
                company_data, grading_system, evaluation_system
            )

            # Store in state
            self.state.context["compensation_system"] = compensation_system.model_dump(mode="json")

            # Request HITL approval
            await self.request_hitl_approval(
                gate_id=HITLGateId.COMPENSATION_SYSTEM.value,
                title="報酬制度の確認",
                description="設計された報酬制度が適切かどうか確認してください。",
                data={
                    "compensation_system": compensation_system.model_dump(mode="json"),
                    "company_name": company_data.get("name", "Unknown"),
                },
            )

            return AgentResult(
                success=True,
                data={"compensation_system": compensation_system.model_dump(mode="json")},
                requires_hitl=True,
                hitl_gate_id=HITLGateId.COMPENSATION_SYSTEM.value,
            )

        except Exception as e:
            logger.error("compensation_design_failed", error=str(e))
            return AgentResult(success=False, error=str(e))

    async def _design_compensation_system(
        self,
        company_data: dict[str, Any],
        grading_system: dict[str, Any],
        evaluation_system: dict[str, Any],
    ) -> CompensationSystem:
        """Design the compensation system using AI."""
        grades = grading_system.get("grades", [])
        industry = company_data.get("industry", "")

        user_message = f"""以下の情報に基づいて報酬制度を設計してください。

企業情報:
- 企業名: {company_data.get('name', '')}
- 業界: {industry}
- 従業員数: {company_data.get('employee_count', 0)}名

等級: {[g.get('level') for g in grades]}

以下の形式でJSONを返してください：
{{
    "market_position": "50th percentile",
    "pay_for_performance_ratio": 0.3,
    "annual_increase_budget_percent": 3.0,
    "promotion_increase_percent": 10.0,
    "design_principles": ["原則1", "原則2"],
    "salary_bands": [
        {{
            "grade_level": "J1",
            "min_salary": 3500000,
            "mid_salary": 4000000,
            "max_salary": 4500000
        }}
    ],
    "bonus_months": 4.0,
    "allowances": [
        {{
            "name": "通勤手当",
            "amount": 50000,
            "description": "実費支給（上限5万円）"
        }}
    ]
}}"""

        try:
            response = await self.call_llm(
                system_prompt=self.SYSTEM_PROMPT,
                user_message=user_message,
                temperature=0.5,
                max_tokens=4096,
            )

            import json

            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
            else:
                raise ValueError("Could not parse JSON from response")

            # Build salary bands
            salary_bands = []
            for band_data in data.get("salary_bands", []):
                salary_bands.append(
                    SalaryBand(
                        grade_level=band_data.get("grade_level", ""),
                        min_salary=band_data.get("min_salary", 0),
                        mid_salary=band_data.get("mid_salary", 0),
                        max_salary=band_data.get("max_salary", 0),
                    )
                )

            # Build allowances
            allowances = []
            for allow_data in data.get("allowances", []):
                allowances.append(
                    Allowance(
                        name=allow_data.get("name", ""),
                        description=allow_data.get("description", ""),
                        amount=allow_data.get("amount", 0),
                    )
                )

            # Build bonus structure
            bonus_structures = [
                BonusStructure(
                    name="業績賞与",
                    bonus_type=BonusType.PERFORMANCE,
                    frequency="semi_annual",
                    base_months=data.get("bonus_months", 4.0) / 2,
                )
            ]

            # Build salary components
            salary_components = [
                SalaryComponent(
                    name="基本給",
                    salary_type=SalaryType.BASE,
                    description="等級に基づく固定給与",
                    is_fixed=True,
                ),
                SalaryComponent(
                    name="業績給",
                    salary_type=SalaryType.PERFORMANCE,
                    description="評価に基づく変動給与",
                    is_fixed=False,
                ),
            ]

            return CompensationSystem(
                company_id=company_data.get("company_id", "unknown"),
                salary_bands=salary_bands,
                salary_components=salary_components,
                bonus_structures=bonus_structures,
                total_bonus_months=data.get("bonus_months", 4.0),
                allowances=allowances,
                annual_increase_budget_percent=data.get("annual_increase_budget_percent", 3.0),
                promotion_increase_percent=data.get("promotion_increase_percent", 10.0),
                market_position=data.get("market_position", "50th percentile"),
                pay_for_performance_ratio=data.get("pay_for_performance_ratio", 0.3),
                design_principles=data.get("design_principles", []),
            )

        except Exception as e:
            logger.warning("ai_compensation_design_failed", error=str(e))
            return self._create_default_compensation_system(company_data, grading_system)

    def _create_default_compensation_system(
        self,
        company_data: dict[str, Any],
        grading_system: dict[str, Any],
    ) -> CompensationSystem:
        """Create a default compensation system template."""
        grades = grading_system.get("grades", [])
        industry = company_data.get("industry", "")

        # Industry-based salary multipliers
        multipliers = {
            "consulting": 1.2,
            "saas": 1.15,
            "light_freight": 0.9,
        }
        multiplier = multipliers.get(industry, 1.0)

        # Base salary ranges (in JPY)
        base_salaries = {
            "J1": (3500000, 4000000, 4500000),
            "J2": (4000000, 4500000, 5000000),
            "S1": (5000000, 5500000, 6500000),
            "S2": (6000000, 7000000, 8000000),
            "M1": (7500000, 9000000, 10500000),
            "M2": (9000000, 11000000, 13000000),
            "E1": (12000000, 15000000, 18000000),
        }

        salary_bands = []
        for grade in grades:
            level = grade.get("level", "")
            base = base_salaries.get(level, (4000000, 5000000, 6000000))
            salary_bands.append(
                SalaryBand(
                    grade_level=level,
                    min_salary=int(base[0] * multiplier),
                    mid_salary=int(base[1] * multiplier),
                    max_salary=int(base[2] * multiplier),
                )
            )

        return CompensationSystem(
            company_id=company_data.get("company_id", "unknown"),
            salary_bands=salary_bands,
            salary_components=[
                SalaryComponent(
                    name="基本給",
                    salary_type=SalaryType.BASE,
                    is_fixed=True,
                ),
            ],
            bonus_structures=[
                BonusStructure(
                    name="業績賞与",
                    bonus_type=BonusType.PERFORMANCE,
                    base_months=2.0,
                )
            ],
            total_bonus_months=4.0,
            allowances=[
                Allowance(name="通勤手当", amount=50000, description="実費支給（上限5万円）"),
            ],
            market_position="50th percentile",
            pay_for_performance_ratio=0.3,
            design_principles=[
                "成果に応じた報酬",
                "市場競争力のある水準",
                "透明性のある制度",
            ],
        )

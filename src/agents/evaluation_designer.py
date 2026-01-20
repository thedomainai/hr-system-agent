"""
Evaluation Designer Agent.

Designs the evaluation system (評価制度) based on
the talent profile and grading system.
"""

from typing import Any

from src.core import AgentResult, BaseAgent, HITLGateId
from src.domain import (
    EvaluationCriterion,
    EvaluationPeriod,
    EvaluationSystem,
    EvaluationTemplate,
    EvaluationType,
)
from src.utils import get_logger

logger = get_logger(__name__)


class EvaluationDesignerAgent(BaseAgent):
    """
    Agent responsible for designing the evaluation system.

    This agent:
    1. Maps competencies to evaluation criteria
    2. Designs evaluation templates per grade
    3. Defines rating scales and guidelines
    4. Requests HITL approval
    """

    agent_type = "evaluation_designer"

    SYSTEM_PROMPT = """あなたは人事制度設計の専門家です。
企業の評価制度を設計してください。

評価制度の設計原則:
1. 求める人材像との整合性
2. 公平性と透明性
3. 成長を促すフィードバック
4. 運用のしやすさ

回答はJSON形式で提供してください。"""

    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        """Execute evaluation system design."""
        try:
            # Get context from previous steps
            company_data = input_data.get("collect_context", {}).get("company", {})
            talent_profile = input_data.get("generate_talent_profile", {}).get("talent_profile", {})
            grading_system = input_data.get("design_grading", {}).get("grading_system", {})

            if not all([company_data, talent_profile, grading_system]):
                return AgentResult(
                    success=False,
                    error="Missing required context from previous steps.",
                )

            # Design evaluation system
            evaluation_system = await self._design_evaluation_system(
                company_data, talent_profile, grading_system
            )

            # Store in state
            self.state.context["evaluation_system"] = evaluation_system.model_dump(mode="json")

            # Request HITL approval
            await self.request_hitl_approval(
                gate_id=HITLGateId.EVALUATION_SYSTEM.value,
                title="評価制度の確認",
                description="設計された評価制度が適切かどうか確認してください。",
                data={
                    "evaluation_system": evaluation_system.model_dump(mode="json"),
                    "company_name": company_data.get("name", "Unknown"),
                },
            )

            return AgentResult(
                success=True,
                data={"evaluation_system": evaluation_system.model_dump(mode="json")},
                requires_hitl=True,
                hitl_gate_id=HITLGateId.EVALUATION_SYSTEM.value,
            )

        except Exception as e:
            logger.error("evaluation_design_failed", error=str(e))
            return AgentResult(success=False, error=str(e))

    async def _design_evaluation_system(
        self,
        company_data: dict[str, Any],
        talent_profile: dict[str, Any],
        grading_system: dict[str, Any],
    ) -> EvaluationSystem:
        """Design the evaluation system using AI."""
        competencies = talent_profile.get("competencies", [])
        grades = grading_system.get("grades", [])

        user_message = f"""以下の情報に基づいて評価制度を設計してください。

企業情報:
- 企業名: {company_data.get('name', '')}
- 業界: {company_data.get('industry', '')}
- 従業員数: {company_data.get('employee_count', 0)}名

コンピテンシー:
{self._format_competencies(competencies)}

等級: {[g.get('level') for g in grades]}

以下の形式でJSONを返してください：
{{
    "evaluation_period": "semi_annual",
    "competency_weight": 0.6,
    "performance_weight": 0.4,
    "has_self_evaluation": true,
    "calibration_required": true,
    "design_principles": ["原則1", "原則2"],
    "criteria": [
        {{
            "name": "評価項目名",
            "description": "評価項目の説明",
            "evaluation_type": "competency",
            "weight": 0.1,
            "rating_descriptors": {{
                "S": "卓越した成果",
                "A": "期待を上回る",
                "B": "期待通り",
                "C": "改善が必要",
                "D": "大幅な改善が必要"
            }}
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

            # Build criteria
            criteria = []
            for crit_data in data.get("criteria", []):
                eval_type = EvaluationType.COMPETENCY
                type_str = crit_data.get("evaluation_type", "competency")
                if type_str == "performance":
                    eval_type = EvaluationType.PERFORMANCE
                elif type_str == "behavior":
                    eval_type = EvaluationType.BEHAVIOR

                criteria.append(
                    EvaluationCriterion(
                        name=crit_data.get("name", ""),
                        description=crit_data.get("description", ""),
                        evaluation_type=eval_type,
                        weight=crit_data.get("weight", 0.1),
                        rating_descriptors=crit_data.get("rating_descriptors", {}),
                    )
                )

            # Create templates for each grade group
            templates = self._create_templates(grades, criteria)

            # Parse period
            period_str = data.get("evaluation_period", "semi_annual")
            period = EvaluationPeriod.SEMI_ANNUAL
            if period_str == "quarterly":
                period = EvaluationPeriod.QUARTERLY
            elif period_str == "annual":
                period = EvaluationPeriod.ANNUAL

            return EvaluationSystem(
                company_id=company_data.get("company_id", "unknown"),
                evaluation_period=period,
                competency_weight=data.get("competency_weight", 0.5),
                performance_weight=data.get("performance_weight", 0.5),
                templates=templates,
                has_self_evaluation=data.get("has_self_evaluation", True),
                calibration_required=data.get("calibration_required", True),
                design_principles=data.get("design_principles", []),
            )

        except Exception as e:
            logger.warning("ai_evaluation_design_failed", error=str(e))
            return self._create_default_evaluation_system(company_data, talent_profile, grading_system)

    def _format_competencies(self, competencies: list[dict[str, Any]]) -> str:
        """Format competencies for prompt."""
        lines = []
        for comp in competencies:
            elements = comp.get("elements", [])
            elem_names = [e.get("name", "") for e in elements]
            lines.append(f"- {comp.get('name', '')}: {', '.join(elem_names)}")
        return "\n".join(lines)

    def _create_templates(
        self,
        grades: list[dict[str, Any]],
        criteria: list[EvaluationCriterion],
    ) -> list[EvaluationTemplate]:
        """Create evaluation templates for grade groups."""
        templates = []

        # Group grades
        junior_levels = [g["level"] for g in grades if g["level"].startswith("J")]
        senior_levels = [g["level"] for g in grades if g["level"].startswith("S")]
        manager_levels = [g["level"] for g in grades if g["level"].startswith(("M", "E"))]

        if junior_levels:
            templates.append(
                EvaluationTemplate(
                    name="ジュニア評価テンプレート",
                    grade_levels=junior_levels,
                    criteria=criteria,
                )
            )

        if senior_levels:
            templates.append(
                EvaluationTemplate(
                    name="シニア評価テンプレート",
                    grade_levels=senior_levels,
                    criteria=criteria,
                )
            )

        if manager_levels:
            templates.append(
                EvaluationTemplate(
                    name="マネージャー評価テンプレート",
                    grade_levels=manager_levels,
                    criteria=criteria,
                )
            )

        return templates

    def _create_default_evaluation_system(
        self,
        company_data: dict[str, Any],
        talent_profile: dict[str, Any],
        grading_system: dict[str, Any],
    ) -> EvaluationSystem:
        """Create a default evaluation system template."""
        competencies = talent_profile.get("competencies", [])
        grades = grading_system.get("grades", [])

        # Create criteria from competencies
        criteria = []
        total_weight = 0.6  # Competency weight

        for comp in competencies:
            weight = total_weight / len(competencies) if competencies else 0.2
            criteria.append(
                EvaluationCriterion(
                    name=comp.get("name", ""),
                    description=comp.get("description", ""),
                    evaluation_type=EvaluationType.COMPETENCY,
                    weight=weight,
                    rating_descriptors={
                        "S": "期待を大幅に上回る",
                        "A": "期待を上回る",
                        "B": "期待通り",
                        "C": "期待をやや下回る",
                        "D": "期待を大幅に下回る",
                    },
                )
            )

        # Add performance criterion
        criteria.append(
            EvaluationCriterion(
                name="業績達成度",
                description="設定された目標の達成度",
                evaluation_type=EvaluationType.PERFORMANCE,
                weight=0.4,
            )
        )

        templates = self._create_templates(grades, criteria)

        return EvaluationSystem(
            company_id=company_data.get("company_id", "unknown"),
            evaluation_period=EvaluationPeriod.SEMI_ANNUAL,
            competency_weight=0.6,
            performance_weight=0.4,
            templates=templates,
            has_self_evaluation=True,
            calibration_required=True,
            design_principles=[
                "求める人材像に基づく評価",
                "成長を促す建設的フィードバック",
                "公平性と透明性の確保",
            ],
        )

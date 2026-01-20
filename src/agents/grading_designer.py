"""
Grading Designer Agent.

Designs the grade structure (等級制度) based on
company context and talent profile.
"""

from typing import Any

from src.core import AgentResult, BaseAgent, HITLGateId
from src.domain import CompetencyLevel, Grade, GradeTrack, GradingSystem
from src.utils import get_logger

logger = get_logger(__name__)


class GradingDesignerAgent(BaseAgent):
    """
    Agent responsible for designing the grading system.

    This agent:
    1. Analyzes company size and industry
    2. Designs appropriate grade levels
    3. Maps competency requirements to grades
    4. Requests HITL approval
    """

    agent_type = "grading_designer"

    SYSTEM_PROMPT = """あなたは人事制度設計の専門家です。
企業の等級制度を設計してください。

等級制度の設計原則:
1. 企業規模に適した等級数（通常4-8等級）
2. 求める人材像との整合性
3. 各等級の役割・責任の明確化
4. 昇格基準の明確化

回答はJSON形式で提供してください。"""

    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        """Execute grading system design."""
        try:
            # Get context from previous steps
            company_data = input_data.get("collect_context", {}).get("company", {})
            talent_profile = input_data.get("generate_talent_profile", {}).get("talent_profile", {})

            if not company_data:
                return AgentResult(
                    success=False,
                    error="Company context not found.",
                )

            if not talent_profile:
                return AgentResult(
                    success=False,
                    error="Talent profile not found. Run talent_profile_generator first.",
                )

            # Design grading system
            grading_system = await self._design_grading_system(company_data, talent_profile)

            # Store in state
            self.state.context["grading_system"] = grading_system.model_dump(mode="json")

            # Request HITL approval
            await self.request_hitl_approval(
                gate_id=HITLGateId.GRADING_SYSTEM.value,
                title="等級制度の確認",
                description="設計された等級制度が適切かどうか確認してください。",
                data={
                    "grading_system": grading_system.model_dump(mode="json"),
                    "company_name": company_data.get("name", "Unknown"),
                },
            )

            return AgentResult(
                success=True,
                data={"grading_system": grading_system.model_dump(mode="json")},
                requires_hitl=True,
                hitl_gate_id=HITLGateId.GRADING_SYSTEM.value,
            )

        except Exception as e:
            logger.error("grading_design_failed", error=str(e))
            return AgentResult(success=False, error=str(e))

    async def _design_grading_system(
        self,
        company_data: dict[str, Any],
        talent_profile: dict[str, Any],
    ) -> GradingSystem:
        """Design the grading system using AI."""
        competencies = talent_profile.get("competencies", [])
        comp_names = [c.get("name", "") for c in competencies]

        user_message = f"""以下の企業情報と求める人材像に基づいて等級制度を設計してください。

企業情報:
- 企業名: {company_data.get('name', '')}
- 業界: {company_data.get('industry', '')}
- 従業員数: {company_data.get('employee_count', 0)}名
- 成長段階: {company_data.get('growth_stage', '')}

求める人材像のコンピテンシー:
{', '.join(comp_names)}

以下の形式でJSONを返してください：
{{
    "recommended_grade_count": 6,
    "has_dual_ladder": true,
    "design_principles": ["原則1", "原則2"],
    "grades": [
        {{
            "level": "J1",
            "name": "ジュニア I",
            "track": "general",
            "order": 1,
            "description": "等級の説明",
            "role_expectations": ["期待される役割1", "期待される役割2"],
            "responsibility_scope": "責任範囲",
            "competency_levels": [
                {{"competency_name": "コンピテンシー名", "required_level": 1}}
            ],
            "min_tenure_months": 12
        }}
        // 全等級分
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

            # Build grades
            grades = []
            for grade_data in data.get("grades", []):
                track_str = grade_data.get("track", "general")
                track = GradeTrack.GENERAL
                if track_str == "management":
                    track = GradeTrack.MANAGEMENT
                elif track_str == "specialist":
                    track = GradeTrack.SPECIALIST

                comp_levels = []
                for cl in grade_data.get("competency_levels", []):
                    comp_levels.append(
                        CompetencyLevel(
                            competency_id="",
                            competency_name=cl.get("competency_name", ""),
                            required_level=cl.get("required_level", 1),
                        )
                    )

                grades.append(
                    Grade(
                        level=grade_data.get("level", f"L{len(grades)+1}"),
                        name=grade_data.get("name", ""),
                        track=track,
                        order=grade_data.get("order", len(grades) + 1),
                        description=grade_data.get("description", ""),
                        role_expectations=grade_data.get("role_expectations", []),
                        responsibility_scope=grade_data.get("responsibility_scope", ""),
                        competency_levels=comp_levels,
                        min_tenure_months=grade_data.get("min_tenure_months", 12),
                    )
                )

            # Create system
            return GradingSystem(
                company_id=company_data.get("company_id", "unknown"),
                grades=grades,
                has_dual_ladder=data.get("has_dual_ladder", False),
                max_grade_level=data.get("recommended_grade_count", 6),
                design_principles=data.get("design_principles", []),
            )

        except Exception as e:
            logger.warning("ai_grading_design_failed", error=str(e))
            return self._create_default_grading_system(company_data, talent_profile)

    def _create_default_grading_system(
        self,
        company_data: dict[str, Any],
        talent_profile: dict[str, Any],
    ) -> GradingSystem:
        """Create a default grading system template."""
        employee_count = company_data.get("employee_count", 50)

        # Determine grade count based on company size
        if employee_count <= 50:
            grade_count = 4
        elif employee_count <= 100:
            grade_count = 5
        elif employee_count <= 300:
            grade_count = 6
        else:
            grade_count = 7

        grades = []
        grade_templates = [
            ("J1", "ジュニア I", "基礎を学ぶ段階"),
            ("J2", "ジュニア II", "自立して業務を遂行できる段階"),
            ("S1", "シニア I", "専門性を発揮する段階"),
            ("S2", "シニア II", "チームをリードする段階"),
            ("M1", "マネージャー I", "組織を管理する段階"),
            ("M2", "マネージャー II", "部門を統括する段階"),
            ("E1", "エグゼクティブ", "経営に参画する段階"),
        ]

        for i, (level, name, desc) in enumerate(grade_templates[:grade_count]):
            grades.append(
                Grade(
                    level=level,
                    name=name,
                    track=GradeTrack.GENERAL,
                    order=i + 1,
                    description=desc,
                    role_expectations=[],
                    min_tenure_months=12 + (i * 6),
                )
            )

        return GradingSystem(
            company_id=company_data.get("company_id", "unknown"),
            grades=grades,
            has_dual_ladder=employee_count > 100,
            max_grade_level=grade_count,
            design_principles=[
                "能力と成果の両面で評価",
                "明確な昇格基準",
                "キャリアパスの可視化",
            ],
        )

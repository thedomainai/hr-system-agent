"""
Talent Profile Generator Agent.

Generates the Ideal Talent Profile (求める人材像) with
3 competencies and 2 elements each.
"""

from typing import Any

from src.core import AgentResult, BaseAgent, HITLGateId
from src.domain import Competency, CompetencyElement, GraduationRequirement, IdealTalentProfile
from src.utils import get_logger

logger = get_logger(__name__)


class TalentProfileGeneratorAgent(BaseAgent):
    """
    Agent responsible for generating the Ideal Talent Profile.

    This agent:
    1. Analyzes company context and industry
    2. Generates 3 competencies with 2 elements each
    3. Defines graduation requirements
    4. Requests HITL approval
    """

    agent_type = "talent_profile_generator"

    SYSTEM_PROMPT = """あなたは人事制度設計の専門家です。
企業の「求める人材像」を設計してください。

求める人材像の構成:
- 3つのコンピテンシー（能力・行動特性）
- 各コンピテンシーには2つの要素
- 合計6つの要素

設計原則:
1. 企業のミッション・ビジョン・価値観と整合性を持つ
2. 業界特性を反映する
3. 具体的かつ観察可能な行動指標を含む
4. 成長段階に応じた設計

回答はJSON形式で提供してください。"""

    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        """Execute talent profile generation."""
        try:
            # Get company context from previous step
            company_data = input_data.get("collect_context", {}).get("company", {})
            enriched = input_data.get("collect_context", {}).get("enriched_context", {})

            if not company_data:
                return AgentResult(
                    success=False,
                    error="Company context not found. Run context_collector first.",
                )

            company_id = company_data.get("company_id", "unknown")

            # Generate talent profile
            profile = await self._generate_profile(company_data, enriched)

            # Store in state
            self.state.context["talent_profile"] = profile.model_dump(mode="json")

            # Request HITL approval
            await self.request_hitl_approval(
                gate_id=HITLGateId.IDEAL_TALENT_PROFILE.value,
                title="求める人材像の確認",
                description="生成された求める人材像が適切かどうか確認してください。",
                data={
                    "profile": profile.model_dump(mode="json"),
                    "company_name": company_data.get("name", "Unknown"),
                },
            )

            return AgentResult(
                success=True,
                data={"talent_profile": profile.model_dump(mode="json")},
                requires_hitl=True,
                hitl_gate_id=HITLGateId.IDEAL_TALENT_PROFILE.value,
            )

        except Exception as e:
            logger.error("talent_profile_generation_failed", error=str(e))
            return AgentResult(success=False, error=str(e))

    async def _generate_profile(
        self,
        company_data: dict[str, Any],
        enriched: dict[str, Any],
    ) -> IdealTalentProfile:
        """Generate the ideal talent profile using AI."""
        user_message = f"""以下の企業情報に基づいて「求める人材像」を設計してください。

企業情報:
- 企業名: {company_data.get('name', '')}
- 業界: {company_data.get('industry', '')}
- 従業員数: {company_data.get('employee_count', 0)}名
- ミッション: {company_data.get('mission', '')}
- ビジョン: {company_data.get('vision', '')}
- 価値観: {', '.join(company_data.get('values', []))}
- 設計目標: {', '.join(company_data.get('design_goals', []))}

業界特性:
{enriched.get('industry_characteristics', '')}

推奨コンピテンシー:
{', '.join(enriched.get('key_competencies_for_industry', []))}

以下の形式でJSONを返してください：
{{
    "vision_statement": "求める人材像を一文で表現",
    "competencies": [
        {{
            "name": "コンピテンシー名1",
            "description": "コンピテンシーの説明",
            "elements": [
                {{
                    "name": "要素名1",
                    "description": "要素の説明",
                    "behavioral_indicators": ["行動指標1", "行動指標2"]
                }},
                {{
                    "name": "要素名2",
                    "description": "要素の説明",
                    "behavioral_indicators": ["行動指標1", "行動指標2"]
                }}
            ],
            "weight": 0.33
        }},
        // 合計3つのコンピテンシー
    ]
}}"""

        try:
            response = await self.call_llm(
                system_prompt=self.SYSTEM_PROMPT,
                user_message=user_message,
                temperature=0.7,
                max_tokens=4096,
            )

            # Parse JSON response
            import json

            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
            else:
                raise ValueError("Could not parse JSON from response")

            # Build competencies
            competencies = []
            for i, comp_data in enumerate(data.get("competencies", [])[:3]):
                elements = []
                for elem_data in comp_data.get("elements", [])[:2]:
                    elements.append(
                        CompetencyElement(
                            name=elem_data.get("name", f"要素{len(elements)+1}"),
                            description=elem_data.get("description", ""),
                            behavioral_indicators=elem_data.get("behavioral_indicators", []),
                        )
                    )

                # Ensure 2 elements
                while len(elements) < 2:
                    elements.append(
                        CompetencyElement(
                            name=f"要素{len(elements)+1}",
                            description="（要定義）",
                            behavioral_indicators=[],
                        )
                    )

                competencies.append(
                    Competency(
                        name=comp_data.get("name", f"コンピテンシー{i+1}"),
                        description=comp_data.get("description", ""),
                        elements=elements,
                        weight=comp_data.get("weight", 0.33),
                    )
                )

            # Ensure 3 competencies
            while len(competencies) < 3:
                competencies.append(
                    Competency(
                        name=f"コンピテンシー{len(competencies)+1}",
                        description="（要定義）",
                        elements=[
                            CompetencyElement(name="要素1", description="（要定義）"),
                            CompetencyElement(name="要素2", description="（要定義）"),
                        ],
                        weight=0.33,
                    )
                )

            # Create profile
            profile = IdealTalentProfile(
                company_id=company_data.get("company_id", "unknown"),
                vision_statement=data.get("vision_statement", ""),
                competencies=competencies,
            )

            return profile

        except Exception as e:
            logger.warning("ai_profile_generation_failed", error=str(e))
            # Return a template profile
            return self._create_template_profile(company_data)

    def _create_template_profile(self, company_data: dict[str, Any]) -> IdealTalentProfile:
        """Create a template profile when AI generation fails."""
        return IdealTalentProfile(
            company_id=company_data.get("company_id", "unknown"),
            vision_statement="（ビジョンステートメントを入力してください）",
            competencies=[
                Competency(
                    name="問題解決力",
                    description="複雑な課題を分析し、効果的な解決策を導き出す能力",
                    elements=[
                        CompetencyElement(
                            name="課題分析",
                            description="問題の本質を見極め、構造的に整理する力",
                        ),
                        CompetencyElement(
                            name="解決策立案",
                            description="実行可能な解決策を複数提案する力",
                        ),
                    ],
                    weight=0.33,
                ),
                Competency(
                    name="コミュニケーション力",
                    description="関係者と効果的にコミュニケーションを取る能力",
                    elements=[
                        CompetencyElement(
                            name="傾聴力",
                            description="相手の意図を正確に理解する力",
                        ),
                        CompetencyElement(
                            name="説明力",
                            description="複雑な内容を分かりやすく伝える力",
                        ),
                    ],
                    weight=0.33,
                ),
                Competency(
                    name="自律性",
                    description="主体的に行動し、継続的に成長する能力",
                    elements=[
                        CompetencyElement(
                            name="主体性",
                            description="自ら課題を見つけ、行動を起こす力",
                        ),
                        CompetencyElement(
                            name="継続学習",
                            description="新しい知識・スキルを積極的に習得する力",
                        ),
                    ],
                    weight=0.34,
                ),
            ],
        )

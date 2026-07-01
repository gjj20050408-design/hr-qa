"""个性化权益报告服务 — 根据员工个人信息生成专属权益清单

权益数值由确定规则（工龄档位 + 婚姻状况）算出，LLM 仅润色整体寄语文案，
绝不修改任何数字。按 (user_id, year) 缓存。
"""
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.enums import MaritalStatus
from app.models.benefit_report import BenefitReport

logger = logging.getLogger(__name__)


class BenefitService:

    SYSTEM_PROMPT = (
        "你是企业HR福利顾问。下面给你一位员工的权益清单（已由系统按制度精确计算）。"
        "请生成一段 80-150 字的友好、温暖的整体说明寄语，帮助员工理解自己的权益。\n\n"
        "严格要求：\n"
        "1. 绝对不要修改、新增或删除任何数字与条目，只做语言润色与总体说明\n"
        "2. 不要逐条复述清单，而是给出整体性的温馨说明\n"
        "3. 使用中文，语气亲切专业\n"
        "只输出寄语文本本身，不要输出 JSON 或其他格式。"
    )

    @staticmethod
    async def get_or_generate(
        user, year: int, db_session: AsyncSession, force: bool = False,
    ) -> dict:
        """获取或生成本人权益报告。"""
        # 缓存命中
        if not force:
            cached = await BenefitService._get_cache(user.user_id, year, db_session)
            if cached:
                return BenefitService._to_dict(cached, user, cached_hit=True)

        # 1. 按确定规则计算权益条目
        tenure = user.compute_tenure_years()
        items = BenefitService._compute_items(user, tenure)

        # 2. LLM 润色整体寄语（失败则用默认文案）
        summary, model = BenefitService._polish_summary(user, year, tenure, items)

        # 3. 写缓存
        if force:
            await BenefitService._delete_cache(user.user_id, year, db_session)
        record = BenefitReport(
            user_id=user.user_id,
            year=year,
            tenure_years=tenure,
            items=items,
            summary=summary,
            model=model,
        )
        db_session.add(record)
        await db_session.flush()
        return BenefitService._to_dict(record, user, cached_hit=False)

    @staticmethod
    def _compute_items(user, tenure: int) -> list:
        """按制度规则算出确定的权益条目（数值不经过 LLM）。"""
        # 年假档位：<3→5，3-10→10，>10→15（与 RULE_TEMPLATES / qa_chain _fill_context 一致）
        annual_leave = 5 if tenure < 3 else (10 if tenure < 10 else 15)

        items = [
            {
                "title": "带薪年假",
                "value": f"{annual_leave} 天/年",
                "description": f"您当前工龄 {tenure} 年，按《休假制度》可享受 {annual_leave} 天带薪年假。",
                "category": "休假",
                "source_rule": "rule-annual-leave",
            },
            {
                "title": "病假薪酬",
                "value": "最高全额",
                "description": "病假≤2天全额工资；3-30天按基本工资80%；超30天按当地最低工资标准。",
                "category": "薪酬",
                "source_rule": "rule-sick-leave-pay",
            },
            {
                "title": "加班补偿",
                "value": "1.5–3 倍",
                "description": "工作日加班1.5倍、休息日2倍（或调休）、法定节假日3倍工资。需提前审批。",
                "category": "薪酬",
                "source_rule": "rule-overtime-pay",
            },
        ]

        # 婚假：根据婚姻状况个性化展示
        marital = user.marital_status
        is_married = marital == MaritalStatus.MARRIED
        items.append({
            "title": "婚假",
            "value": "3 天起",
            "description": (
                "法定婚假3天，晚婚（男≥25/女≥23）可增加7天，需在领证后一年内休完。"
                + ("（您已婚，如尚未休可向HR申请。）" if is_married else "（祝您未来喜结良缘时及时申请。）")
            ),
            "category": "休假",
            "source_rule": "rule-marriage-leave",
        })

        return items

    @staticmethod
    def _polish_summary(user, year: int, tenure: int, items: list) -> tuple:
        """调用 LLM 生成整体寄语；不可用时返回默认文案。返回 (summary, model)。"""
        default_summary = (
            f"{user.name}，您好！这是您 {year} 年度的专属权益清单。"
            f"您当前工龄 {tenure} 年，共梳理出 {len(items)} 项核心权益。"
            "如对任何一项有疑问，欢迎随时咨询 HR 部门。"
        )

        from app.providers.llm import llm_provider
        if isinstance(llm_provider, type(None)):
            return default_summary, ""
        try:
            if not llm_provider.health_check():
                return default_summary, ""
        except Exception:
            return default_summary, ""

        items_text = "\n".join(f"- {it['title']}：{it['value']}（{it['description']}）" for it in items)
        prompt = (
            f"员工姓名：{user.name}\n"
            f"报告年份：{year}\n"
            f"工龄：{tenure} 年\n"
            f"权益清单：\n{items_text}\n\n"
            "请生成整体寄语。"
        )
        try:
            resp = llm_provider.generate(
                prompt=prompt,
                system_prompt=BenefitService.SYSTEM_PROMPT,
                max_tokens=512,
                temperature=0.5,
            )
            if not resp.content or resp.content.startswith("[LLM"):
                return default_summary, ""
            return resp.content.strip(), resp.model
        except Exception as e:
            logger.error(f"BenefitService: polish failed: {e}")
            return default_summary, ""

    @staticmethod
    async def _get_cache(user_id: str, year: int, db_session: AsyncSession) -> Optional[BenefitReport]:
        result = await db_session.execute(
            select(BenefitReport).where(
                BenefitReport.user_id == user_id,
                BenefitReport.year == year,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _delete_cache(user_id: str, year: int, db_session: AsyncSession) -> None:
        existing = await BenefitService._get_cache(user_id, year, db_session)
        if existing:
            await db_session.delete(existing)
            await db_session.flush()

    @staticmethod
    def _to_dict(record: BenefitReport, user, cached_hit: bool) -> dict:
        return {
            "year": record.year,
            "user_name": user.name,
            "department_name": user.department.name if user.department else None,
            "tenure_years": record.tenure_years,
            "items": record.items or [],
            "summary": record.summary or "",
            "model": record.model or "",
            "created_at": str(record.created_at) if record.created_at else None,
            "cached": cached_hit,
        }

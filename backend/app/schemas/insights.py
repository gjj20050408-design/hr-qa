"""制度解读 / 个性化权益报告 schema"""
from typing import List, Optional
from pydantic import BaseModel, Field


class InterpretationResponse(BaseModel):
    document_id: str
    title: str
    doc_version: str
    summary: str = ""
    flowchart: str = ""
    comparison_table: str = ""
    key_points: List[str] = Field(default_factory=list)
    model: str = ""
    created_at: Optional[str] = None
    cached: bool = False
    degraded: bool = False


class BenefitItem(BaseModel):
    title: str
    value: str
    description: str
    category: str = ""
    source_rule: str = ""


class BenefitReportResponse(BaseModel):
    year: int
    user_name: str
    department_name: Optional[str] = None
    tenure_years: Optional[int] = None
    items: List[BenefitItem] = Field(default_factory=list)
    summary: str = ""
    model: str = ""
    created_at: Optional[str] = None
    cached: bool = False

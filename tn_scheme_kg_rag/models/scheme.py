from typing import List, Optional
from pydantic import BaseModel, Field

class SchemeRecord(BaseModel):
    scheme_id: str = Field(..., description="Unique scheme hash or code")
    scheme_name_en: str = Field(..., description="Official scheme name in English")
    scheme_name_ta: Optional[str] = Field("Not available in the retrieved official sources", description="Scheme name in Tamil")
    department: str = Field(..., description="Implementing department")
    category: Optional[str] = Field("Not available in the retrieved official sources")
    description: str = Field(..., description="Core description and objectives")
    eligibility_criteria: List[str] = Field(default_factory=list)
    benefits: str = Field(..., description="Assistance amount or subsidy details")
    required_documents: List[str] = Field(default_factory=list)
    application_procedure: str = Field(..., description="Application steps")
    application_portal_url: Optional[str] = Field(None)
    g_o_references: List[str] = Field(default_factory=list)
    source_url: str = Field(..., description="Official source URL")
    last_verified_timestamp: str = Field(..., description="Timestamp of last check")
    confidence_score: float = Field(1.0, ge=0.0, le=1.0)
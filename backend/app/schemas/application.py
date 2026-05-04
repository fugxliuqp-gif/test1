from typing import Optional
from pydantic import BaseModel


class ApplyRequest(BaseModel):
    company_name: str
    credit_code: str
    industry: str
    scale: str
    contact_name: str
    contact_phone: str
    contact_email: str
    interested_skills: Optional[str] = ""
    requirements: Optional[str] = ""
    current_systems: Optional[str] = ""


class ReviewRequest(BaseModel):
    status: str
    reject_reason: Optional[str] = ""

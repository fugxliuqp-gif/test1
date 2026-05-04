from typing import Optional
from pydantic import BaseModel


class SkillCreate(BaseModel):
    key: str
    name: str
    icon: Optional[str] = ""
    summary: str
    description: Optional[str] = ""
    scenarios: Optional[str] = ""
    capabilities: Optional[str] = ""
    platforms: Optional[str] = ""
    sort_order: int = 0
    is_active: bool = True

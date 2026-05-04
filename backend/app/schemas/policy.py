from typing import Optional
from pydantic import BaseModel


class PolicyCreate(BaseModel):
    dept: str
    doc_number: Optional[str] = ""
    title: str
    description: Optional[str] = ""
    sort_order: int = 0
    is_active: bool = True

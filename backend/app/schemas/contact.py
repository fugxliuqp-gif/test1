from typing import Optional
from pydantic import BaseModel


class ContactCreate(BaseModel):
    type: str
    label: str
    value: str
    display_order: int = 0

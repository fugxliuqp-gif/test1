from typing import Optional
from pydantic import BaseModel


class BannerCreate(BaseModel):
    title: str
    subtitle: Optional[str] = ""
    image_url: str = ""
    button_text: str = "了解更多"
    button_link: str = "#trial"
    sort_order: int = 0
    is_active: bool = True

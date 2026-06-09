from pydantic import BaseModel
from typing import Optional


class ShareWeekResponse(BaseModel):
    url: str
    token: str


class ShareWeekStatusResponse(BaseModel):
    active: bool
    url: Optional[str] = None
    token: Optional[str] = None

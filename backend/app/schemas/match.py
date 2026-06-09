from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
import uuid


class CreateMatch(BaseModel):
    rival: str
    fecha: date
    resultado: Optional[str] = None
    notas: Optional[str] = None


class UpdateMatch(BaseModel):
    rival: str
    fecha: date
    resultado: Optional[str] = None
    notas: Optional[str] = None


class MatchResponse(BaseModel):
    id: uuid.UUID
    team_id: uuid.UUID
    rival: str
    fecha: date
    resultado: Optional[str] = None
    notas: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

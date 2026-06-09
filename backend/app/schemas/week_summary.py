from pydantic import BaseModel
from datetime import date
from typing import Optional
import uuid


class WeekActivitySummary(BaseModel):
    id: uuid.UUID
    horario: Optional[str] = None
    lugar: Optional[str] = None
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True


class WeekDaySummary(BaseModel):
    id: uuid.UUID
    dia: str
    fecha: Optional[date] = None
    activities: list[WeekActivitySummary]

    class Config:
        from_attributes = True


class WeekSummaryResponse(BaseModel):
    id: uuid.UUID
    fecha_inicio: date
    fecha_fin: date
    notas: Optional[str] = None
    public_token: Optional[str] = None
    days: list[WeekDaySummary]

    class Config:
        from_attributes = True
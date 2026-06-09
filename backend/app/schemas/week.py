from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
import uuid


# --- INPUT ---

class CreateWeek(BaseModel):
	fecha_inicio: date
	fecha_fin: date
	notas: Optional[str] = None


class UpdateWeek(BaseModel):
	fecha_inicio: date
	fecha_fin: date
	notas: Optional[str] = None


class CopyWeek(BaseModel):
	fecha_inicio: Optional[date] = None
	fecha_fin: Optional[date] = None
	notas: Optional[str] = None


class GenerateWeek(BaseModel):
	descripcion: str
	fecha_inicio: date
	fecha_fin: date


# --- OUTPUT ---

class WeekResponse(BaseModel):
	id: uuid.UUID
	team_id: uuid.UUID
	fecha_inicio: date
	fecha_fin: date
	notas: Optional[str]
	public_token: Optional[str] = None
	created_at: datetime

	class Config:
		from_attributes = True

from pydantic import BaseModel
from datetime import date
from typing import Optional
import uuid


# --- INPUT ---

class CreateWeekDay(BaseModel):
	dia: str
	fecha: Optional[date] = None


class UpdateWeekDay(BaseModel):
	dia: str
	fecha: Optional[date] = None


# --- OUTPUT ---

class WeekDayResponse(BaseModel):
	id: uuid.UUID
	week_id: uuid.UUID
	dia: str
	fecha: Optional[date]

	class Config:
		from_attributes = True

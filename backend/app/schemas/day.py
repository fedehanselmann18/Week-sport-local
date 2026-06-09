from pydantic import BaseModel
from typing import Optional
import uuid


# --- INPUT ---

class CreateDayActivity(BaseModel):
	horario: Optional[str] = None
	lugar: Optional[str] = None
	descripcion: Optional[str] = None


class UpdateDayActivity(BaseModel):
	horario: Optional[str] = None
	lugar: Optional[str] = None
	descripcion: Optional[str] = None


# --- OUTPUT ---

class DayActivityResponse(BaseModel):
	id: uuid.UUID
	day_id: uuid.UUID
	horario: Optional[str]
	lugar: Optional[str]
	descripcion: Optional[str]

	class Config:
		from_attributes = True

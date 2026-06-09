from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid


# --- INPUT ---

class CreatePlayer(BaseModel):
	nombre: str
	apellido: str
	posicion: Optional[str] = None
	dorsal: Optional[int] = None
	notas: Optional[str] = None


class UpdatePlayer(BaseModel):
	nombre: str
	apellido: str
	posicion: Optional[str] = None
	dorsal: Optional[int] = None
	notas: Optional[str] = None


# --- OUTPUT ---

class PlayerResponse(BaseModel):
	id: uuid.UUID
	team_id: uuid.UUID
	nombre: str
	apellido: str
	posicion: Optional[str]
	dorsal: Optional[int]
	notas: Optional[str]
	created_at: datetime

	class Config:
		from_attributes = True

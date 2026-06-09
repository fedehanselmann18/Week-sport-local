from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid


# --- INPUT ---

class CreateTeam(BaseModel):
    nombre: str
    deporte: str


class UpdateTeam(BaseModel):
    nombre: str
    deporte: str


# --- OUTPUT ---

class TeamResponse(BaseModel):
    id: uuid.UUID
    nombre: str
    deporte: str
    foto_url: Optional[str] = None
    owner_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
from pydantic import BaseModel
from datetime import datetime
import uuid                        # ← agregá esto


class CreateUser(BaseModel):
    email: str
    password: str
    username: str


class UpdateUsername(BaseModel):
    username: str


class UserResponse(BaseModel):
    id: uuid.UUID                  # ← antes era int, ahora UUID
    email: str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True
from app.db.db import Base
from sqlalchemy import Column, String, ForeignKey, Text, Date, Integer
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid


# ─────────────────────────────────────────
#  USERS
# ─────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email      = Column(String, nullable=False, unique=True)
    password   = Column(String, nullable=False)
    username   = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    teams = relationship(
        "Team",
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ─────────────────────────────────────────
#  TEAMS
# ─────────────────────────────────────────
class Team(Base):
    __tablename__ = "teams"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre     = Column(String, nullable=False)
    deporte    = Column(String, nullable=False)
    # En el modelo Team, agregar:
    foto_url = Column(String, nullable=True)
    owner_id   = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    owner          = relationship("User", back_populates="teams")
    players        = relationship(
        "Player",
        back_populates="team",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    training_weeks = relationship(
        "TrainingWeek",
        back_populates="team",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    matches = relationship(
        "Match",
        back_populates="team",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ─────────────────────────────────────────
#  PLAYERS
# ─────────────────────────────────────────
class Player(Base):
    __tablename__ = "players"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id    = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    nombre     = Column(String, nullable=False)
    apellido   = Column(String, nullable=False)
    posicion   = Column(String, nullable=True)
    dorsal     = Column(Integer, nullable=True)
    notas      = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    team = relationship("Team", back_populates="players")


# ─────────────────────────────────────────
#  TRAINING WEEKS
# ─────────────────────────────────────────
class TrainingWeek(Base):
    __tablename__ = "training_weeks"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id      = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin    = Column(Date, nullable=False)
    notas        = Column(Text, nullable=True)
    public_token = Column(String, nullable=True, unique=True)
    created_at   = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    team      = relationship("Team", back_populates="training_weeks")
    days      = relationship(
        "WeekDay",
        back_populates="week",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ─────────────────────────────────────────
#  WEEK DAYS
# ─────────────────────────────────────────
class WeekDay(Base):
    __tablename__ = "week_days"

    id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    week_id = Column(UUID(as_uuid=True), ForeignKey("training_weeks.id", ondelete="CASCADE"), nullable=False)
    dia     = Column(String, nullable=False)
    fecha   = Column(Date, nullable=True)

    week       = relationship("TrainingWeek", back_populates="days")
    activities = relationship(
        "DayActivity",
        back_populates="day",
        order_by="DayActivity.horario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ─────────────────────────────────────────
#  DAY ACTIVITIES
# ─────────────────────────────────────────
class DayActivity(Base):
    __tablename__ = "day_activities"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    day_id      = Column(UUID(as_uuid=True), ForeignKey("week_days.id", ondelete="CASCADE"), nullable=False)
    horario     = Column(String, nullable=True)
    lugar       = Column(String, nullable=True)
    descripcion = Column(Text, nullable=True)

    day = relationship("WeekDay", back_populates="activities")


# ─────────────────────────────────────────
#  MATCHES
# ─────────────────────────────────────────
class Match(Base):
    __tablename__ = "matches"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id    = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    rival      = Column(String, nullable=False)
    fecha      = Column(Date, nullable=False)
    resultado  = Column(String, nullable=True)
    notas      = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    team = relationship("Team", back_populates="matches")
from datetime import timedelta
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import models
from app.db.db import get_db
from app.oAuth2 import get_current_user
from app.schemas.week import CreateWeek, UpdateWeek, WeekResponse


router = APIRouter(
    prefix="/teams/{team_id}/weeks",
    tags=["Training Weeks"],
)

DAY_ORDER = [
    "Lunes",
    "Martes",
    "Miercoles",
    "Jueves",
    "Viernes",
    "Sabado",
    "Domingo",
]


def _validate_owned_team_or_404(db: Session, team_id, owner_id):
    team = db.query(models.Team).filter(
        models.Team.id == team_id,
        models.Team.owner_id == owner_id,
    ).first()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return team


def _validate_exact_7_day_week(fecha_inicio, fecha_fin):
    if fecha_fin < fecha_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date cannot be before start date",
        )

    if (fecha_fin - fecha_inicio).days != 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Week must be exactly 7 days",
        )

    if fecha_inicio.weekday() != 0 or fecha_fin.weekday() != 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Week must start on Monday and end on Sunday",
        )


def _build_week_days(new_week, start_date):
    return [
        models.WeekDay(
            week=new_week,
            dia=day_name,
            fecha=start_date + timedelta(days=index),
        )
        for index, day_name in enumerate(DAY_ORDER)
    ]


@router.post("/", response_model=WeekResponse, status_code=status.HTTP_201_CREATED)
def create_week(team_id: uuid.UUID, week: CreateWeek, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _validate_owned_team_or_404(db, team_id, current_user.id)
    _validate_exact_7_day_week(week.fecha_inicio, week.fecha_fin)

    new_week = models.TrainingWeek(
        team_id=team_id,
        fecha_inicio=week.fecha_inicio,
        fecha_fin=week.fecha_fin,
        notas=week.notas,
    )
    db.add(new_week)
    for day in _build_week_days(new_week, week.fecha_inicio):
        db.add(day)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not create week")

    db.refresh(new_week)
    return new_week


@router.get("/", response_model=list[WeekResponse], status_code=status.HTTP_200_OK)
def get_weeks(team_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _validate_owned_team_or_404(db, team_id, current_user.id)
    return db.query(models.TrainingWeek).filter(models.TrainingWeek.team_id == team_id).all()


@router.get("/{week_id}", response_model=WeekResponse, status_code=status.HTTP_200_OK)
def get_week(team_id: uuid.UUID, week_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _validate_owned_team_or_404(db, team_id, current_user.id)
    week = db.query(models.TrainingWeek).filter(
        models.TrainingWeek.id == week_id,
        models.TrainingWeek.team_id == team_id,
    ).first()
    if week is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Week not found")
    return week


@router.delete("/{week_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_week(team_id: uuid.UUID, week_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _validate_owned_team_or_404(db, team_id, current_user.id)
    week = db.query(models.TrainingWeek).filter(
        models.TrainingWeek.id == week_id,
        models.TrainingWeek.team_id == team_id,
    ).first()
    if week is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Week not found")
    db.delete(week)
    db.commit()


@router.put("/{week_id}", response_model=WeekResponse, status_code=status.HTTP_200_OK)
def update_week(team_id: uuid.UUID, week_id: uuid.UUID, week_data: UpdateWeek, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _validate_owned_team_or_404(db, team_id, current_user.id)
    _validate_exact_7_day_week(week_data.fecha_inicio, week_data.fecha_fin)

    week = db.query(models.TrainingWeek).filter(
        models.TrainingWeek.id == week_id,
        models.TrainingWeek.team_id == team_id,
    ).first()
    if week is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Week not found")

    week.fecha_inicio = week_data.fecha_inicio
    week.fecha_fin = week_data.fecha_fin
    week.notas = week_data.notas

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not update week")

    db.refresh(week)
    return week

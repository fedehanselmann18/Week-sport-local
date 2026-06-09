from datetime import timedelta
import secrets
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import models
from app.db.db import get_db
from app.oAuth2 import get_current_user
from app.schemas.share import ShareWeekResponse, ShareWeekStatusResponse
from app.schemas.week import CopyWeek, CreateWeek, UpdateWeek, WeekResponse
from app.schemas.week_summary import WeekSummaryResponse


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


def _ensure_full_week_days(db: Session, week):
    existing_day_names = {day.dia for day in week.days}
    if len(existing_day_names) == len(DAY_ORDER):
        return week

    for index, day_name in enumerate(DAY_ORDER):
        if day_name in existing_day_names:
            continue
        db.add(
            models.WeekDay(
                week=week,
                dia=day_name,
                fecha=week.fecha_inicio + timedelta(days=index) if week.fecha_inicio else None,
            )
        )

    db.commit()
    return db.query(models.TrainingWeek).filter(models.TrainingWeek.id == week.id).first()


def _serialize_summary(week):
    ordered_days = sorted(
        week.days,
        key=lambda day: DAY_ORDER.index(day.dia) if day.dia in DAY_ORDER else len(DAY_ORDER),
    )

    return WeekSummaryResponse(
        id=week.id,
        fecha_inicio=week.fecha_inicio,
        fecha_fin=week.fecha_fin,
        notas=week.notas,
        public_token=week.public_token,
        days=[
            {
                "id": day.id,
                "dia": day.dia,
                "fecha": day.fecha,
                "activities": [
                    {
                        "id": activity.id,
                        "horario": activity.horario,
                        "lugar": activity.lugar,
                        "descripcion": activity.descripcion,
                    }
                    for activity in day.activities
                ],
            }
            for day in ordered_days
        ],
    )


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


@router.post("/{week_id}/copy", response_model=WeekResponse, status_code=status.HTTP_201_CREATED)
def copy_week(team_id: uuid.UUID, week_id: uuid.UUID, copy_data: Optional[CopyWeek] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _validate_owned_team_or_404(db, team_id, current_user.id)

    original_week = db.query(models.TrainingWeek).filter(
        models.TrainingWeek.id == week_id,
        models.TrainingWeek.team_id == team_id,
    ).first()
    if original_week is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Week not found")

    default_new_start = original_week.fecha_fin + timedelta(days=1)
    new_start = copy_data.fecha_inicio if copy_data and copy_data.fecha_inicio else default_new_start
    new_end = copy_data.fecha_fin if copy_data and copy_data.fecha_fin else (new_start + timedelta(days=6))
    new_notes = copy_data.notas if copy_data and copy_data.notas is not None else original_week.notas
    _validate_exact_7_day_week(new_start, new_end)

    original_days_by_name = {day.dia: day for day in original_week.days}
    new_week = models.TrainingWeek(
        team_id=team_id,
        fecha_inicio=new_start,
        fecha_fin=new_end,
        notas=new_notes,
    )
    db.add(new_week)

    for index, day_name in enumerate(DAY_ORDER):
        duplicated_day = models.WeekDay(
            week=new_week,
            dia=day_name,
            fecha=new_start + timedelta(days=index),
        )
        db.add(duplicated_day)

        original_day = original_days_by_name.get(day_name)
        if original_day is None:
            continue

        for activity in original_day.activities:
            db.add(
                models.DayActivity(
                    day=duplicated_day,
                    horario=activity.horario,
                    lugar=activity.lugar,
                    descripcion=activity.descripcion,
                )
            )

    db.commit()
    db.refresh(new_week)
    return new_week


@router.post("/{week_id}/share", response_model=ShareWeekResponse, status_code=status.HTTP_200_OK)
def create_share(team_id: uuid.UUID, week_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _validate_owned_team_or_404(db, team_id, current_user.id)

    week = db.query(models.TrainingWeek).filter(
        models.TrainingWeek.id == week_id,
        models.TrainingWeek.team_id == team_id,
    ).first()
    if week is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Week not found")

    if not week.public_token:
        week.public_token = secrets.token_urlsafe(16)
        db.commit()
        db.refresh(week)

    return {"url": f"/public/week/{week.public_token}", "token": week.public_token}


@router.get("/{week_id}/share", response_model=ShareWeekStatusResponse, status_code=status.HTTP_200_OK)
def get_share_status(team_id: uuid.UUID, week_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _validate_owned_team_or_404(db, team_id, current_user.id)

    week = db.query(models.TrainingWeek).filter(
        models.TrainingWeek.id == week_id,
        models.TrainingWeek.team_id == team_id,
    ).first()
    if week is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Week not found")

    if not week.public_token:
        return {"active": False, "url": None, "token": None}

    return {"active": True, "url": f"/public/week/{week.public_token}", "token": week.public_token}


@router.delete("/{week_id}/share", status_code=status.HTTP_204_NO_CONTENT)
def disable_share(team_id: uuid.UUID, week_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _validate_owned_team_or_404(db, team_id, current_user.id)

    week = db.query(models.TrainingWeek).filter(
        models.TrainingWeek.id == week_id,
        models.TrainingWeek.team_id == team_id,
    ).first()
    if week is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Week not found")

    week.public_token = None
    db.commit()


@router.get("/{week_id}/summary", response_model=WeekSummaryResponse, status_code=status.HTTP_200_OK)
def get_week_summary(team_id: uuid.UUID, week_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _validate_owned_team_or_404(db, team_id, current_user.id)

    week = db.query(models.TrainingWeek).filter(
        models.TrainingWeek.id == week_id,
        models.TrainingWeek.team_id == team_id,
    ).first()
    if week is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Week not found")

    week = _ensure_full_week_days(db, week)
    return _serialize_summary(week)

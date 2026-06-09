from datetime import timedelta
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import models
from app.db.db import get_db
from app.schemas.week_summary import WeekSummaryResponse


DAY_ORDER = [
    "Lunes",
    "Martes",
    "Miercoles",
    "Jueves",
    "Viernes",
    "Sabado",
    "Domingo",
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


router = APIRouter(
    prefix="/public/week",
    tags=["Public Weeks"],
)


@router.get("/{token}", response_model=WeekSummaryResponse, status_code=status.HTTP_200_OK)
def get_public_week(token: str, db: Session = Depends(get_db)):
    week = db.query(models.TrainingWeek).filter(models.TrainingWeek.public_token == token).first()
    if week is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Public week not found")

    week = _ensure_full_week_days(db, week)
    return _serialize_summary(week)

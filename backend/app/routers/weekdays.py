from fastapi import APIRouter, status, HTTPException, Depends
from app.db.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db import models
from app.schemas.weekday import CreateWeekDay, WeekDayResponse, UpdateWeekDay
from app.oAuth2 import get_current_user
import uuid


router = APIRouter(
	prefix="/weeks/{week_id}/days",
	tags=['Week Days']
)


@router.post("/", response_model=WeekDayResponse,
			 status_code=status.HTTP_201_CREATED)
# Create a day inside a week only when that week belongs to a team owned by current user.
def create_day(week_id: uuid.UUID, day: CreateWeekDay,
			   db: Session = Depends(get_db),
			   current_user = Depends(get_current_user)):
	week = db.query(models.TrainingWeek).join(models.Team).filter(
		models.TrainingWeek.id == week_id,
		models.Team.owner_id == current_user.id,
	).first()
	if week is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Week not found")

	new_day = models.WeekDay(
		week_id=week_id,
		dia=day.dia,
		fecha=day.fecha,
	)
	db.add(new_day)
	try:
		db.commit()
	except IntegrityError:
		db.rollback()
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not create day")

	db.refresh(new_day)
	return new_day


@router.get("/", response_model=list[WeekDayResponse],
			status_code=status.HTTP_200_OK)
# Return all days of a week only when that week belongs to a team owned by current user.
def get_days(week_id: uuid.UUID, db: Session = Depends(get_db),
			 current_user = Depends(get_current_user)):
	week = db.query(models.TrainingWeek).join(models.Team).filter(
		models.TrainingWeek.id == week_id,
		models.Team.owner_id == current_user.id,
	).first()
	if week is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Week not found")
	return db.query(models.WeekDay).filter(models.WeekDay.week_id == week_id).all()


@router.get("/{day_id}", response_model=WeekDayResponse,
			status_code=status.HTTP_200_OK)
# Return one specific day by id when the week belongs to a team owned by current user.
def get_day(week_id: uuid.UUID, day_id: uuid.UUID,
			db: Session = Depends(get_db),
			current_user = Depends(get_current_user)):
	week = db.query(models.TrainingWeek).join(models.Team).filter(
		models.TrainingWeek.id == week_id,
		models.Team.owner_id == current_user.id,
	).first()
	if week is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Week not found")

	day = db.query(models.WeekDay).filter(
		models.WeekDay.id == day_id,
		models.WeekDay.week_id == week_id,
	).first()
	if day is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")
	return day


@router.delete("/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
# Delete a day only when the week belongs to a team owned by current user.
def delete_day(week_id: uuid.UUID, day_id: uuid.UUID,
			   db: Session = Depends(get_db),
			   current_user = Depends(get_current_user)):
	week = db.query(models.TrainingWeek).join(models.Team).filter(
		models.TrainingWeek.id == week_id,
		models.Team.owner_id == current_user.id,
	).first()
	if week is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Week not found")

	day = db.query(models.WeekDay).filter(
		models.WeekDay.id == day_id,
		models.WeekDay.week_id == week_id,
	).first()
	if day is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")

	db.delete(day)
	db.commit()


@router.put("/{day_id}", response_model=WeekDayResponse,
			status_code=status.HTTP_200_OK)
# Update day name and date only when the week belongs to a team owned by current user.
def update_day(week_id: uuid.UUID, day_id: uuid.UUID,
			   day_data: UpdateWeekDay,
			   db: Session = Depends(get_db),
			   current_user = Depends(get_current_user)):
	week = db.query(models.TrainingWeek).join(models.Team).filter(
		models.TrainingWeek.id == week_id,
		models.Team.owner_id == current_user.id,
	).first()
	if week is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Week not found")

	day = db.query(models.WeekDay).filter(
		models.WeekDay.id == day_id,
		models.WeekDay.week_id == week_id,
	).first()
	if day is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")

	day.dia = day_data.dia
	day.fecha = day_data.fecha
	try:
		db.commit()
	except IntegrityError:
		db.rollback()
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not update day")

	db.refresh(day)
	return day
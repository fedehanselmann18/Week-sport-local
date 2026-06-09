from fastapi import APIRouter, status, HTTPException, Depends
from app.db.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db import models
from app.schemas.day import CreateDayActivity, DayActivityResponse, UpdateDayActivity
from app.oAuth2 import get_current_user
import uuid


router = APIRouter(
	prefix="/days/{day_id}/activities",
	tags=['Day Activities']
)


@router.post("/", response_model=DayActivityResponse,
			 status_code=status.HTTP_201_CREATED)
# Create an activity only when the day belongs to a team owned by current user.
def create_activity(day_id: uuid.UUID, activity: CreateDayActivity,
				db: Session = Depends(get_db),
				current_user = Depends(get_current_user)):
	day = db.query(models.WeekDay).join(models.TrainingWeek).join(models.Team).filter(
		models.WeekDay.id == day_id,
		models.Team.owner_id == current_user.id,
	).first()
	if day is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")

	new_activity = models.DayActivity(
		day_id=day_id,
		horario=activity.horario,
		lugar=activity.lugar,
		descripcion=activity.descripcion,
	)
	db.add(new_activity)
	try:
		db.commit()
	except IntegrityError:
		db.rollback()
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not create activity")

	db.refresh(new_activity)
	return new_activity


@router.get("/", response_model=list[DayActivityResponse],
			status_code=status.HTTP_200_OK)
# Return all activities of a day only when the day belongs to a team owned by current user.
def get_activities(day_id: uuid.UUID, db: Session = Depends(get_db),
			   current_user = Depends(get_current_user)):
	day = db.query(models.WeekDay).join(models.TrainingWeek).join(models.Team).filter(
		models.WeekDay.id == day_id,
		models.Team.owner_id == current_user.id,
	).first()
	if day is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")
	return db.query(models.DayActivity).filter(models.DayActivity.day_id == day_id).all()


@router.get("/{activity_id}", response_model=DayActivityResponse,
			status_code=status.HTTP_200_OK)
# Return one specific activity by id when the day belongs to a team owned by current user.
def get_activity(day_id: uuid.UUID, activity_id: uuid.UUID,
			 db: Session = Depends(get_db),
			 current_user = Depends(get_current_user)):
	day = db.query(models.WeekDay).join(models.TrainingWeek).join(models.Team).filter(
		models.WeekDay.id == day_id,
		models.Team.owner_id == current_user.id,
	).first()
	if day is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")

	activity = db.query(models.DayActivity).filter(
		models.DayActivity.id == activity_id,
		models.DayActivity.day_id == day_id,
	).first()
	if activity is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
	return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
# Delete an activity only when the day belongs to a team owned by current user.
def delete_activity(day_id: uuid.UUID, activity_id: uuid.UUID,
				db: Session = Depends(get_db),
				current_user = Depends(get_current_user)):
	day = db.query(models.WeekDay).join(models.TrainingWeek).join(models.Team).filter(
		models.WeekDay.id == day_id,
		models.Team.owner_id == current_user.id,
	).first()
	if day is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")

	activity = db.query(models.DayActivity).filter(
		models.DayActivity.id == activity_id,
		models.DayActivity.day_id == day_id,
	).first()
	if activity is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

	db.delete(activity)
	db.commit()


@router.put("/{activity_id}", response_model=DayActivityResponse,
			status_code=status.HTTP_200_OK)
# Update activity fields only when the day belongs to a team owned by current user.
def update_activity(day_id: uuid.UUID, activity_id: uuid.UUID,
				activity_data: UpdateDayActivity,
				db: Session = Depends(get_db),
				current_user = Depends(get_current_user)):
	day = db.query(models.WeekDay).join(models.TrainingWeek).join(models.Team).filter(
		models.WeekDay.id == day_id,
		models.Team.owner_id == current_user.id,
	).first()
	if day is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")

	activity = db.query(models.DayActivity).filter(
		models.DayActivity.id == activity_id,
		models.DayActivity.day_id == day_id,
	).first()
	if activity is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

	activity.horario = activity_data.horario
	activity.lugar = activity_data.lugar
	activity.descripcion = activity_data.descripcion
	try:
		db.commit()
	except IntegrityError:
		db.rollback()
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not update activity")

	db.refresh(activity)
	return activity

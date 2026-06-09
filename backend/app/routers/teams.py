from pathlib import Path
import secrets

from fastapi import APIRouter, status, Depends, File, UploadFile, HTTPException
from app.db.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db import models
from app.schemas.team import CreateTeam, TeamResponse, UpdateTeam
from app.oAuth2 import get_current_user
import uuid


STATIC_PHOTOS_DIR = Path(__file__).resolve().parents[1] / "static" / "team_photos"
ALLOWED_PHOTO_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_PHOTO_SIZE = 2 * 1024 * 1024


router = APIRouter(
    prefix="/teams",
    tags=['Teams']
)

@router.post("/", response_model=TeamResponse,
             status_code=status.HTTP_201_CREATED)
# Create a team and assign it to the currently authenticated user.
def create_team(team: CreateTeam, db: Session = Depends(get_db),
                current_user = Depends(get_current_user)):
    new_team = models.Team(
        nombre=team.nombre,
        deporte=team.deporte,
        owner_id=current_user.id,
    )
    db.add(new_team)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Team name already exists",
        )

    db.refresh(new_team)
    return new_team


@router.get("/", response_model=list[TeamResponse],
            status_code=status.HTTP_200_OK)
# Return all teams that belong to the currently authenticated user.
def get_my_teams(db: Session = Depends(get_db),
                 current_user = Depends(get_current_user)):
    return db.query(models.Team).filter(models.Team.owner_id == current_user.id).all()


@router.get("/{team_id}", response_model=TeamResponse,
            status_code=status.HTTP_200_OK)
# Return one team only if it belongs to the current authenticated user.
def get_team(team_id: uuid.UUID, db: Session = Depends(get_db),
             current_user = Depends(get_current_user)):
    team = db.query(models.Team).filter(
        models.Team.id == team_id,
        models.Team.owner_id == current_user.id,
    ).first()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
# Delete a team only if it exists and belongs to the currently authenticated user.
def delete_team(team_id: uuid.UUID, db: Session = Depends(get_db),
                current_user = Depends(get_current_user)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this team")
    db.delete(team)
    db.commit()


@router.put("/{team_id}", response_model=TeamResponse,
            status_code=status.HTTP_200_OK)
# Update team name and sport only if the team belongs to the current user.
def update_team(team_id: uuid.UUID, team_data: UpdateTeam,
                db: Session = Depends(get_db),
                current_user = Depends(get_current_user)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this team")

    team.nombre = team_data.nombre
    team.deporte = team_data.deporte

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Team name already exists")

    db.refresh(team)
    return team


@router.post("/{team_id}/photo", response_model=TeamResponse,
             status_code=status.HTTP_200_OK)
# Upload or replace a team photo/logo.
def upload_team_photo(team_id: uuid.UUID,
                      photo: UploadFile = File(...),
                      db: Session = Depends(get_db),
                      current_user = Depends(get_current_user)):
    team = db.query(models.Team).filter(
        models.Team.id == team_id,
        models.Team.owner_id == current_user.id,
    ).first()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    if photo.content_type not in ALLOWED_PHOTO_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only JPG, PNG and WEBP images are allowed")

    file_bytes = photo.file.read()
    if len(file_bytes) > MAX_PHOTO_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image size must be 2MB or less")

    extension = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }[photo.content_type]

    STATIC_PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{team_id}_{secrets.token_hex(8)}{extension}"
    relative_path = f"static/team_photos/{filename}"
    (STATIC_PHOTOS_DIR / filename).write_bytes(file_bytes)

    team.foto_url = relative_path
    db.commit()
    db.refresh(team)
    return team
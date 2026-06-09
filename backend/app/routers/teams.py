from fastapi import APIRouter, status, Depends, HTTPException
from app.db.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db import models
from app.schemas.team import CreateTeam, TeamResponse, UpdateTeam
from app.oAuth2 import get_current_user
import uuid


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
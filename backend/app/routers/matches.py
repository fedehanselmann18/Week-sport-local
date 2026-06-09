from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db import models
from app.db.db import get_db
from app.oAuth2 import get_current_user
from app.schemas.match import CreateMatch, UpdateMatch, MatchResponse
import uuid


router = APIRouter(
    prefix="/teams/{team_id}/matches",
    tags=["Matches"],
)


@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(team_id: uuid.UUID, payload: CreateMatch,
                 db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    team = db.query(models.Team).filter(
        models.Team.id == team_id,
        models.Team.owner_id == current_user.id,
    ).first()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    new_match = models.Match(
        team_id=team_id,
        rival=payload.rival,
        fecha=payload.fecha,
        resultado=payload.resultado,
        notas=payload.notas,
    )
    db.add(new_match)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not create match")

    db.refresh(new_match)
    return new_match


@router.get("/", response_model=list[MatchResponse], status_code=status.HTTP_200_OK)
def get_matches(team_id: uuid.UUID,
                db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    team = db.query(models.Team).filter(
        models.Team.id == team_id,
        models.Team.owner_id == current_user.id,
    ).first()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return db.query(models.Match).filter(models.Match.team_id == team_id).all()


@router.get("/{match_id}", response_model=MatchResponse, status_code=status.HTTP_200_OK)
def get_match(team_id: uuid.UUID, match_id: uuid.UUID,
              db: Session = Depends(get_db),
              current_user=Depends(get_current_user)):
    team = db.query(models.Team).filter(
        models.Team.id == team_id,
        models.Team.owner_id == current_user.id,
    ).first()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    match = db.query(models.Match).filter(
        models.Match.id == match_id,
        models.Match.team_id == team_id,
    ).first()
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match


@router.put("/{match_id}", response_model=MatchResponse, status_code=status.HTTP_200_OK)
def update_match(team_id: uuid.UUID, match_id: uuid.UUID, payload: UpdateMatch,
                 db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    team = db.query(models.Team).filter(
        models.Team.id == team_id,
        models.Team.owner_id == current_user.id,
    ).first()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    match = db.query(models.Match).filter(
        models.Match.id == match_id,
        models.Match.team_id == team_id,
    ).first()
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    match.rival = payload.rival
    match.fecha = payload.fecha
    match.resultado = payload.resultado
    match.notas = payload.notas
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not update match")

    db.refresh(match)
    return match


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(team_id: uuid.UUID, match_id: uuid.UUID,
                 db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    team = db.query(models.Team).filter(
        models.Team.id == team_id,
        models.Team.owner_id == current_user.id,
    ).first()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    match = db.query(models.Match).filter(
        models.Match.id == match_id,
        models.Match.team_id == team_id,
    ).first()
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    db.delete(match)
    db.commit()

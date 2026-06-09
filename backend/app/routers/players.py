from fastapi import APIRouter, status, HTTPException, Depends
from app.db.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db import models
from app.schemas.player import CreatePlayer, PlayerResponse, UpdatePlayer
from app.oAuth2 import get_current_user
import uuid


router = APIRouter(
	prefix="/teams/{team_id}/players",
	tags=['Players']
)


@router.post("/", response_model=PlayerResponse,
			 status_code=status.HTTP_201_CREATED)
# Create a new player inside the selected team if the current user owns the team.
def create_player(team_id: uuid.UUID, player: CreatePlayer,
				  db: Session = Depends(get_db),
				  current_user = Depends(get_current_user)):
	team = db.query(models.Team).filter(
		models.Team.id == team_id,
		models.Team.owner_id == current_user.id,
	).first()
	if team is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

	new_player = models.Player(
		team_id=team_id,
		nombre=player.nombre,
		apellido=player.apellido,
		posicion=player.posicion,
		dorsal=player.dorsal,
		notas=player.notas,
	)
	db.add(new_player)
	try:
		db.commit()
	except IntegrityError:
		db.rollback()
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not create player")

	db.refresh(new_player)
	return new_player


@router.get("/", response_model=list[PlayerResponse],
			status_code=status.HTTP_200_OK)
# Return all players of a team only when the current user owns that team.
def get_players(team_id: uuid.UUID, db: Session = Depends(get_db),
				current_user = Depends(get_current_user)):
	team = db.query(models.Team).filter(
		models.Team.id == team_id,
		models.Team.owner_id == current_user.id,
	).first()
	if team is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
	return db.query(models.Player).filter(models.Player.team_id == team_id).all()


@router.get("/{player_id}", response_model=PlayerResponse,
            status_code=status.HTTP_200_OK)
# Return one specific player by id when it belongs to the selected owned team.
def get_player(team_id: uuid.UUID, player_id: uuid.UUID,
               db: Session = Depends(get_db),
               current_user = Depends(get_current_user)):
	team = db.query(models.Team).filter(
		models.Team.id == team_id,
		models.Team.owner_id == current_user.id,
	).first()
	if team is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

	player = db.query(models.Player).filter(
		models.Player.id == player_id,
		models.Player.team_id == team_id,
	).first()
	if player is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
	return player


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
# Delete a specific player from the selected team if the current user owns that team.
def delete_player(team_id: uuid.UUID, player_id: uuid.UUID,
				  db: Session = Depends(get_db),
				  current_user = Depends(get_current_user)):
	team = db.query(models.Team).filter(
		models.Team.id == team_id,
		models.Team.owner_id == current_user.id,
	).first()
	if team is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

	player = db.query(models.Player).filter(
		models.Player.id == player_id,
		models.Player.team_id == team_id,
	).first()
	if player is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

	db.delete(player)
	db.commit()


@router.put("/{player_id}", response_model=PlayerResponse,
			status_code=status.HTTP_200_OK)
# Update player data in the selected team if the current user owns that team.
def update_player(team_id: uuid.UUID, player_id: uuid.UUID,
				  player_data: UpdatePlayer,
				  db: Session = Depends(get_db),
				  current_user = Depends(get_current_user)):
	team = db.query(models.Team).filter(
		models.Team.id == team_id,
		models.Team.owner_id == current_user.id,
	).first()
	if team is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

	player = db.query(models.Player).filter(
		models.Player.id == player_id,
		models.Player.team_id == team_id,
	).first()
	if player is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

	player.nombre = player_data.nombre
	player.apellido = player_data.apellido
	player.posicion = player_data.posicion
	player.dorsal = player_data.dorsal
	player.notas = player_data.notas

	try:
		db.commit()
	except IntegrityError:
		db.rollback()
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not update player")

	db.refresh(player)
	return player

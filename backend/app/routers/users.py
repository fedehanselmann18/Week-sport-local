from fastapi import APIRouter, status, HTTPException, Depends
from app.db.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db import models
from app.schemas.user import CreateUser, UpdateUsername, UserResponse
from app.oAuth2 import get_current_user
from app.verification import hash_password


router = APIRouter(
    prefix="/user",
    tags=['User']
)

@router.get("/me", response_model=UserResponse)
# Return the profile data of the currently authenticated user.
def get_current_user_data(db: Session = Depends(get_db),
                current_user = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Authenticated user not found.")
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# Create a new user account with a hashed password.
def create_user(user: CreateUser, db: Session = Depends(get_db)):
    new_user = models.User(
        email=user.email,
        password=hash_password(user.password),
        username=user.username,
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    db.refresh(new_user)
    return new_user

@router.delete("/me")
# Delete the currently authenticated user account.
def delete_my_user(current_user = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Authenticated user not found")
    db.query(models.User).filter(models.User.id == current_user.id).delete(synchronize_session=False)
    db.commit()
    return {"message": f"User with id: {current_user.id} has been deleted"}


@router.put("/me", response_model=UserResponse)
# Update the username of the currently authenticated user.
def update_current_user(user: UpdateUsername, db: Session = Depends(get_db),
                current_user = Depends(get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == current_user.id)
    old_user = user_query.first()
    if not old_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Authenticated user not found.")

    username_exists = db.query(models.User).filter(
        models.User.username == user.username,
        models.User.id != current_user.id,
    ).first()
    if username_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")

    user_query.update({"username": user.username}, synchronize_session=False)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
    return user_query.first()
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.db import models
from app.schemas.token import TokenResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.oAuth2 import create_access_token
from app.verification import verify_password

router = APIRouter(
    tags=['Authentication']
)


@router.post("/login",response_model=TokenResponse)
# Authenticate user by email or username and return a JWT access token.
def login(db: Session = Depends(get_db),
          user_credentials: OAuth2PasswordRequestForm = Depends()):
    user = db.query(models.User).filter(
        or_(
            models.User.email == user_credentials.username,
            models.User.username == user_credentials.username,
        )
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials",
        )

    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials",
        )

    access_token = create_access_token(data={"user_id": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
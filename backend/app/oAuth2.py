from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from app.schemas import token as tockenschema
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db import models
from app.db.db import get_db
from app.config import settings 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# SECRET_KEY
# ALGORITHM
# ACCESS_TOKEN_EXPIRE_MINUTES

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict):
    # Create a copy of the data to encode
    to_encode = data.copy()

    # Set the expiration time for the token
    # Time now + 30 minutes (30 minutes from the moment the token is created)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Update the data to encode with the expiration time
    to_encode.update({"exp": expire})

    # GIVE THE DATA TO ENCODE, THE SECRET KEY AND THE ALGORITHM TO CREATE THE TOKEN
    # it cannot be hacked because the secret key is only known by the server
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token: str, credentials_exception):

    try:
        decoded_token = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

        id : str = decoded_token.get("user_id")

        if id == None:
            raise credentials_exception
        
        token_data = tockenschema.TokenData(user_id = id)

    except JWTError:
        raise credentials_exception
    
    return token_data # So that we can get use of the data
    
# If we for example want to post something and you
# have to be logged in, so you add it as a dependency to the route

def get_current_user(token: str = Depends(oauth2_scheme),
                     db : Session = Depends(get_db)):

    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    
    # Instead of returning the token data, we'll return
    # directly the user, so we can use it in the route

    token_data = verify_access_token(token, credentials_exception)
    # we search for the user in database with the same id as the
    # one in the token data.
    user = db.query(models.User).filter(models.User.id==token_data.user_id).first()

    if user is None:
        raise credentials_exception

    # we dont validate because we know its valid token (validated before)
    return user
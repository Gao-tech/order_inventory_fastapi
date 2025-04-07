import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException,status
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select
from .models import TokenData, User
from .db import get_session
from .config import settings

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")
oauth2_schema_admin = OAuth2PasswordBearer(tokenUrl="login_admin")


# SECRET_KEY   SECRET_KEY_ADMIN
# Algorithm
# Expriation time

SECRET_KEY = settings.secret_key
SECRET_KEY_ADMIN = settings.secret_key_admin
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPERIE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)+timedelta(ACCESS_TOKEN_EXPERIE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

    return encoded_jwt
    
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)  # here to extract id only but can do more.
    except jwt.PyJWKError:
        raise credentials_exception
    
    return token_data

#to protect the endpoint. Login to verify if it is a valid user.
def get_current_user(token: str=Depends(oauth2_schema), session: Session=Depends(get_session)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                         detail=f"Could not validate credentials", 
                                         headers={"WWW-Authenticate": "Bearer"})
    
    token = verify_access_token(token, credential_exception)
    user = session.exec(select(User).where(User.id==token.id)).first()

    return user


## Login Admin
def create_adimin_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)+timedelta(ACCESS_TOKEN_EXPERIE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY_ADMIN, ALGORITHM)

    return encoded_jwt
    
def verify_admin_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY_ADMIN, algorithms=[ALGORITHM])
        role: str = payload.get("user_role")
        id: int = payload.get("user_id")
        if role is None or id is None:
            raise credentials_exception
        token_data_admin = TokenData(id=id)  # here to extract id only but can do more.
    except jwt.PyJWKError:
        raise credentials_exception
    
    return token_data_admin

#to protect the endpoint. Login to verify if it is a valid user.

def get_admin(token: str = Depends(oauth2_schema_admin), session: Session = Depends(get_session)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                         detail="Could not validate credentials", 
                                         headers={"WWW-Authenticate": "Bearer"})

    token_data = verify_admin_token(token, credential_exception)
    
    admin = session.exec(select(User).where(User.id == token_data.id)).first()

    if not admin or getattr(admin, "role", None) != "admin":
        raise credential_exception

    return admin

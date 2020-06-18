""" Auth router. """
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

from ..config import get_config
from ..db import Controller
from ..exceptions import BadPayloadError, ClientNotFoundError, \
    InvalidCredentialsError
from ..models import Client


router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.on_event('startup')
async def startup_event():
    global controller
    config = get_config()
    controller = Controller(config.DB_DSN)
    await controller.connect()


@router.on_event('shutdown')
async def startup_event():
    await controller.disconnect()


def create_access_token(data: dict, expires_delta_sec: int = 7 * 24 * 3600):
    to_encode = data.copy()
    to_encode.update({
        "exp": datetime.utcnow() + timedelta(seconds=expires_delta_sec)
    })
    return jwt.encode(to_encode, key=get_config().JWT_SECRET,
                      algorithm='HS256')


async def auth_client(token: str = Depends(oauth2_scheme)) -> Client:
    try:
        payload = jwt.decode(token, get_config().JWT_SECRET,
                             algorithms=['HS256'])
        client_id: str = payload.get("sub")
        if client_id is None:
            raise BadPayloadError
        client = await controller.get_client(client_id)
    except (jwt.PyJWTError, ClientNotFoundError, InvalidCredentialsError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"})
    return client


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        client = await controller.get_client_verify(
            form_data.username, form_data.password)
    except ClientNotFoundError:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password")
    token_data = {
        "access_token": create_access_token({"sub": client.id}),
        "token_type": "bearer"}
    return token_data

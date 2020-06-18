""" Basic router located at / endpoint. """
from typing import List

from fastapi import APIRouter, Depends

from .auth import auth_client
from ..db import Controller
from ..exceptions import ClientNotFoundError, InsufficientFundsError, \
    UsernameAlreadyRegisteredError
from ..models import Client, ClientOut, CreateClientBody, Error, Response, \
    Status, TopupBody, TransferBody, TransferOut
from ..config import get_config


router = APIRouter()

# Async init on startup
controller: Controller


@router.on_event('startup')
async def startup_event():
    global controller
    config = get_config()
    controller = Controller(config.DB_DSN)
    await controller.connect()


@router.on_event('shutdown')
async def shutdown_event():
    await controller.disconnect()


@router.get('/transfers', response_model=Response[List[TransferOut]],
            response_model_exclude_unset=True)
async def list_transfers(page_num: int = 0,
                         client: Client = Depends(auth_client)):
    """ List client's transfers. """
    transfers = await controller.list_transfers(client.id, page_num)
    return {'data': transfers}


@router.post('/transfers', response_model=Response[Status],
             response_model_exclude_unset=True)
async def create_transfer(body: TransferBody,
                          client: Client = Depends(auth_client)):
    """ Transfer funds between clients.

    Auth required.
    """
    try:
        if client.balance < body.amount:
            raise InsufficientFundsError()
        async with controller.transaction():
            await controller.transfer(body.amount, client.id,
                                      to_username=body.to)
    except InsufficientFundsError:
        e = Error(code=400, message="Insufficient funds.")
        return {'error': e}
    return {'data': {'status': True}}


@router.post('/clients', response_model=Response[ClientOut],
             response_model_exclude_unset=True)
async def create(body: CreateClientBody):
    """ Create client. """
    try:
        client_id: int = await controller.create_client(
            body.username, str(body.password))
        client = ClientOut(id=client_id, username=body.username, balance="0.0")
        return {'data': client}
    except UsernameAlreadyRegisteredError:
        e = Error(code=400, message="Username already registered.")
        return {'error': e}


@router.get('/clients', response_model=Response[ClientOut],
            response_model_exclude_unset=True)
async def get_client_info(client: Client = Depends(auth_client)):
    """ Get client info.

    Auth required.
    """
    try:
        return {'data': client}
    except UsernameAlreadyRegisteredError:
        e = Error(code=400, message="Username already registered.")
        return {'error': e}


@router.post('/topup', response_model=Response[Status],
             response_model_exclude_unset=True)
async def topup(body: TopupBody):
    """ Topping up clients wallet. """
    try:
        async with controller.transaction():
            await controller.topup(body.to, body.amount)
    except ClientNotFoundError:
        e = Error(code=404, message="Client not found.")
        return {'error': e}
    return {'data': {'status': True}}

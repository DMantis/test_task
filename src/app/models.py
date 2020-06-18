from datetime import datetime
from decimal import Decimal
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, SecretStr, validator
from pydantic.generics import GenericModel


DataT = TypeVar('DataT')


class Error(BaseModel):
    code: int
    message: str


class Response(GenericModel, Generic[DataT]):
    data: Optional[DataT]
    error: Optional[Error]


class Status(BaseModel):
    status: bool


class ClientOut(BaseModel):
    id: int
    username: str
    balance: Decimal


class Client(ClientOut):
    pwd_hash: str


class TransferOut(BaseModel):
    amount: Decimal
    created_at: datetime
    from_username: Optional[str]
    to_username: str


class Transfer(TransferOut):
    pass


class TransferBody(BaseModel):
    to: str
    amount: Decimal

    @validator('amount')
    def validate_amount(cls, v: Decimal):
        vs = str(v)
        if '.' in vs:
            if len(vs.split('.')[1]) > 2:
                raise ValueError("Bad precision for USD currency")
        if v < Decimal(0):
            raise ValueError("'amount' can't be negative.")
        return v


class TopupBody(TransferBody):
    pass


class CreateClientBody(BaseModel):
    username: str
    password: SecretStr

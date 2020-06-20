from decimal import Decimal

from asyncpg.exceptions import UniqueViolationError
from databases import Database
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Column, DateTime, ForeignKey, Integer, MetaData, \
    Numeric, String, Table

from .exceptions import ClientNotFoundError, InvalidCredentialsError, \
    UsernameAlreadyRegisteredError
from .models import Client, Transfer


metadata = MetaData()

clients = Table(
    'clients',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(32)),
    Column('pwd_hash', String(256)),
    Column('balance', Numeric(10, 2), server_default='0'),
    Column('created_at', DateTime, server_default='NOW()')
)

transfers = Table(
    'transfers',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('amount', Numeric(10, 2)),
    Column('from_id', Integer, ForeignKey('clients.id'), nullable=True,
           server_default='NULL'),
    Column('to_id', Integer, ForeignKey('clients.id'), nullable=False,
           server_default='NULL'),
    Column('created_at', DateTime, server_default='NOW()')
)


class Controller(Database):
    """ Basic application controller. """

    async def create_client(self, username: str, password: str) -> int:
        """ Create client in database.

        :param username: client's username.
        :param password: client's password.
        :return: client's db id.
        """
        # passlib will handle both salt gen and hashing and return their
        # concatenated result with info about used algorithm.
        hashed_password = pbkdf2_sha256.hash(password)
        try:
            query = clients.insert().values(
                username=username,
                pwd_hash=hashed_password)
            return await self.fetch_val(query)
        except UniqueViolationError:
            raise UsernameAlreadyRegisteredError()

    async def get_client(
            self,
            client_id: int = None,
            username: str = None) -> Client:
        """ Get client by client_id or username.
        client_id has priority over username if both provided.

        :param client_id: client's database id.
        :param username: client's username.
        :return: client model.
        """
        if client_id is not None:
            query = clients.select().where(clients.c.id == client_id)
        elif username is not None:
            query = clients.select().where(clients.c.username == username)
        else:
            raise ValueError("Either client_id or username must be provided.")
        row = await self.fetch_one(query)
        if not row:
            raise ClientNotFoundError()
        return Client(**row)

    async def get_client_verify(self, username: str, password: str) -> Client:
        """ Get client after password verification or raise exception.

        :param username: client's username.
        :param password: client's password.
        :return: client model.
        """
        client = await self.get_client(username=username)
        if not pbkdf2_sha256.verify(password, client.pwd_hash):
            raise InvalidCredentialsError()
        return client

    async def topup(self, username: str, amount: Decimal) -> None:
        """ Top up client's account with specified amount.

        :param username: client's username.
        :param amount: amount to add on clients account.
        :return: None
        """

        client_to = await self.get_client(username=username)

        query = clients.update().\
            values(balance=clients.c.balance + amount).\
            where(clients.c.username == username)
        await self.execute(query)

        query = transfers.insert().values(
            amount=amount,
            from_id=None,
            to_id=client_to.id)
        await self.execute(query)

    async def transfer(self, amount: Decimal, from_id: int, to_id: int = None,
                       to_username: str = None) -> None:
        """ Transfer specified amount from `from_id` client to `to_id` client.

        Vulnerable to race conditions if not in database transaction,
        so this method MUST BE executed in transaction.

        Recipient must be be set either via id or username.

        :param from_id: sender id.
        :param amount: transfer amount.
        :param to_id: recipient's id.
        :param to_username: recipient's username.
        :return:
        """
        client_to = await self.get_client(username=to_username)

        # add funds.
        if to_id is not None:
            query = clients.update(). \
                values(balance=clients.c.balance + amount). \
                where(clients.c.id == to_id)
        elif to_username is not None:
            query = clients.update(). \
                values(balance=clients.c.balance + amount). \
                where(clients.c.username == to_username)
        else:
            raise ValueError("Either to_id or to_username must be provided.")
        await self.execute(query)

        query = clients.update().\
            values(balance=clients.c.balance - amount).\
            where(clients.c.id == from_id)
        await self.execute(query)

        query = transfers.insert().values(
            amount=amount,
            from_id=from_id,
            to_id=client_to.id)
        await self.execute(query)

    async def list_transfers(self, client_id: int, page_num: int = 0,
                             page_size: int = 25):
        """ Paged method to list user related transfers"""
        # haven't got much time to figure out this query in sqlalchemy, so
        # made it by hand
        query = "SELECT transfers.amount, from_c.username as from_username, " \
                "to_c.username as to_username, transfers.created_at " \
                "FROM transfers " \
                "FULL JOIN clients AS from_c ON transfers.from_id = from_c.id" \
                " JOIN clients AS to_c ON transfers.to_id = to_c.id " \
                "WHERE transfers.from_id = :client_id OR " \
                "transfers.to_id = :client_id " \
                "ORDER BY transfers.created_at DESC " \
                "LIMIT :limit OFFSET :offset;"
        values = {
            'limit': page_size,
            'offset': page_num * page_size,
            'client_id': client_id}
        rows = await self.fetch_all(query, values)
        return [Transfer.construct(**row) for row in rows]

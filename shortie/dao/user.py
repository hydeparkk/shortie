from passlib.hash import sha256_crypt

from .base import DaoBase
from .exception import DaoException


class UserException(DaoException):
    pass


class User(DaoBase):

    COLLECTION_NAME = 'users'

    def __init__(self, db, data):
        super().__init__(db)
        self.collection = self.db[self.COLLECTION_NAME]

        self.email = data.get('email')
        self.password = data.get('password')

    async def validate_user(self):
        user = await self.collection.find_one({'email': self.email})

        if not user:
            raise UserException('User does not exists.')

        if not sha256_crypt.verify(self.password, user.get('password')):
            raise UserException('Incorrect password.')

    async def save_user(self):
        if not self.email or not self.password:
            raise UserException('Email and password are required.')

        if not await self.collection.find_one({'email': self.email}):
            await self.collection.insert_one({
                'email': self.email,
                'password': sha256_crypt.hash(self.password)
            })
        else:
            raise UserException('User already exists.')

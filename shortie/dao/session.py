from datetime import datetime

import jwt

from .base import DaoBase
from .exception import DaoException
from ..settings import settings


class SessionException(DaoException):
    pass


class Session(DaoBase):

    COLLECTION_NAME = 'sessions'

    def __init__(self, db):
        super().__init__(db)
        self.collection = self.db[self.COLLECTION_NAME]

    async def set_session(self, email):
        token = await self.get_session_by_email(email)
        if token:
            return token

        now = datetime.utcnow().replace(microsecond=0)
        token = jwt.encode(
            {
                'email': email,
                'iat': now
            },
            settings.SHORTIE_SECRET,
            algorithm='HS256'
        ).decode('utf-8')

        sess = {
            'created_at': now,
            'email': email
        }

        await self.collection.insert_one(sess)

        return token

    async def get_session(self, token):
        try:
            decoded = jwt.decode(
                token,
                settings.SHORTIE_SECRET,
                algorithm='HS256'
            )
        except jwt.InvalidTokenError:
            raise SessionException('Incorrect session token.')

        sess = await self.collection.find_one(
            {
                'email': decoded.get('email'),
                'created_at': datetime.utcfromtimestamp(decoded.get('iat'))
            }
        )

        if sess:
            return sess.get('email')

        raise SessionException('Session does not exists.')

    async def get_session_by_email(self, email):
        sess = await self.collection.find_one({'email': email})

        if sess:
            return jwt.encode(
                {
                    'email': email,
                    'iat': sess.get('created_at')
                },
                settings.SHORTIE_SECRET,
                algorithm='HS256'
            ).decode('utf-8')
        return None

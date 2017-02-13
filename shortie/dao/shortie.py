import re
from datetime import datetime

from hashids import Hashids

from pymongo.collection import ReturnDocument

from ..settings import settings

from .base import DaoBase
from .exception import DaoException


class ShortieException(DaoException):
    pass


class Shortie(DaoBase):

    COLLECTION_NAME = 'shorties'
    COUNTERS_COLLECTION_NAME = 'counters'

    def __init__(self, db):
        super().__init__(db)
        self.collection = self.db[self.COLLECTION_NAME]
        self.counters = self.db[self.COUNTERS_COLLECTION_NAME]

        self.hasher = Hashids(salt=settings.SHORTIE_SECRET, min_length=5)

        self.name_pattern = re.compile('^[a-zA-Z0-9]+$')

    async def save(self, url, user_id=None, name=None):
        if name:
            if await self.get(name):
                raise ShortieException(
                    'This name ({}) already exists'.format(name))
            if not self.name_pattern.match(name):
                raise ShortieException(
                    'Name should contain only alphanumeric chars (a-zA-Z0-9)'
                )
            shortie = name
        else:
            res = await self.find_full_url(url)
            if res:
                if user_id:
                    await self.collection.update(
                        {'_id': res.get('_id')},
                        {'$addToSet': {'users': user_id}}
                    )
                return res.get('shortie')

            counter = await self.counters.find_one_and_update(
                {'_id': 'shortie'}, {'$inc': {'seq': 1}},
                projection={'_id': False, 'seq': True},
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
            shortie = self.hasher.encode(counter.get('seq'))

        doc = {
            'url': url,
            'shortie': shortie,
            'users': [user_id, ] if user_id else [],
            'clicks': [],
            'created_at': datetime.utcnow()
        }

        await self.collection.insert_one(doc)

        return shortie

    async def get(self, shortie_id):
        return await self.collection.find_one(
            {'shortie': shortie_id}, projection={'_id': False, 'users': False}
        )

    async def find_full_url(self, full_url):
        return await self.collection.find_one(
            {'url': full_url}
        )

    async def get_url(self, shortie_id):
        res = await self.collection.find_one_and_update(
            {'shortie': shortie_id},
            {'$push': {'clicks': datetime.utcnow()}},
            projection={'_id': False, 'url': True},
            return_document=ReturnDocument.AFTER
        )
        if res:
            return res.get('url')

    async def get_user_shorties(self, user_id):
        return await self.collection.find(
            {'users': user_id}, projection={'users': False, '_id': False}
        ).to_list(None)

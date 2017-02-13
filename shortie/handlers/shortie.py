import json

from tornado.web import HTTPError

from .base import BaseHandler
from ..dao import DaoException, Session, Shortie


class ShortenHandler(BaseHandler):

    async def prepare(self):
        super().prepare()
        self.shortie_dao = Shortie(self.db)
        self.user_email = None

        session_dao = Session(self.db)
        auth_header = self.request.headers.get('Authorization')

        if auth_header:
            try:
                self.user_email = await session_dao.get_session(auth_header)
            except DaoException as err:
                raise HTTPError(
                    status_code=401,
                    reason=err.message
                )

    async def get(self, *args, **kwargs):
        res = await self.shortie_dao.get_url(kwargs.get('shortie'))
        if res:
            self.finish({'url': res})
        else:
            raise HTTPError(
                status_code=404,
                reason='Shortie does not exists.'
            )

    async def post(self, *args, **kwargs):
        data = json.loads(self.request.body)

        if 'url' not in data:
            raise HTTPError(
                status_code=400,
                reason='url field is required!'
            )

        try:
            res = await self.shortie_dao.save(
                data['url'], self.user_email, data.get('name')
            )
            self.finish({
                'shortie': '{protocol}://{host}/api/shortie/{shortie}'.format(
                    **vars(self.request), shortie=res
                )
            })
        except DaoException as err:
            raise HTTPError(
                status_code=400,
                reason=err.message
            )

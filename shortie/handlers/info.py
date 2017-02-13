from tornado.web import HTTPError

from .base import BaseHandler
from ..dao import Shortie


class InfoHandler(BaseHandler):

    def jsonify_shortie(self, shortie):
        clicks = []

        shortie['created_at'] = str(shortie.get('created_at'))

        for click in shortie.get('clicks'):
            clicks.append(str(click))
        shortie['clicks'] = clicks

        return shortie

    def prepare(self):
        super().prepare()
        self.shortie_dao = Shortie(self.db)

    async def get(self):
        email = self.get_argument('email', None)
        if email:
            shorties = await self.shortie_dao.get_user_shorties(email)
            if shorties:
                self.finish(
                    {
                        'shorties': [
                            self.jsonify_shortie(shortie)
                            for shortie in shorties
                        ]
                    }
                )
                return

            raise HTTPError(
                status_code=404,
                reason=(
                    'User does not have any shorties or User does not exists'
                )
            )

        shortie_id = self.get_argument('shortie', None)
        if shortie_id:
            shortie = await self.shortie_dao.get(shortie_id)
            if shortie:
                self.finish(self.jsonify_shortie(shortie))
                return

            raise HTTPError(
                status_code=404,
                reason='Shortie does not exists.'
            )

        raise HTTPError(
            status_code=400,
            reason=(
                '"shortie" or "email" parameter with proper value is required'
            )
        )

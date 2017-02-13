import json

from tornado.web import HTTPError

from ..dao import DaoException, Session, SessionException, User
from .base import BaseHandler


class AuthHandler(BaseHandler):

    def initialize(self, register=False):
        self.register = register

    async def post(self):
        login_data = json.loads(self.request.body)

        try:
            user = User(self.db, login_data)
            if self.register:
                await user.save_user()
            else:
                await user.validate_user()

            token = await Session(self.db).set_session(user.email)
            self.finish({'token': token})
        except DaoException as err:
            raise HTTPError(
                status_code=401 if isinstance(err, SessionException) else 400,
                reason=err.message
            )

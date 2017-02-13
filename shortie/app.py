from motor.motor_tornado import MotorClient

from tornado.ioloop import IOLoop
from tornado.web import Application

from .handlers import AuthHandler

from .handlers import InfoHandler
from .handlers import ShortenHandler

from .settings import settings


class ShortieApp(Application):

    COLLECTIONS = ('users', 'shorties', 'counters', 'sessions')

    def __init__(self):
        db = MotorClient(settings.MONGO_URL)[settings.DATABASE]
        app_settings = {
            'debug': settings.DEBUG,
            'db': db
        }

        handlers = [
            (r'/api/auth', AuthHandler),
            (r'/api/info', InfoHandler),
            (r'/api/register', AuthHandler, {'register': True}),
            (r'/api/shortie/?(?P<shortie>[a-zA-Z0-9]+)?', ShortenHandler)
        ]
        IOLoop.current().add_callback(self.init_database, db)
        super().__init__(handlers, **app_settings)

    async def init_database(self, db):
        collection_indexes = {
            'users': {
                'keys': 'email',
                'options': {
                    'unique': True
                }
            },
            'sessions': {
                'keys': 'created_at',
                'options': {
                    'expireAfterSeconds': settings.SESSION_LENGTH
                }
            }
        }
        for coll, opts in collection_indexes.items():
            await db[coll].create_index(
                opts['keys'], background=True, **opts['options']
            )

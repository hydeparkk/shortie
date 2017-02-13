from motor.motor_tornado import MotorClient

from tornado.ioloop import IOLoop
from tornado.testing import AsyncTestCase, AsyncHTTPTestCase

from shortie.settings import settings


class ShortieTestCommon(AsyncTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = MotorClient(settings.MONGO_URL)
        cls.db = cls.client[settings.DATABASE]

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        super().tearDownClass()

    def get_new_ioloop(self):
        return IOLoop.current()


class DaoTestBase(ShortieTestCommon):
    pass


class HandlersTestBase(AsyncHTTPTestCase, ShortieTestCommon):
    pass

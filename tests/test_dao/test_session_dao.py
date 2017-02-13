from tornado.gen import sleep
from tornado.testing import gen_test

from tests.shortie_tests_common import DaoTestBase

from shortie.dao import DaoException, Session


class TestSessionDao(DaoTestBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.sess_dao = Session(cls.db)

        async def create_index(db, collection):
            await db[collection].create_index(
                'created_at', expireAfterSeconds=3
            )

        cls.get_new_ioloop(cls).add_callback(
            create_index, cls.db, cls.sess_dao.COLLECTION_NAME
        )

    def setUp(self):
        super().setUp()

        async def clear_colection(db, collection):
            await db[collection].delete_many({})

        self.io_loop.add_callback(
            clear_colection, self.db, self.sess_dao.COLLECTION_NAME
        )

    @gen_test
    async def test_set_session(self):
        res = await self.sess_dao.set_session('tst@tst.com')

        self.assertEqual(len(res.split('.')), 3)

    @gen_test
    async def test_incorrect_token(self):
        with self.assertRaises(DaoException):
            await self.sess_dao.get_session('incorrect_token')

    @gen_test
    async def test_get_session(self):
        email = 'tst@tst.com'
        res = await self.sess_dao.set_session(email)
        self.assertIsNotNone(res)

        payload = await self.sess_dao.get_session(res)

        self.assertEqual(payload, email)

    @gen_test
    async def test_set_session_twice(self):
        session = await self.sess_dao.set_session('tst@tst.com')

        await sleep(1)

        session_two = await self.sess_dao.set_session('tst@tst.com')

        self.assertEqual(session, session_two)

    # MongoDB cleans ttl indexes every 60 seconds
    @gen_test(timeout=65)
    async def test_session_expired(self):
        email = 'tst@tst.com'
        res = await self.sess_dao.set_session(email)
        self.assertIsNotNone(res)

        await sleep(60)

        with self.assertRaises(DaoException):
            await self.sess_dao.get_session(res)

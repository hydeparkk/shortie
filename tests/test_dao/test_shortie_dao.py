from hashids import Hashids

from tornado.testing import gen_test

from tests.shortie_tests_common import DaoTestBase

from shortie.dao import DaoException, Shortie
from shortie.settings import settings


class TestShortieDao(DaoTestBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.shortie_dao = Shortie(cls.db)

    def setUp(self):
        super().setUp()

        async def clear_colection(db, collection):
            await db[collection].delete_many({})

        self.io_loop.add_callback(
            clear_colection, self.db, self.shortie_dao.COLLECTION_NAME
        )

    @gen_test
    async def test_add_shortie(self):
        res = await self.shortie_dao.save('http://exapmle.com')
        hasher = Hashids(salt=settings.SHORTIE_SECRET, min_length=5)

        counter = await self.db[
            self.shortie_dao.COUNTERS_COLLECTION_NAME].find_one(
            {'_id': 'shortie'}, projection={'seq': True}
        )
        hash_for_one = hasher.encode(counter.get('seq'))

        self.assertEqual(hash_for_one, res)

    @gen_test
    async def test_add_named_shortie(self):
        res = await self.shortie_dao.save('http://example.com', name='test')

        self.assertEqual(res, 'test')

    @gen_test
    async def test_add_named_shortie_again(self):
        await self.shortie_dao.save('http://example.com', name='test')

        with self.assertRaises(DaoException):
            await self.shortie_dao.save('http://test.com', name='test')

    @gen_test
    async def test_add_named_shortie_with_unproper_name(self):
        with self.assertRaises(DaoException):
            await self.shortie_dao.save('http://test.com', name='test!')

    @gen_test
    async def test_add_named_shortie_with_empty_name(self):
        res = await self.shortie_dao.save('http://test.com', name='')
        hasher = Hashids(salt=settings.SHORTIE_SECRET, min_length=5)
        hash_for_one = hasher.encode(1)

        self.assertEqual(hash_for_one, res)

    @gen_test
    async def test_add_the_same_url_twice(self):
        res = await self.shortie_dao.save('http://exapmle.com')
        res2 = await self.shortie_dao.save('http://exapmle.com')

        self.assertEqual(res, res2)

    @gen_test
    async def test_add_user_to_existing_shortie(self):
        await self.shortie_dao.save('http://exapmle.com')

        await self.shortie_dao.save('http://exapmle.com', user_id='tst@t.com')

        user_shorties = await self.shortie_dao.get_user_shorties('tst@t.com')

        self.assertEqual(len(user_shorties), 1)

    @gen_test
    async def test_get_user_shorties(self):
        await self.shortie_dao.save('http://exapmle.com', user_id='tst@t.com')
        await self.shortie_dao.save('http://google.co.uk')
        await self.shortie_dao.save('http://google.com', user_id='tst@t.com')

        self.assertEqual(
            {
                rec['url']
                for rec in await self.shortie_dao.get_user_shorties(
                    'tst@t.com'
                )
            },
            {'http://exapmle.com', 'http://google.com'}
        )

    @gen_test
    async def test_gen_notexisting_shortie(self):
        res = await self.shortie_dao.get('demo')

        self.assertIsNone(res)

    @gen_test
    async def test_get_url_appends_clicks(self):
        shortie = await self.shortie_dao.save('http://google.co.uk')

        for _ in range(5):
            await self.shortie_dao.get_url(shortie)

        shortie_info = await self.shortie_dao.get(shortie)

        self.assertEqual(len(shortie_info.get('clicks')), 5)

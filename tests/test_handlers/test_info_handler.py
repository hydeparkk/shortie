import json

from datetime import datetime

from tornado.httpclient import HTTPError
from tornado.testing import gen_test
from tornado.web import Application

from shortie.handlers import InfoHandler

from tests.shortie_tests_common import HandlersTestBase


class TestInfoHandler(HandlersTestBase):

    def get_app(self):
        return Application(
            [(r'/api/info', InfoHandler)],
            db=self.db
        )

    @gen_test
    async def test_request_without_params(self):
        with self.assertRaises(HTTPError):
            await self.http_client.fetch(
                self.get_url('/api/info'),
                method='GET',
                callback=self.stop
            )
            self.wait()

    @gen_test
    async def test_info_for_nonexisting_user(self):
        with self.assertRaises(HTTPError):
            await self.http_client.fetch(
                self.get_url('/api/info?email=tst@tst.com'),
                method='GET',
                callback=self.stop
            )
            self.wait()

    @gen_test
    async def test_info_for_nonexisting_shortie(self):
        with self.assertRaises(HTTPError):
            await self.http_client.fetch(
                self.get_url('/api/info?shortie=test123'),
                method='GET',
                callback=self.stop
            )
            self.wait()

    @gen_test
    async def test_get_user_shorties(self):
        await self.db.shorties.insert_many([
            {
                'long_url': 'http://tst.com',
                'shortie': 'eGWVm',
                'users': [
                    'tester@test.com'
                ],
                'clicks': [],
                'created_at': datetime.utcnow()
            },
            {
                'long_url': 'http://tst.com/one',
                'shortie': 'hello',
                'users': [],
                'clicks': [],
                'created_at': datetime.utcnow()
            },
            {
                'long_url': 'http://tst.com/two',
                'shortie': 'cwksL',
                'users': [
                    'tester@test.com'
                ],
                'clicks': [],
                'created_at': datetime.utcnow()
            }
        ])

        await self.http_client.fetch(
            self.get_url('/api/info?email=tester@test.com'),
            method='GET',
            callback=self.stop
        )
        res = self.wait()

        self.assertEqual(res.code, 200)

        res_body = json.loads(res.body)

        self.assertEqual(len(res_body.get('shorties')), 2)

    @gen_test
    async def test_get_shortie_info(self):
        await self.db.shorties.insert_one(
            {
                'long_url': 'http://tst.com/one',
                'shortie': 'newOne',
                'users': [],
                'clicks': [
                    datetime.utcnow()
                ],
                'created_at': datetime.utcnow()
            }
        )

        await self.http_client.fetch(
            self.get_url('/api/info?shortie=newOne'),
            method='GET',
            callback=self.stop
        )
        res = self.wait()

        self.assertEqual(res.code, 200)

        res_body = json.loads(res.body)

        self.assertEqual(res_body.get('long_url'), 'http://tst.com/one')

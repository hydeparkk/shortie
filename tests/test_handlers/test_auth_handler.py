import json

from tornado.httpclient import HTTPError
from tornado.testing import gen_test
from tornado.web import Application

from shortie.handlers import AuthHandler

from tests.shortie_tests_common import HandlersTestBase


class TestAuthHandler(HandlersTestBase):

    def get_app(self):
        return Application(
            [
                (r'/api/auth', AuthHandler),
                (r'/api/register', AuthHandler, {'register': True})
            ],
            db=self.db
        )

    @gen_test
    async def test_register_success(self):
        await self.http_client.fetch(
            self.get_url('/api/register'),
            method='POST',
            body=json.dumps({'email': 'test@t.com', 'password': 'test'}),
            callback=self.stop
        )
        res = self.wait()

        self.assertEqual(res.code, 200)

        res_body = json.loads(res.body)

        self.assertIn('token', res_body)

    @gen_test
    async def test_register_failed(self):
        with self.assertRaises(HTTPError):
            await self.http_client.fetch(
                self.get_url('/api/register'),
                method='POST',
                body=json.dumps({'password': 'test'}),
                callback=self.stop
            )
            self.wait()

    @gen_test
    async def test_get_auth_token_failed(self):
        with self.assertRaises(HTTPError):
            await self.http_client.fetch(
                self.get_url('/api/auth'),
                method='POST',
                body=json.dumps({'password': 'test'}),
                callback=self.stop
            )
            self.wait()

    @gen_test
    async def test_get_auth_token(self):
        await self.http_client.fetch(
            self.get_url('/api/register'),
            method='POST',
            body=json.dumps({'email': 'test@t2.com', 'password': 'test'}),
            callback=self.stop
        )
        self.wait()

        await self.http_client.fetch(
            self.get_url('/api/auth'),
            method='POST',
            body=json.dumps({'email': 'test@t2.com', 'password': 'test'}),
            callback=self.stop
        )
        res = self.wait()

        self.assertEqual(res.code, 200)

        res_body = json.loads(res.body)

        self.assertIn('token', res_body)

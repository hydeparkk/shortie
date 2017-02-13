import json
from urllib.parse import urlparse

from tornado.httpclient import HTTPError
from tornado.testing import gen_test
from tornado.web import Application

from shortie.handlers import ShortenHandler

from tests.shortie_tests_common import HandlersTestBase


class TestShortieHandler(HandlersTestBase):

    def get_app(self):
        return Application(
            [(r'/api/shortie/?(?P<shortie>[a-zA-Z0-9]+)?', ShortenHandler)],
            db=self.db
        )

    @gen_test
    async def test_post_shortie(self):
        await self.http_client.fetch(
            self.get_url('/api/shortie'),
            method='POST',
            body=json.dumps({'url': 'http://example.com'}),
            callback=self.stop
        )
        res = self.wait()

        self.assertEqual(res.code, 200)

        res_body = json.loads(res.body)

        self.assertIn('shortie', res_body)

    @gen_test
    async def test_post_with_incorect_auth_header(self):
        with self.assertRaises(HTTPError):
            await self.http_client.fetch(
                self.get_url('/api/shortie'),
                method='POST',
                body=json.dumps(
                    {'url': 'http://example.com', 'name': 'testOne'}),
                headers={'Authorization': 'NotCorrectToken'},
                callback=self.stop
            )
            self.wait()

    @gen_test
    async def test_post_named_shortie(self):
        await self.http_client.fetch(
            self.get_url('/api/shortie'),
            method='POST',
            body=json.dumps({'url': 'http://example.com', 'name': 'testOne'}),
            callback=self.stop
        )
        res = self.wait()

        res_body = json.loads(res.body)

        self.assertIn('shortie', res_body)
        self.assertEqual(res_body.get('shortie').split('/')[-1], 'testOne')

    @gen_test
    async def test_post_named_shortie_twice(self):
        await self.http_client.fetch(
            self.get_url('/api/shortie'),
            method='POST',
            body=json.dumps({'url': 'http://example.com', 'name': 'TestName'}),
            callback=self.stop
        )
        self.wait()

        with self.assertRaises(HTTPError):
            await self.http_client.fetch(
                self.get_url('/api/shortie'),
                method='POST',
                body=json.dumps(
                    {'url': 'http://example.com', 'name': 'TestName'}),
                callback=self.stop
            )
            self.wait()

    @gen_test
    async def test_post_with_empty_body(self):
        with self.assertRaises(HTTPError):
            await self.http_client.fetch(
                self.get_url('/api/shortie'),
                method='POST',
                body=json.dumps({}),
                callback=self.stop
            )
            self.wait()

    @gen_test
    async def test_get_not_existing_shortie(self):
        with self.assertRaises(HTTPError):
            await self.http_client.fetch(
                self.get_url('/api/shortie/notExists'),
                method='GET',
                callback=self.stop
            )
            self.wait()

    @gen_test
    async def test_get_shortie(self):
        await self.http_client.fetch(
            self.get_url('/api/shortie'),
            method='POST',
            body=json.dumps({'url': 'http://example.com'}),
            callback=self.stop
        )
        res = self.wait()

        self.assertEqual(res.code, 200)

        res_body = json.loads(res.body)

        await self.http_client.fetch(
            self.get_url(urlparse(res_body.get('shortie')).path),
            method='GET',
            callback=self.stop
        )
        res = self.wait()

        res_body = json.loads(res.body)
        self.assertEqual(res_body.get('url'), 'http://example.com')

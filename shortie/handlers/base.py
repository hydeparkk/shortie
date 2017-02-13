import json

from tornado.web import RequestHandler


class BaseHandler(RequestHandler):

    def prepare(self):
        self.set_header('Content-Type', 'application/json')

    def write_error(self, status_code, **kwargs):
        self.finish(json.dumps({
            'error': {
                'code': status_code,
                'message': self._reason
            }
        }))

    @property
    def db(self):
        return self.settings['db']

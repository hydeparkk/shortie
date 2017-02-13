import logging
import signal
import time

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line

from shortie.app import ShortieApp


SECONDS_WAIT_BEFORE_SHUTDOWN = 5

define('host', default='0.0.0.0', type=str, help='Run on the given host.')
define('port', default=8000, type=int, help='Run on the given port.')


def main():

    parse_command_line()

    http_server = HTTPServer(ShortieApp())
    http_server.listen(port=options.port, address=options.host)

    # if True:
    #     autoreload.start()
    #     for f in Path('.').glob('**/*.py'):
    #         autoreload.watch(f.absolute())
    #     # for folder, _, files in os.walk(os.path.abspath(__file__)):
    #     #     for f in files:
    #     #         autoreload.watch(os.path.join(folder, f))

    def sig_handler(sig, frame):
        IOLoop.current().add_callback(shutdown)

    def shutdown():
        logging.info('Stopping http server.')
        http_server.stop()

        io_loop = IOLoop.current()

        deadline = time.time() + SECONDS_WAIT_BEFORE_SHUTDOWN

        def stop_loop():
            now = time.time()

            if now < deadline and (io_loop._callbacks or io_loop._timeouts):
                io_loop.add_timeout(now + 1, stop_loop)
            else:
                io_loop.stop()
                logging.info('Shutdown.')

        stop_loop()

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    IOLoop.current().start()


if __name__ == '__main__':
    main()

# Python imports
import logging

# Tornado imports
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
from tornado.web import url

# App imports
import models
import handlers

# Options
define("port", default=8000, help="run on the given port", type=int)
define("debug", default=False, type=bool)
define("db_path", default='sqlite:///sqlite3.db', type=str)


class Application(tornado.web.Application):

    def __init__(self, options):
        urls = [
            url(r'/clients/(\d+)?', handlers.ClientHandler, name='clients'),
            url(r'/rooms/(\d+)?', handlers.RoomHandler, name='rooms'),
        ]
        settings = {
            'debug': options.debug
        }
        tornado.web.Application.__init__(self, urls, **settings)
        self.db = models.create_session(options.db_path, options.debug)


def main():
    logging.basicConfig(level=logging.DEBUG if options.debug else logging.INFO)
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application(options))
    logging.info('Start listening on {0} port'.format(options.port))
    try:
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()
    finally:
        http_server.stop()
        tornado.ioloop.IOLoop.instance().stop()

if __name__ == '__main__':
    main()

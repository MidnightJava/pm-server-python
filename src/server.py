import os
import sys
import json
from bson import json_util
from argparse import ArgumentParser
import signal
import tornado.web
import logging
import pymongo
from pymongo import MongoClient

logging.basicConfig(filename='log/server.log', level = logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger('asyncio').setLevel(logging.WARNING)
log = logging.getLogger('HandlerLogger')

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Allow-Methods', 'GET PUT POST DELETE')
        self.set_header('Access-Control-Allow-Origin', '*')

    def options(self):
       self.set_status(204)
       self.finish()

class GetMembersHandler(BaseHandler):
    def get(self):
        scope = self.get_argument('scope')
        if scope == 'all':
            log.debug('Get All Members')
        elif scope == 'active':
            log.debug('Get Active Members')
        else:
            err_msg = 'Invalid scope parameter: %s' % scope
            log.error(err_msg)
            self.set_status(400)
            self.write(err_msg)
            return
        client = self.application.mongo
        query = {}
        if scope == 'active':
            query = {"$or" : [
                {"status": "COMMUNING"},
                {"status": "NONCOMMUNING"}
            ]}
        data = client.PeriMeleon['Members'].find(query)
        data = list(data)
        log.info('%d records found' % len(data))
        self.set_status(200)
        self.write(json.dumps(data, default=json_util.default))


class FileHandler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.enmdswith('/'):
            url_path+= 'index.html'
        return url_path

    def get(self):
        #Serve app here when available
        self.render('./index.html')


class PMServer(tornado.web.Application):
    is_closing = False

    def __init__(self, handlers, **settings):
        print(settings)
        self.mongo = MongoClient(host=settings['host'], port=settings['port'])
        super(PMServer, self).__init__(handlers, **settings)

    def signal_handler(self, signum, frame):
        log.info('Exiting...')
        self.is_closing = True

    def try_exit(self):
        if self.is_closing:
            tornado.ioloop.IOLoop.instance().stop()
            log.info('Server exited')

def mk_app(prefix=''):
    if prefix:
        path= '/' + prefix + '/(.)'
    else:
        path = '/(.)'
    handlers = [
        (path, FileHandler, {"path": os.getcwd()}),
        (r"/api/getMembers", GetMembersHandler)
    ]
    settings = dict(debug=True, host='db', port=27017)
    application = PMServer(handlers, **settings)
    return application

def start_server(prefix='', port=8000):
    app = mk_app(prefix)
    signal.signal(signal.SIGINT, app.signal_handler)
    app.listen(port)
    log.info('Server listening on port %d' % port)
    tornado.ioloop.PeriodicCallback(app.try_exit, 100).start()
    tornado.ioloop.IOLoop.instance().start()

def parse_args(args=None):
    parser = ArgumentParser(description="...")
    parser.add_argument('-p', '--port', type=int, default=8000, help='The port on which the server will listen')
    #The following two args are for serving a client application or other file
    parser.add_argument('-f', '--prefix', type=str, default="", help="A prefix to add to the location from which pages are served")
    parser.add_argument('-d', '--dir', default='.', help="Directory from which to serve files")
    return parser.parse_args()

def main(args=None):
    args = parse_args(args)
    os.chdir(args.dir)
    start_server(prefix=args.prefix, port=args.port)

if __name__ == '__main__':
    main(sys.argv)
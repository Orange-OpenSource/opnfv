#!/usr/bin/python3
import tornado.ioloop
import tornado.web
import sys
from foreman.foremanAPI import ForemanAPI
from foreman.host import Host


class UserDataHandler(tornado.web.RequestHandler):
    """
    User Data handler
    """
    def get(self):
        host = Host(foreman, getIP(self.request))
        ret = host.getUserData()
        print("===== Return user-data for {} ======".format(host.name))
        print(ret)
        self.write(ret)


class MetaDataHandler(tornado.web.RequestHandler):
    """
    Meta Data handler
    """
    def get(self, meta):
        host = Host(foreman, getIP(self.request))
        available_meta = {
            'name': host.name,
            'instance-id': host.name,
            'hostname': host.name,
            'local-hostname': host.name,
            }
        if meta in available_meta.keys():
            ret = available_meta[meta]
        elif meta == '':
            ret = "\n".join(available_meta)
        else:
            raise tornado.web.HTTPError(status_code=404, log_message='No such metadata')
        print("===== Return meta-data '{}' for {} ======".format(meta, host.name))
        print(ret)
        self.write(ret)


def getIP(request):
    return request.headers['X-Forwarded-For'] if 'X-Forwarded-For' in request.headers.keys() else request.remote_ip

application = tornado.web.Application([
    (r'.*/user-data', UserDataHandler),
    (r'.*/meta-data/(.*)', MetaDataHandler),
])

if __name__ == "__main__":
    if len(sys.argv) == 3:
        foreman_auth = (sys.argv[1], sys.argv[2])
        foreman = ForemanAPI(foreman_auth)
        application.listen(8888)
        tornado.ioloop.IOLoop.instance().start()
    else:
        print('Error: Usage\npython {} foreman_user foreman_password'.format(sys.argv[0]))

#!/usr/bin/python3
import tornado.ioloop
import tornado.web
import socket
import sys
from opensteak.conf import OpenSteakConfig
from opensteak.foreman import OpenSteakForeman
from opensteak.printer import OpenSteakPrinter


class UserDataHandler(tornado.web.RequestHandler):
    """
    User Data handler
    """
    def get(self):
        hostname = getName(getIP(self.request))
        host = foreman.hosts[hostname]
        hostgroupDefaultPwd = foreman.hostgroups[host['hostgroup_id']]
                              .getParam('password')
        domainDefaultPwd = foreman.domains[host['domain_id']]\
                           .getParam('password')
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
            raise tornado.web.HTTPError(status_code=404,
                                        log_message='No such metadata')
        print("===== Return meta-data '{}' for {} ======".format(meta,
                                                                 host.name))
        print(ret)
        self.write(ret)


def getIP(request):
    if 'X-Forwarded-For' in request.headers.keys():
        return request.headers['X-Forwarded-For']
    else:
        return request.remote_ip


def getNameFromSourceIP(ip):
    return socket.gethostbyaddr(ip)[0]


application = tornado.web.Application([
    (r'.*/user-data', UserDataHandler),
    (r'.*/meta-data/(.*)', MetaDataHandler),
])

if __name__ == "__main__":
    if len(sys.argv) == 4:
        foreman = OpenSteakForeman(login=sys.argv[1],
                                   password=sys.argv[2],
                                   ip=sys.argv[3])
        conf = OpenSteakConfig(config_file='config/infra-test.yaml')
        p = OpenSteakPrinter()
        application.listen(8888)
        tornado.ioloop.IOLoop.instance().start()
    else:
        print('Error: Usage\npython3 {} foreman_user \
              foreman_password foreman_IP'.format(sys.argv[0]))

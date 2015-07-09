#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# Authors:
# @author: David Blaisonneau <david.blaisonneau@orange.com>
# @author: Arnaud Morin <arnaud1.morin@orange.com>

import tornado.ioloop
import tornado.web
import socket
import sys
import argparse
from opensteak.conf import OpenSteakConfig
from opensteak.foreman import OpenSteakForeman
from opensteak.printer import OpenSteakPrinter


DEFAULT_PASSWORD = 'password'


class UserDataHandler(tornado.web.RequestHandler):
    """
    User Data handler
    """
    def get(self):
        """ Function get
        Return UserData script from the foreman API

        @return RETURN: user-data script
        """
        hostname = getNameFromSourceIP(getIP(self.request))
        host = foreman.hosts[hostname]
        # Get the hostgroup
        if host['hostgroup_id']:
            hg = foreman.hostgroups[host['hostgroup_id']]
        else:
            hg = None
        # get the domain
        domain = foreman.domains[host['domain_id']]
        ret = host.getUserData(hostgroup=hg,
                               domain=domain,
                               defaultPwd=DEFAULT_PASSWORD,
                               proxyHostname=conf['smart_proxies'])
        p.status(bool(ret), "user data sent to {}".format(hostname))
        self.write(ret)


class MetaDataHandler(tornado.web.RequestHandler):
    """
    Meta Data handler
    """
    def get(self, meta):
        """ Function get
        Return meta data parameters from the foreman API

        @return RETURN: meta data parameters
        """
        hostname = getNameFromSourceIP(getIP(self.request))
        host = foreman.hosts[hostname]
        available_meta = {
            'name': host['name'],
            'instance-id': host['name'],
            'hostname': host['name'],
            'local-hostname': host['name'],
            }
        if meta in available_meta.keys():
            ret = available_meta[meta]
        elif meta == '':
            ret = "\n".join(available_meta)
        else:
            raise tornado.web.HTTPError(status_code=404,
                                        log_message='No such metadata')
        p.status(bool(ret), "meta data {} sent to {}"
                            .format(meta, hostname))
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
    p = OpenSteakPrinter()

    #
    # Check for params
    #
    p.header("Check parameters")
    args = {}

    # Update args with values from CLI
    parser = argparse.ArgumentParser(description='This script will run a '
                                                 'metadata server connected '
                                                 'to a foreman server.',
                                     usage='%(prog)s [options]')
    parser.add_argument('-c', '--config',
                        help='YAML config file to use (default is '
                              'config/infra.yaml).',
                        default='config/infra.yaml')
    args.update(vars(parser.parse_args()))

    # Open config file
    conf = OpenSteakConfig(config_file=args["config"])

    a = {}
    a["admin"] = conf["foreman"]["admin"]
    a["password"] = conf["foreman"]["password"]
    a["ip"] = conf["foreman"]["ip"]
    # Update args with values from config file
    args.update(a)
    del a

    # p.list_id(args)

    foreman = OpenSteakForeman( login=args["admin"],
                                password=args["password"],
                                ip=args["ip"])

    p.header("Run server")
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

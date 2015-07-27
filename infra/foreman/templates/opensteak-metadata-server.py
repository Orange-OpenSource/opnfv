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
from foreman import Foreman

DEFAULT_USERNAME = '${admin}'
DEFAULT_PASSWORD = '${password}'
DEFAULT_IP = '${ip}'

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
                               domain=domain['name'],
                               tplFolder='/opt/metadata/templates/')
        p.status(bool(ret), "VM {0}: sent user data".format(hostname))
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
        p.status(bool(ret), "VM {0}: sent meta data '{1}' with value '{2}'"
                            .format(hostname, meta, ret))
        self.write(ret)

class OpenSteakPrinter:
    """ Just a nice message printer """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    TABSIZE = 4

    def header(self, msg):
        """ Function header
        Print a header for a block

        @param msg: The message to print in the header (limited to 78 chars)
        @return RETURN: None
        """
        print("""
#
# {}
#
""".format(msg[0:78]))

    def config(self, msg, name, value=None, indent=0):
        """ Function config
        Print a line with the value of a parameter

        @param msg: The message to print in the header (limited to 78 chars)
        @param name: The name of the prameter
        @param value: The value of the parameter
        @param indent: Tab size at the beginning of the line
        @return RETURN: None
        """
        ind = ' ' * indent * self.TABSIZE
        if value is None:
            print('{} - {} = {}'.format(ind, msg, name))
        elif value is False:
            print('{} [{}KO{}] {} > {} (NOT found)'.
                  format(ind, self.FAIL, self.ENDC, msg, name))
        else:
            print('{} [{}OK{}] {} > {} = {}'.
                  format(ind, self.OKGREEN, self.ENDC, msg, name, str(value)))

    def list(self, msg, indent=0):
        """ Function list
        Print a list item

        @param msg: The message to print in the header (limited to 78 chars)
        @param indent: Tab size at the beginning of the line
        @return RETURN: None
        """
        print(' ' * indent * self.TABSIZE, '-', msg)

    def list_id(self, dic, indent=0):
        """ Function list_id
        Print a list of dict items

        @param dic: The dict to print
        @param indent: Tab size at the beginning of the line
        @return RETURN: None
        """
        for (k, v) in dic.items():
            self.list("{}: {}".format(k, v), indent=indent)

    def status(self, res, msg, failed="", eol="\n", quit=True, indent=0):
        """ Function status
        Print status message
        - OK/KO if the result is a boolean
        - Else the result text

        @param res: The status to show
        @param msg: The message to show
        @param eol: End of line
        @param quit: Exit the system in case of failure
        @param indent: Tab size at the beginning of the line
        @return RETURN: None
        """
        ind = ' ' * indent * self.TABSIZE
        if res is True:
            msg = '{} [{}OK{}] {}'.format(ind, self.OKGREEN, self.ENDC, msg)
        elif res:
            msg = '{} [{}{}{}] {}'.format(ind, self.OKBLUE, res,
                                          self.ENDC, msg)
        else:
            msg = '{} [{}KO{}] {}'.format(ind, self.FAIL, self.ENDC, msg)
            if failed:
                msg += '\n > {}'.format(failed)
        msg = msg.ljust(140) + eol
        sys.stdout.write(msg)
        if res is False and quit is True:
            sys.exit(0)

    def ask_validation(self, prompt=None, resp=False):
        """ Function ask_validation
        Ask a validation message

        @param prompt: The question to ask ('Continue ?') if None
        @param resp: The default value (Default is False)
        @return RETURN: Trie or False
        """
        if prompt is None:
            prompt = 'Continue ?'
        if resp:
            prompt += ' [{}Y{}/n]: '.format(self.BOLD, self.ENDC)
        else:
            prompt += ' [y/{}N{}]: '.format(self.BOLD, self.ENDC)
        while True:
            ans = input(prompt)
            if not ans:
                ans = 'y' if resp else 'n'
            if ans not in ['y', 'Y', 'n', 'N']:
                print('please enter y or n.')
                continue
            if ans == 'y' or ans == 'Y':
                return True
            if ans == 'n' or ans == 'N':
                sys.exit(0)


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
    parser.add_argument('-a', '--admin',
                        help='Username to connect to foreman (default is '
                              '{0}).'.format(DEFAULT_USERNAME),
                        default=DEFAULT_USERNAME)
    parser.add_argument('-p', '--password',
                        help='Password to connect to foreman (default is '
                              '{0}).'.format(DEFAULT_PASSWORD),
                        default=DEFAULT_PASSWORD)
    parser.add_argument('-i', '--ip',
                        help='IP address of foreman (default is '
                              '{0}).'.format(DEFAULT_IP),
                        default=DEFAULT_IP)
    args.update(vars(parser.parse_args()))

    # p.list_id(args)

    foreman = Foreman(  login=args["admin"],
                        password=args["password"],
                        ip=args["ip"])

    p.header("Run server")
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

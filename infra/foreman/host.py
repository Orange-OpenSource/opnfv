#!/usr/bin/python3
import socket
from string import Template
import base64
from foreman.foremanAPI import ForemanAPI
from foreman.hostgroup import HostGroup
from foreman.domain import Domain
import pprint

default_password = 'ubuntu'


class Host:
    """
    Host class
    """
    def __init__(self, api, ip, tplFolder = 'templates/'):
        self.ip = ip
        self.tplFolder = tplFolder
        self.name = socket.gethostbyaddr(self.ip)[0]
        self.api = api
        self.data = api.get('hosts', self.name)
        self.group = HostGroup(api, self.data['hostgroup_id'])
        self.domain = Domain(api ,self.data['domain_id'])
        if 'parameters' in self.data:
            self.params = {}
            for param in self.data['parameters']:
                self.params[param['name']] = param['value']
        else:
            self.params = []
        if 'password' in self.params:
            self.password = self.params['password']
        elif 'password' in self.group.params:
            self.password = self.group.params['password']
        else:
            self.password = default_password

    def __getattr__(self, name):
        return self.data[name]

    def getUserData(self):
        pprint.pprint(self.group.params)
        if 'user-data' in self.params:
            return self.params['user-data']
        else:
            class MyTemplate(Template):
                delimiter = '%'
                idpattern = r'[a-z][_a-z0-9]*'
            with open(self.tplFolder+'puppet.conf', 'rb') as puppet_file:
                content = puppet_file.read()
                enc_puppet_file = base64.b64encode(content)
            with open(self.tplFolder+'cloud-init.tpl', 'r') as content_file:
                tpl = content_file.read()
                s = MyTemplate(tpl)
                if 'global_sshkey' in self.group.params:
                    sshauthkeys = ' - '+self.group.params['global_sshkey']
                else:
                    sshauthkeys = ''
                self.userdata = s.substitute(
                    password = self.password,
                    fqdn = self.name,
                    sshauthkeys = sshauthkeys,
                    foremanurlbuilt = "http://foreman.{}/unattended/built".format(self.domain.name),
                    puppet_conf_content = enc_puppet_file.decode('utf-8'))
                return self.userdata


if __name__ == "__main__":
    import pprint
    import sys
    if len(sys.argv) == 4:
        foreman_auth = (sys.argv[1], sys.argv[2])
        foreman = ForemanAPI(foreman_auth, '192.168.1.4')
        print(foreman)
        host = Host(foreman, sys.argv[3])
        pprint.pprint(host.params)
        pprint.pprint(host.group.params)
        pprint.pprint(host.group.params)
        pprint.pprint(host.password)
        pprint.pprint(host.getUserData())
    else:
        print('Error: Usage\npython {} foreman_user foreman_password ip'.format(sys.argv[0]))

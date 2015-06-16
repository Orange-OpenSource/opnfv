#!/usr/bin/python3
from foreman.foremanAPI import ForemanAPI


class HostGroup:
    """
    HostGroup class
    """
    def __init__(self, api, id='0'):
        self.api = api
        if id is None:
            self.params = {}
        else:
            self.data = api.get('hostgroups', id)
            if 'parameters' in self.data:
                self.params = {}
                for param in self.data['parameters']:
                    self.params[param['name']] = param['value']
            else:
                self.params = {}

    def __getattr__(self, name):
        return self.data[name]

if __name__ == "__main__":
    import pprint
    import sys
    if len(sys.argv) == 4:
        foreman_auth = (sys.argv[1], sys.argv[2])
        foreman = ForemanAPI(foreman_auth, '192.168.1.4')
        group = HostGroup(foreman, sys.argv[3])
        pprint.pprint(group.params)
    else:
        print('Error: Usage\npython {} foreman_user foreman_password hostgroup_id'.format(sys.argv[0]))

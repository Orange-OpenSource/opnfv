#!/usr/bin/python3
from foreman.foremanAPI import ForemanAPI


class Domain:
    """
    Domain class
    """
    def __init__(self, api, id = None):
        self.foreman = api
        if id:
            self.load(id=id)

    def load(self, id='0', name=''):
        if name:
            id = self.__getIdByName__(name)
        self.data = self.foreman.get('domains', id)
        if 'parameters' in self.data:
            self.params = self.data['parameters']
        else:
            self.params = []
        self.name = self.data['name']

    def __getIdByName__(self, name):
        ret = self.foreman.list('domains', filter='name = '+name, only_id=True)
        if ret[name]:
            return ret[name]
        else:
            return None

if __name__ == "__main__":
    import pprint
    import sys
    if len(sys.argv) == 4:
        foreman_auth = (sys.argv[1], sys.argv[2])
        foreman = ForemanAPI(foreman_auth, '192.168.1.4')
        domain = Domain(foreman, sys.argv[3])
        pprint.pprint(domain.params)
        pprint.pprint(domain.name)
    else:
        print('Error: Usage\npython {} foreman_user foreman_password domain_id'.format(sys.argv[0]))

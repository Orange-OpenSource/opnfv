#!/usr/bin/python3
from foreman.foremanAPI import ForemanAPI


class Domain:
    """
    Domain class
    """
    def __init__(self, api, id='0'):
        self.api = api
        self.data = api.get('domains', id)
        if 'parameters' in self.data:
            self.params = self.data['parameters']
        else:
            self.params = []
        self.name = self.data['name']


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

#!/usr/bin/python3
from pprint import pprint as pp
from foreman.foremanAPI import ForemanAPI
from opensteak.conf import OpenSteakConfig
from opensteak.printer import OpenSteakPrinter

import sys
foreman_auth = (sys.argv[1], sys.argv[2])
foreman = ForemanAPI(foreman_auth, '192.168.1.4')
conf = OpenSteakConfig(config_file='config.yaml')
p = OpenSteakPrinter()

print("== List hosts ID ==")
pp(foreman.get('hosts', sys.argv[3], 'status')['status'])

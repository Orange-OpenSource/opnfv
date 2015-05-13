#!/usr/bin/python3
from pprint import pprint as pp
from foreman.foremanAPI import ForemanAPI
import json
import sys

foreman_auth = (sys.argv[1], sys.argv[2])
foreman = ForemanAPI(foreman_auth, '192.168.1.4')
payload = {
    "power_action": "start",
    "host": {},
}
res = foreman.set('hosts',sys.argv[3],'power',payload)
print(res)

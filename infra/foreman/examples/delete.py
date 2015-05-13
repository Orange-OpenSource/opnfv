#!/usr/bin/python3
from pprint import pprint as pp
from foreman.foremanAPI import ForemanAPI
import json
import sys
import os

foreman_auth = (sys.argv[1], sys.argv[2])
foreman = ForemanAPI(foreman_auth, '192.168.1.4')
foreman.delete('hosts',sys.argv[3])
os.system("./delete_dns.sh %s"%sys.argv[3])

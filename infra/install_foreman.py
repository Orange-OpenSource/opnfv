#!/usr/bin/python3
from pprint import pprint as pp
from foreman.foremanAPI import ForemanAPI
from opensteak.conf import OpenSteakConfig
from opensteak.printer import OpenSteakPrinter
import json
import time
import sys


#~
#~ Check for params
#~
if len(sys.argv) != 3:
    print('Error: Usage\npython3 {} foreman_user foreman_password'.format(sys.argv[0]))
    exit(1)

#~
#~ Prepare classes
#~
foreman_auth = (sys.argv[1], sys.argv[2])
foreman = ForemanAPI(foreman_auth, '192.168.1.4')
conf = OpenSteakConfig(config_file='config/infra.yaml')
p = OpenSteakPrinter()


print("== List hosts ID ==")
pp(foreman.list('hosts', only_id=True))
print("== List compute resources ID ==")
pp(foreman.list('compute_resources', only_id=True))
print("== List compute resources ID ==")
pp(foreman.list('operatingsystems', only_id=True))
print("== List images for OS 2 ==")
pp(foreman.list('operatingsystems/2/images', only_id=True))

#~ name = "mysql2."+domainName
#~ if name not in foreman.list('hosts', only_id=True):
    #~ payload = {'host': {
                #~ "name": name
                #~ "environment_id": "334344675",
                #~ "domain_id": "22495316",
                #~ "ip": "10.0.0.20",
                #~ "mac": "52:53:00:1e:85:93",
                #~ "ptable_id": "980190962",
                #~ "medium_id": "980190962",
                #~ "architecture_id": "501905019",
                #~ "operatingsystem_id": "1073012828",
                #~ "puppet_proxy_id": "980190962",
                #~ "compute_resource_id": "980190962",
                #~ "root_pass": "xybxa6JUkz63w",
                #~ "location_id": "255093256",
                #~ "organization_id": "447626438"
                #~ }}
    #~ foreman.create('domains', payload)
#~ domains = foreman.list('domains', only_id=True)
#~ status(domainName in domains, 'Domain '+domainName, "Error when creating domain "+domainName)

#~
#~ To be completed for a full install
#~

# #~ Check or create domain
# if domainName not in foreman.list('domains', only_id=True):
#     payload = {'domain': {"name": domainName}}
#     foreman.create('domains', payload)
# domains = foreman.list('domains', only_id=True)
# status(domainName in domains, 'Domain '+domainName, "Error when creating domain "+domainName)
#
# #~ Check or create main group
# if domainName not in foreman.list('hostgroups', only_id=True):
#     payload = {'hostgroup': {"name": domainName}}
#     foreman.create('hostgroups', payload)
# groups = foreman.list('hostgroups', only_id=True)
# status(domainName in groups, 'Hostgroup '+domainName, "Error when creating hostgroup "+domainName)

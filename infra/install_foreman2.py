#!/usr/bin/python3
"""
Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Authors:
@author: David Blaisonneau <david.blaisonneau@orange.com>
@author: Arnaud Morin <arnaud1.morin@orange.com>
"""

from opensteak.conf import OpenSteakConfig
from opensteak.foreman import OpenSteakForeman
from opensteak.printer import OpenSteakPrinter
import sys


#
# Check for params
#
if len(sys.argv) != 4:
    print('Error: Usage\npython3 {} foreman_user \
          foreman_password foreman_ip'.format(sys.argv[0]))
    exit(1)

#
# Prepare classes
#
foreman = OpenSteakForeman(login=sys.argv[1],
                           password=sys.argv[2], ip=sys.argv[3])
conf = OpenSteakConfig(config_file='config/infra-test.yaml')
p = OpenSteakPrinter()

##############################################
p.header("Check smart proxy")
##############################################

smartProxy = conf['smart_proxies']
smartProxyId = foreman.smartProxies[smartProxy]['id']
p.status(bool(smartProxyId), 'Check smart proxy ' + smartProxy + ' exists')

##############################################
p.header("Get puppt classes")
##############################################

# Reload the smart proxy to get the latest puppet classes

# p.status(bool(foreman.smartProxies.importPuppetClasses(smartProxyId)),
#                'Import puppet classes from proxy '+smartProxy)

# Get the list of puppet classes ids
puppetClassesId = {}
puppetClassesId['hostgroupTop'] = {}
for pclass in conf['hostgroupTop']['classes']:
        puppetClassesId['hostgroupTop'][pclass] =\
            foreman.puppetClasses[pclass]['id']
        p.status(bool(puppetClassesId['hostgroupTop'][pclass]),
                 'Puppet Class "{}"'.format(pclass))
for name in conf['hostgroups']:
    puppetClassesId[name] = {}
    for pclass in conf['hostgroups'][name]['classes']:
        puppetClassesId[name][pclass] = foreman.puppetClasses[pclass]['id']
        p.status(bool(puppetClassesId[name][pclass]),
                 'Puppet Class "{}"'.format(pclass))

##############################################
p.header("Check and create - OS")
##############################################

operatingSystems = conf['operatingsystems']
osIds = set()
for os, data in operatingSystems.items():
    osId = foreman.operatingSystems.checkAndCreate(os, {})
    p.status(bool(osId), 'Operating system ' + os)
    osIds.add(osId)

##############################################
p.header("Check and create - Architecture")
##############################################

architecture = conf['architectures']
architectureId = foreman.architectures.checkAndCreate(architecture, {}, osIds)
p.status(bool(architectureId), 'Architecture ' + architecture)

##############################################
p.header("Check and create - Domains")
##############################################

domain = conf['domains']
domainId = foreman.domains.checkAndCreate(domain, {})
p.status(bool(domainId), 'Domain ' + domain)

##############################################
p.header("Check and create - Subnets")
##############################################

confSubnets = conf['subnets']
for name, data in confSubnets.items():
    payload = data['data']
    if 'dhcp_id' not in data['data'].keys():
        payload['dhcp_id'] = smartProxyId
    if 'tftp_id' not in data['data'].keys():
        payload['tftp_id'] = smartProxyId
    if 'dns_id' not in data['data'].keys():
        payload['dns_id'] = smartProxyId
    subnetId = foreman.subnets.checkAndCreate(name, payload, domainId)
    p.status(bool(subnetId), 'Subnet ' + name)

##############################################
p.header("Check and create - Hostgroups")
##############################################

hg_parent = conf['hostgroupTop']['name']
payload = {"environment_name": conf['environments'],
           "subnet_name": conf['hostgroupTop']['subnet'],
           "domain_name": domain}
hg_parentId = foreman.hostgroups.checkAndCreate(hg_parent, payload,
                                                conf['hostgroupTop'],
                                                False,
                                                puppetClassesId['hostgroupTop'])
p.status(bool(hg_parentId), 'Hostgroup {}'.format(hg_parent))

for hg in conf['hostgroups'].keys():
    key = hg_parent + '_' + conf['hostgroups'][hg]['name']
    payload = {"title": hg_parent + '/' + conf['hostgroups'][hg]['name'],
               "parent_id": hg_parentId}
    p.status(bool(foreman.hostgroups.checkAndCreate(key, payload,
                                                    conf['hostgroups'][hg],
                                                    hg_parent,
                                                    puppetClassesId[hg])),
             'Sub Hostgroup {}'.format(conf['hostgroups'][hg]['name']))

sys.exit()
##############################################
p.header("Clean")
##############################################

# Delete Sub Hostgroups
for hg in conf['hostgroups'].keys():
    key = hg_parent + '_' + conf['hostgroups'][hg]['name']
    del(foreman.hostgroups[key])
    p.status(bool(key not in foreman.hostgroups),
             'Delete sub hostgroup {}'.format(conf['hostgroups'][hg]['name']))

# Delete Top hostgroup
hg_parent = conf['hostgroupTop']['name']
del(foreman.hostgroups[hg_parent])
p.status(bool(hg_parent not in foreman.hostgroups),
         'Delete top hostgroup {}'.format(hg_parent))

# Delete subnets or remove domain from its
for name, data in confSubnets.items():
    subnetId = foreman.subnets[name]['id']
    p.status(foreman.subnets.removeDomain(subnetId, domainId),
             'Remove domain {} from subnet {}'.format(domain, name))
    if not data['shared']:
        del(foreman.subnets[subnetId])
        p.status(name not in foreman.subnets, 'Delete subnet ' + name)

# Delete domain
del(foreman.domains[domainId])
p.status(domainId not in foreman.domains, 'Delete domain ' + domain)

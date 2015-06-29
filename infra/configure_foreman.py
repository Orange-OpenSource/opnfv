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

from opensteak.conf import OpenSteakConfig
from opensteak.foreman import OpenSteakForeman
from opensteak.printer import OpenSteakPrinter
import argparse
import sys
from pprint import pprint as pp


p = OpenSteakPrinter()

#
# Check for params
#
p.header("Check parameters")
args = {}

# Update args with values from CLI
parser = argparse.ArgumentParser(description='This script will configure'
                                             'foreman.',
                                 usage='%(prog)s [options]')
parser.add_argument('-c', '--config',
                    help='YAML config file to use (default is '
                          'config/infra.yaml).',
                    default='config/infra.yaml')
parser.add_argument('-d', '--disable_update',
                    help='Disable Puppet class update on foreman. This can '
                         'be used when the configuration has already '
                         'been done.',
                    default=False,
                    action='store_true')
args.update(vars(parser.parse_args()))

# Open config file
conf = OpenSteakConfig(config_file=args["config"])

a = {}
a["admin"] = conf["foreman"]["admin"]
a["password"] = conf["foreman"]["password"]
a["ip"] = conf["foreman"]["ip"]

# Update args with values from config file
args.update(a)
del a

# p.list_id(args)

#
# Prepare classes
#
foreman = OpenSteakForeman(login=args["admin"],
                           password=args["password"],
                           ip=args["ip"])

##############################################
p.header("Check smart proxy")
##############################################

smartProxy = conf['smart_proxies']
smartProxyId = foreman.smartProxies[smartProxy]['id']
p.status(bool(smartProxyId), 'Check smart proxy ' + smartProxy + ' exists')

##############################################
p.header("Check and create - Environment production")
##############################################

environment = conf['environments']
environmentId = foreman.environments.checkAndCreate(environment, {})
p.status(bool(environmentId), 'Environment ' + environment)

##############################################
p.header("Get puppet classes")
##############################################

# Reload the smart proxy to get the latest puppet classes
if not args["disable_update"]:
    p.status(bool(foreman.smartProxies.importPuppetClasses(smartProxyId)),
             'Import puppet classes from proxy '+smartProxy,
             '{}\n >> {}'.format(foreman.api.errorMsg, foreman.api.url))

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
puppetClassesId['foreman'] = {}
for pclass in conf['foreman']['classes']:
        puppetClassesId['foreman'][pclass] =\
            foreman.puppetClasses[pclass]['id']
        p.status(bool(puppetClassesId['foreman'][pclass]),
                 'Puppet Class "{}"'.format(pclass))

##############################################
p.header("Check and create - OS")
##############################################

operatingSystems = conf['operatingsystems']
osIds = set()
for os, data in operatingSystems.items():
    osId = foreman.operatingSystems.checkAndCreate(os, data)
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
hg_parentId = foreman.hostgroups.checkAndCreate(
    hg_parent,
    payload,
    conf['hostgroupTop'],
    False,
    puppetClassesId['hostgroupTop']
)
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


## ##############################################
## p.header("Authorize Foreman to do puppet runs")
## ##############################################
##
## foreman.settings['puppetrun']['value'] = 'true'
## p.status(foreman.settings['puppetrun']['value'],
##          'Set puppetrun parameter to True')
##
## ##############################################
## p.header("Configure Foreman host")
## ##############################################
##
## hostName = "foreman.{}".format(conf['domains'])
## foremanHost = foreman.hosts[hostName]
##
## # Add puppet classes to foreman
## p.status(foreman.hosts[hostName].checkAndCreateClasses(
##          puppetClassesId['foreman'].values()),
##          "Add puppet classes to foreman host")
##
## # Add smart class parameters of opensteak::dhcp to foreman
## className = 'opensteak::dhcp'
## scp = {x['parameter']: x['id'] for x in
##        foreman.puppetClasses[className]['smart_class_parameters']}
## for k, v in conf['foreman']['classes'][className].items():
##     if v is None:
##         if k == 'pools':
##             v = {'pools': dict()}
##             for subn in conf['subnets'].values():
##                 v['pools'][subn['domain']] = dict()
##                 v['pools'][subn['domain']]['network'] = subn['data']['network']
##                 v['pools'][subn['domain']]['netmask'] = subn['data']['mask']
##                 v['pools'][subn['domain']]['range'] =\
##                     subn['data']['from'] + ' ' + subn['data']['to']
##                 if 'gateway' in subn['data'].keys():
##                     v['pools'][subn['domain']]['gateway'] =\
##                         subn['data']['gateway']
##         elif k == 'dnsdomain':
##             v = list()
##             for subn in conf['subnets'].values():
##                 v.append(subn['domain'])
##                 revZone = subn['data']['network'].split('.')[::-1]
##                 while revZone[0] is '0':
##                     revZone=revZone[1::]
##                 v.append('.'.join(revZone) + '.in-addr.arpa')
##     scp_id = scp[k]
##     foreman.hosts[hostName][
##         'smart_class_parameters_dict'][
##         '{}::{}'.format(className, k)].setOverrideValue(v, hostName)
##
## foremanSCP = set([x['parameter']
##                  for x in foreman.hosts[hostName]
##                  ['smart_class_parameters_dict'].values()])
## awaitedSCP = set(conf['foreman']['classes'][className].keys())
## p.status(awaitedSCP.issubset(foremanSCP),
##          "Add smart class parameters to class {} on foreman host"
##          .format(className))
##
## # Run puppet on foreman
## p.status(bool(foreman.hosts[hostName].puppetRun()),
##          'Run puppet on foreman host')
##

## ##############################################
## p.header("Add controller nodes")
## ##############################################
##
## controllerName = 'controller1.infra.opensteak.fr'
## macAddress = '40:f2:e9:2a:4d:e3'
## pTableName = "Preseed default"
## mediaName = "Ubuntu mirror"
## osName = "Ubuntu 14.04.1 LTS"
## password = "opnfv123"
##
## domainId = foreman.domains[conf['domains']]['id']
## environmentId = foreman.environments[conf['environments']]['id']
## architectureId = foreman.architectures[conf['architectures']]['id']
## smartProxyId = foreman.smartProxies[conf['smart_proxies']]['id']
## payload = {
##   "host": {
##     "name": controllerName,
##     "environment_id": environmentId,
##     "mac": macAddress,
##     "domain_id": domainId,
##     "ptable_id": foreman.ptables[pTableName]['id'],
##     "medium_id": foreman.media[mediaName]['id'],
##     "architecture_id": architectureId,
##     "operatingsystem_id": foreman.operatingSystems[osName]['id'],
##     "puppet_proxy_id": smartProxyId,
##     "hostgroup_id": foreman.hostgroups[
##         conf['hostgroups']['hostgroupController']['name']]['id'],
##     "root_pass": password,
##   }
## }
## pp(payload)
## controllerId = foreman.hosts.createController(controllerName, payload)
## pp(foreman.api.url)
## pp(foreman.api.payload)
## pp(foreman.api.errorMsg)
##
##
## bmcIp = '192.168.1.199'
## payload = {
##             "ip": "192.168.1.199",
##             "type": "bmc",
##             "managed": False,
##             "identifier": "ipmi",
##             "username": "user",
##             "password": "B1ng0!",
##             "provider": "IPMI",
##             "virtual": False
##         }
## foreman.hosts[controllerId]['interfaces'] = payload
## pp(foreman.api.url)
## pp(foreman.api.payload)
## pp(foreman.api.errorMsg)

##############################################
p.header("Clean")
##############################################

## # Delete Sub Hostgroups
## for hg in conf['hostgroups'].keys():
##     key = hg_parent + '_' + conf['hostgroups'][hg]['name']
##     del(foreman.hostgroups[key])
##     p.status(bool(key not in foreman.hostgroups),
##              'Delete sub hostgroup {}'.format(conf['hostgroups'][hg]['name']))
##
## # Delete Top hostgroup
## hg_parent = conf['hostgroupTop']['name']
## del(foreman.hostgroups[hg_parent])
## p.status(bool(hg_parent not in foreman.hostgroups),
##          'Delete top hostgroup {}'.format(hg_parent))

## # Delete subnets or remove domain from its
## for name, data in confSubnets.items():
##     subnetId = foreman.subnets[name]['id']
##     p.status(foreman.subnets.removeDomain(subnetId, domainId),
##              'Remove domain {} from subnet {}'.format(domain, name))
##     if not data['shared']:
##         del(foreman.subnets[subnetId])
##         p.status(name not in foreman.subnets, 'Delete subnet ' + name)
##
## # Delete domain
## del(foreman.domains[domainId])
## p.status(domainId not in foreman.domains, 'Delete domain ' + domain)

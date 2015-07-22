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
for name in conf['hostgroupsList']:
    puppetClassesId[name] = {}
    for pclass in conf['hostgroupsList'][name]['classes']:
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
p.header("Check templates")
##############################################

tplList = []
for data in conf['operatingSystemsList'].values():
    if 'templates' in data.keys():
        tplList.extend(data['templates'])
tplList = set(tplList)
for tpl in tplList:
    p.status(tpl in foreman.configTemplates,
             'Template "{}" is present'.format(tpl))

# Overwrite some provisioning templates with files
for templateName, templateFile in conf['configTemplatesList'].items():
    # Overwrite only if template exists in foreman
    if templateName in foreman.configTemplates:
        with open(templateFile) as f:
            data = f.read()
            # Set
            foreman.configTemplates[templateName]['template'] = data
            # Check
            p.status(foreman.configTemplates[templateName]['template'] == data,
                     'Template "{}" is set'.format(templateName))

##############################################
p.header("Check and create - OS")
##############################################

operatingSystems = conf['operatingSystemsList']
osIds = set()
for os, data in operatingSystems.items():
    templates = media = ptables = []
    if 'templates' in data.keys():
        templates = data.pop('templates')
    if 'media' in data.keys():
        media = data.pop('media')
    if 'ptables' in data.keys():
        ptables = data.pop('ptables')
    osId = foreman.operatingSystems.checkAndCreate(os, data)
    p.status(bool(osId), 'Operating system ' + os)
    osIds.add(osId)
    # Set medias
    media_ids = list(map(lambda x: foreman.media[x]['id'], media))
    foreman.operatingSystems[os]['media'] = media_ids
    p.status(list(foreman.operatingSystems[os]['media'].keys()) == media,
             'Media for operating system ' + os)
    # Set ptables
    ptables_ids = list(map(lambda x: foreman.ptables[x]['id'], ptables))
    foreman.operatingSystems[os]['ptables'] = ptables_ids
    p.status(list(foreman.operatingSystems[os]
                  ['ptables'].keys()) == ptables,
             'PTables for operating system ' + os)
    # Set templates
    # - First check OS is added in the template
    for tpl in templates:
        p.status(foreman.configTemplates[tpl].checkOrAddOS(os, osId),
                 "OS {} is in template {}".format(os, tpl))
    for tpl in templates:
        p.status(foreman.operatingSystems[os].checkOrAddDefaultTemplate(
                 foreman.configTemplates[tpl]),
                 'Add template "{}" to Operating system {}'.format(tpl, os))

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

confSubnets = conf['subnetsList']
for name, data in confSubnets.items():
    payload = data['data']
    if 'dhcp_id' not in data['data'].keys():
        payload['dhcp_id'] = smartProxyId
    if 'tftp_id' not in data['data'].keys():
        payload['tftp_id'] = smartProxyId
    if 'dns_id' not in data['data'].keys():
        payload['dns_id'] = smartProxyId
    subnetId = foreman.subnets.checkAndCreate(name, payload, domainId)
    netmaskshort = sum([bin(int(x)).count('1')
                       for x in data['data']['mask'].split('.')])
    p.status(bool(subnetId),
             'Subnet {} ({}/{})'.format(name,
                                        data['data']['network'],
                                        netmaskshort))

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

for hg in conf['hostgroupsList'].keys():
    key = hg_parent + '_' + conf['hostgroupsList'][hg]['name']
    payload = {"title": hg_parent + '/' + conf['hostgroupsList'][hg]['name'],
               "parent_id": hg_parentId}
    # Get back SSH key from foreman/files/id_rsa.pub file
    if 'params' in conf['hostgroupsList'][hg] and 'global_sshkey' in conf['hostgroupsList'][hg]['params'] and conf['hostgroupsList'][hg]['params']['global_sshkey'] is None:
        with open("{0}/id_rsa.pub".format(conf['foreman']['filesFolder']), 'r') as content_file:
            conf['hostgroupsList'][hg]['params']['global_sshkey'] = content_file.read()
    p.status(bool(foreman.hostgroups.checkAndCreate(key, payload,
                                                    conf['hostgroupsList'][hg],
                                                    hg_parent,
                                                    puppetClassesId[hg])),
             'Sub Hostgroup {}'.format(conf['hostgroupsList'][hg]['name']))


##############################################
p.header("Authorize Foreman to do puppet runs")
##############################################

foreman.settings['puppetrun']['value'] = 'true'
p.status(foreman.settings['puppetrun']['value'],
         'Set puppetrun parameter to True')

##############################################
p.header("Configure Foreman host")
##############################################

hostName = "foreman.{}".format(conf['domains'])
foremanHost = foreman.hosts[hostName]

# Add puppet classes to foreman
p.status(foreman.hosts[hostName].checkAndCreateClasses(
         puppetClassesId['foreman'].values()),
         "Add puppet classes to foreman host")

# Add smart class parameters of opensteak::dhcp to foreman
className = 'opensteak::dhcp'
scp = foreman.puppetClasses[className].smartClassParametersList()
for k, v in conf['foreman']['classes'][className].items():
    if v is None:
        if k == 'pools':
            v = {'pools': dict()}
            for subn in conf['subnetsList'].values():
                v['pools'][subn['domain']] = dict()
                v['pools'][subn['domain']]['network'] = subn['data']['network']
                v['pools'][subn['domain']]['netmask'] = subn['data']['mask']
                v['pools'][subn['domain']]['range'] =\
                    subn['data']['from'] + ' ' + subn['data']['to']
                if 'gateway' in subn['data'].keys():
                    v['pools'][subn['domain']]['gateway'] =\
                        subn['data']['gateway']
        elif k == 'dnsdomain':
            v = list()
            for subn in conf['subnetsList'].values():
                v.append(subn['domain'])
                revZone = subn['data']['network'].split('.')[::-1]
                revMask = subn['data']['mask'].split('.')[::-1]
                while revMask[0] != '255':
                    revZone = revZone[1::]
                    revMask = revMask[1::]
                v.append('.'.join(revZone) + '.in-addr.arpa')
    scp_id = scp[k]
    foreman.smartClassParameters[scp_id].setOverrideValue(v, hostName)

foremanSCP = set([x['parameter']
                 for x in foreman.hosts[hostName]
                 ['smart_class_parameters'].values()])
awaitedSCP = set(conf['foreman']['classes'][className].keys())
p.status(awaitedSCP.issubset(foremanSCP),
         "Add smart class parameters to class {} on foreman host"
         .format(className))

# Run puppet on foreman
p.status(bool(foreman.hosts[hostName].puppetRun()),
         'Run puppet on foreman host')


##############################################
p.header("Add controller nodes")
##############################################

for c in conf['controllersList']:

    cConf = conf['controllersList'][c]
    hostName = cConf['controllerName']
    payload = {
        "host": {
            "name": hostName,
            "environment_id": foreman.environments[conf['environments']]['id'],
            "mac": cConf['macAddress'],
            "domain_id": foreman.domains[conf['domains']]['id'],
            "subnet_id": foreman.subnets[conf['subnets']]['id'],
            "ptable_id": foreman.ptables[conf['ptables']]['id'],
            "medium_id": foreman.media[conf['media']]['id'],
            "architecture_id": foreman.architectures[
                conf['architectures']]['id'],
            "operatingsystem_id": foreman.operatingSystems[
                cConf['operatingSystem']]['id'],
            "puppet_proxy_id": foreman.smartProxies[
                conf['smart_proxies']]['id'],
            "hostgroup_id": foreman.hostgroups['{}_{}'.format(
                conf['hostgroupTop']['name'],
                conf['hostgroupsList']['hostgroupController']['name'])]['id'],
            "root_pass": cConf['password']
            }
    }
    payloadBMC = {"ip": cConf['impiIpAddress'],
                  "mac": cConf['ipmiMacAddress'],
                  "type": "bmc",
                  "managed": False,
                  "identifier": "ipmi",
                  "username": cConf['impiUser'],
                  "password": cConf['impiPassword'],
                  "provider": "IPMI",
                  "virtual": False}
    controllerId = foreman.hosts.createController(hostName,
                                                  payload, payloadBMC)
    # Configure OVS - for opensteak::base-network
    ovs_config = cConf['params']['ovs_config']
    pClass = 'opensteak::base-network'
    scp = foreman.puppetClasses[pClass].smartClassParametersList()
    scp_id = scp['ovs_config']
    foreman.smartClassParameters[scp_id].setOverrideValue(ovs_config, hostName)
    # Configure OVS - for opensteak::libvirt
    pClass = 'opensteak::libvirt'
    scp = foreman.puppetClasses[pClass].smartClassParametersList()
    scp_id = scp['ovs_config']
    foreman.smartClassParameters[scp_id].setOverrideValue(ovs_config, hostName)

    # Add the controller to the list of computeRessources


##############################################
p.header("Clean")
##############################################

## # Delete Sub Hostgroups
## for hg in conf['hostgroupsList'].keys():
##     key = hg_parent + '_' + conf['hostgroupsList'][hg]['name']
##     del(foreman.hostgroups[key])
##     p.status(bool(key not in foreman.hostgroups),
##              'Delete sub hostgroup {}'.format(conf['hostgroupsList'][hg]['name']))
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

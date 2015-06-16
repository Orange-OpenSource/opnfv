#!/usr/bin/python3


from pprint import pprint as pp
from foreman.foremanAPI import ForemanAPI
from opensteak.conf import OpenSteakConfig
from opensteak.printer import OpenSteakPrinter
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
foreman = ForemanAPI(foreman_auth, '172.16.0.2')
conf = OpenSteakConfig(config_file='config/infra-test.yaml')
p = OpenSteakPrinter()

#~ #############################################
p.header("Check puppet classes")
#~ #############################################

smartProxy = conf['smart_proxies']
smartProxyId = foreman.get_id_by_name('smart_proxies', smartProxy)
p.status(bool(smartProxyId),
         'Check smart proxy ' + smartProxy + ' exists')
#~ p.status(bool(foreman.create('smart_proxies/{}/import_puppetclasses'.format(smartProxyId), '{}')),
       #~ 'Import puppet classes from proxy '+smartProxy)
p_ids = {}
for name in conf['hostgroups']:
    p_ids[name] = {}
    for pclass in conf['hostgroups'][name]['classes']:
        p_ids[name][pclass] = foreman.get_id_by_name('puppetclasses', pclass)
        p.status(bool(p_ids[name][pclass]), 'Puppet Class "{}"'.format(pclass))
p_ids['hostgroupTop'] = {}
for pclass in conf['hostgroupTop']['classes']:
        p_ids['hostgroupTop'][pclass] = foreman.get_id_by_name('puppetclasses', pclass)
        p.status(bool(p_ids['hostgroupTop'][pclass]), 'Puppet Class "{}"'.format(pclass))

#~ #############################################
p.header("Check and create")
#~ #############################################

#~
#~ Operating systems
#~
operatingSystems = conf['operatingsystems']
osActualTitles = foreman.list('operatingsystems', only_id=True, key='title')
for os, data in operatingSystems.items():
    if os not in osActualTitles.keys():
        payload = {'operatingsystem': {"title": os}}
        payload['operatingsystem'].update(data)
        foreman.create('operatingsystems', payload)
    isCreated = os in foreman.list('operatingsystems', only_id=True, key='title').keys()
    p.status(bool(isCreated), 'Operating system ' + os)
osIds = set(foreman.list('operatingsystems', only_id=True, key='title').values())

#~
#~ Architecture
#~
architecture = conf['architectures']
if not foreman.get_id_by_name('architectures', architecture):
    payload = {'architecture': {"name": architecture}}
    foreman.create('architectures', payload)
architectureId = foreman.get_id_by_name('architectures', architecture)
p.status(bool(architectureId), 'Architecture ' + architecture)
for os in foreman.list('architectures/{}/operatingsystems'.format(architectureId)):
    osIds.add(os['id'])
payload = {'architecture': {"operatingsystem_ids": list(osIds)}}
p.status(bool(foreman.set('architectures', architectureId, payload)),
         'Set OS  for architecture {}'.format(architecture))


#~
#~ Domain
#~
domainName = conf['domains']
if not foreman.get_id_by_name('domains', domainName):
    payload = {'domain': {"name": domainName}}
    foreman.create('domains', payload)
domainId = foreman.get_id_by_name('domains', domainName)
p.status(bool(domainId), 'Domain ' + domainName)

#~
#~ Subnets
#~
confSubnets = conf['subnets']
for name, data in confSubnets.items():
    #~ Create Hostgroup
    if not foreman.get_id_by_name('subnets', name):
        payload = {'subnet': {"name": name}}
        payload['subnet'].update(data['data'])
        if 'dhcp_id' not in data['data'].keys():
            payload['subnet']['dhcp_id'] = smartProxyId
        if 'tftp_id' not in data['data'].keys():
            payload['subnet']['tftp_id'] = smartProxyId
        if 'dns_id' not in data['data'].keys():
            payload['subnet']['dns_id'] = smartProxyId
        foreman.create('subnets', payload)
    subnetId = foreman.get_id_by_name('subnets', name)
    p.status(bool(subnetId), 'Subnet ' + name)
    subnetDomainIds = []
    for domain in foreman.list('subnets/{}/domains'.format(subnetId)):
        subnetDomainIds.append(domain['id'])
    if domainId not in subnetDomainIds:
        subnetDomainIds.append(domainId)
        payload = {'subnet': {"domain_ids": subnetDomainIds}}
        p.status(bool(foreman.set('subnets', subnetId, payload)),
                 'Add domain {} to subnet {}'.format(domainName, name))

#~
#~ Top Hostgroup
#~

#~ Create Hostgroup
hostgroupTop = conf['hostgroupTop']['name']
if not foreman.get_id_by_name('hostgroups', hostgroupTop):
    payload = {"hostgroup": {"name": hostgroupTop,
                             "environment_name": conf['environments'],
                             "subnet_name": conf['hostgroupTop']['subnet'],
                             "domain_name": domainName}}
    foreman.create('hostgroups', payload)
hostgroupTopId = foreman.get_id_by_name('hostgroups', hostgroupTop)
p.status(bool(hostgroupTopId), 'Hostgroup ' + hostgroupTop)

#~ Create Hostgroup classes
hostgroupClasses = foreman.list('hostgroups/{}/puppetclass_ids'.format(hostgroupTopId))
for k, v in p_ids['hostgroupTop'].items():
    if v not in hostgroupClasses:
        payload = {"puppetclass_id": v,
                   "hostgroup_class": {"puppetclass_id": v}}
        p.status(bool(foreman.create('hostgroups/{}/puppetclass_ids'.format(hostgroupTopId), payload)),
                 'Add puppet classe {} to {}'.format(k, hostgroupTop))
    else:
        p.status(True, 'Puppet class {} is in {}'.format(k, hostgroupTop))

#~
#~ Sub hostgroups
#~

confHostGr = conf['hostgroups']
for hg in confHostGr.keys():
    hg_name = confHostGr[hg]['name']

    #~ Create Hostgroup
    if not foreman.get_id_by_name('hostgroups', hostgroupTop + '-' + hg_name):
        payload = {
            "hostgroup": {
                "name": hostgroupTop + '-' + hg_name,
                "title": hostgroupTop + '/' + hg_name,
                "ancestry": str(hostgroupTopId),
            }
        }
        foreman.create('hostgroups', payload)
    hostgroupSubId = foreman.get_id_by_name('hostgroups', hostgroupTop + '-' + hg_name)
    p.status(bool(hostgroupSubId), 'Hostgroup {}/{}'.format(hostgroupTop, hg_name))
    hostgroupClasses = foreman.list('hostgroups/{}/puppetclass_ids'.format(hostgroupSubId))

    #~ Check Hostgroup classes
    for k, v in p_ids[hg].items():
        if v not in hostgroupClasses:
            payload = {"puppetclass_id": v,
                       "hostgroup_class": {"puppetclass_id": v}}
            p.status(bool(foreman.create('hostgroups/{}/puppetclass_ids'.format(hostgroupSubId), payload)),
                     'Add puppet class {} to {}/{}'.format(k, hostgroupTop, hg_name))
        else:
            p.status(True, 'Puppet class {} is in {}/{}'.format(k, hostgroupTop, hg_name))


sys.exit()
#~ #############################################
p.header("Clean")
#~ #############################################
# Delete hostgroups
for hg in confHostGr.keys():
    p.status(bool(foreman.delete('hostgroups', foreman.get_id_by_name('hostgroups', hostgroupTop + '-' + confHostGr[hg]['name']))),
             'Delete hostgroup {}/{}'.format(hostgroupTop, confHostGr[hg]['name']))
# Delete Hostgroup top
p.status(bool(foreman.delete('hostgroups', foreman.get_id_by_name('hostgroups', hostgroupTop))),
         'Delete hostgroup ' + hostgroupTop)
# Delete subnets or remove domain from its
for name, data in confSubnets.items():
    subnetId = foreman.get_id_by_name('subnets', name)
    subnetDomainIds = []
    for domain in foreman.list('subnets/{}/domains'.format(subnetId)):
        subnetDomainIds.append(domain['id'])
    subnetDomainIds.remove(domainId)
    payload = {'subnet': {"domain_ids": subnetDomainIds}}
    p.status(bool(foreman.set('subnets', subnetId, payload)),
             'Remove domain {} from subnet {}'.format(domainName, name))
    if not data['shared']:
        p.status(bool(foreman.delete('subnets', foreman.get_id_by_name('subnets', name))),
                 'Delete subnet ' + name)
# Delete domain
p.status(bool(foreman.delete('domains', foreman.get_id_by_name('domains', domainName))),
         'Delete domain ' + domainName)

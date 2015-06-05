#!/usr/bin/python3
from foreman.foremanAPI import ForemanAPI
from opensteak.conf import OpenSteakConfig
from opensteak.printer import OpenSteakPrinter
import time
import sys
from pprint import pprint as pp

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

#~
#~ Check all requesists are ok
#~
p.header("Check configuration")
ids = {}
for k, v in conf['environment'].items():
    ids[k] = foreman.get_id_by_name(k, v)
    p.config(k, v, ids[k])

#~
#~ Check all puppet classes are ok
#~
p.header("Check puppet classes")
p_ids = {}
for name in conf['opensteak']['vm_list']:
    p_ids[name] = {}
    if conf['vm'][name]['puppet_classes']:
        for pclass in conf['vm'][name]['puppet_classes']:
            p_ids[name][pclass] = foreman.get_id_by_name('puppetclasses', pclass)
            p.config('Puppet Class', pclass, p_ids[name][pclass])

#~
#~ Print controller specifics parameters
#~
p.header("Controller parameters")
for k, v in conf['controller'].items():
    p.config(k, v)

#~
#~ Wait for user input to continue
#~
p.header("List of VM to create")
for name in conf['opensteak']['vm_list']:
    p.list(name)
print()
p.ask_validation()

#~
#~ VM creation routine
#~
p.header("VM creation")
sleep = 5
for name in conf['opensteak']['vm_list']:
    payload = {
        "capabilities": "build image",
        "host": {
            "comment": conf['vm'][name]['description'],
            "compute_attributes": {
                "cpus": 2,
                "image_id": conf['controller']['image_id'],
                "memory": '4194304000',
                "nics_attributes": {
                    "0": {
                        "_delete": "",
                        "bridge": "",
                        "model": 'virtio',
                        "network": conf['controller']['bridge'],
                        "type": 'network',
                    },
                    "new_nics": {
                        "_delete": "",
                        "bridge": "",
                        "model": 'virtio',
                        "type": 'bridge',
                    },
                },
                "start": 1,
                "volumes_attributes": {
                    "0": {
                        "_delete": "",
                        "allocation": '0G',
                        "capacity": '10G',
                        "format_type": 'qcow2',
                        "pool_name": 'default',
                    },
                    "new_volumes": {
                        "_delete": "",
                        "allocation": '0G',
                        "capacity": '10G',
                        "format_type": 'raw',
                        "pool_name": 'default',
                    },
                },
            },
            "compute_resource_id":  ids['compute_resources'],
            "domain_id": ids['domains'],
            "build": "true",
            "enabled": 1,
            "environment_id": ids['environments'],
            "hostgroup_id": ids['hostgroups'],
            "medium_id": ids['media'],
            "ptable_id": ids['ptables'],
            "name":  name+'.'+conf['environment']['domains'],
            "operatingsystem_id": ids['operatingsystems'],
            "provision_method": 'image',
            "puppet_ca_proxy_id": ids['smart_proxies'],
            "puppet_proxy_id": ids['smart_proxies'],
            "puppetclass_ids": list(p_ids[name].values()),
            "subnet_id": ids['subnets'],
            "type": "Host::Managed",
            "interfaces_attributes": {
                "new_interfaces": {
                    "_destroy": "false",
                    "attached_to": "",
                    "domain_id": "",
                    "identifier": "",
                    "ip": "",
                    "mac": "",
                    "managed": 0,
                    "managed": 1,
                    "name": "",
                    "subnet_id": "",
                    "tag": "",
                    "type": "Nic::Managed",
                    "virtual": 0,
                },
            },
        },
        "provider": "Libvirt",
        "utf8": "✓"
    }
    name += '.'+conf['environment']['domains']

    #~ Create the VM in foreman
    p.status('In progress', name+' creation: push in Foreman', eol='\r')
    future1 = foreman.create('hosts', payload, async=True)
    for i in range(0, sleep):
        time.sleep(1)
        p.status('In progress', name+' creation: start in {0}s'.format(sleep-i), eol='\r')
    #~ Power on the VM
    p.status('In progress', name+' creation: starting', eol='\r')
    future2 = foreman.set('hosts', name, {"power_action": "start", "host": {}}, 'power', async=True)
    #~ Show Power on result
    if future2.result().status_code is 200:
        p.status('In progress', name+' creation: wait for end of boot', eol='\r')
    else:
        p.status(False, name+' creation: Error', failed=str(future2.result().status_code))
    #~ Show creation result
    if future1.result().status_code is 200:
        p.status('In progress', name+' creation: created', eol='\r')
    else:
        p.status(False, name+' creation: Error', failed=str(future1.result().status_code))
    #~ Wait for puppet catalog to be applied
    loop_stop = False
    while not loop_stop:
        status = foreman.get('hosts', name, 'status')['status']
        if status == 'No Changes' or status == 'Active':
            p.status(True, name+' creation: provisioning OK')
            loop_stop = True
        elif status == 'Error':
            p.status(False, name+' creation: Error', failed="Error during provisioning")
            loop_stop = True
        else:
            p.status('In progress', name+' creation: provisioning ('+status+')', eol='\r')
        time.sleep(5)

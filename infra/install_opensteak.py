#!/usr/bin/python3
# -*- coding: utf-8 -*-
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
#    Authors:
#     David Blaisonneau <david.blaisonneau@orange.com>
#     Arnaud Morin <arnaud1.morin@orange.com>

from opensteak.conf import OpenSteakConfig
from opensteak.foreman import OpenSteakForeman
from opensteak.printer import OpenSteakPrinter
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

foreman = OpenSteakForeman(login=sys.argv[1], password=sys.argv[2], ip=sys.argv[3])
conf = OpenSteakConfig(config_file='config/infra.yaml')
p = OpenSteakPrinter()

#~
#~ Check all requesists are ok
#~
p.header("Check configuration")
ids = {}
for k, v in conf['environment'].items():
    ids[k] = foreman.api.get_id_by_name(k, v)
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
            p_ids[name][pclass] = foreman.api.puppetclasses.pclass['id']
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
    foreman.host.createVM(name, payload, True)

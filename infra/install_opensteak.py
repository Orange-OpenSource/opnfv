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

# ###################
# Check for params
# ###################
p.header("Check parameters")
args = {}

# Update args with values from CLI
parser = argparse.ArgumentParser(description='This script will configure '
                                 'foreman.', usage='%(prog)s [options]')
parser.add_argument('-c', '--config', help='YAML config file to use '
                    '(default is config/infra.yaml).',
                    default='config/infra.yaml')
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

# ###################
# Prepare classes
# ###################
foreman = OpenSteakForeman(login=args["admin"],
                           password=args["password"],
                           ip=args["ip"])

# ###################
# Check all requesists are ok
# ###################

# p.header("Check configuration")
# ids = {}
# for k, v in conf['environment'].items():
#     ids[k] = foreman.api.get_id_by_name(k, v)
#     p.config(k, v, ids[k])

# ###################
# Check all puppet classes are ok
# ###################

p.header("Check puppet classes")
p_ids = {}
for name in conf['opensteak']['vm_list']:
    p_ids[name] = {}
    if conf['vm'][name]['puppet_classes']:
        for pclass in conf['vm'][name]['puppet_classes']:
            p_ids[name][pclass] = foreman.puppetClasses[pclass]['id']
            p.config('Puppet Class', pclass, p_ids[name][pclass])

# ###################
# Print controller specifics parameters
# ###################
p.header("Controllers attributes")
for k, v in conf['controllersAttributes'].items():
    p.config(k, v)

# ###################
# Wait for user input to continue
# ###################
p.header("List of VM to create")
for name in conf['opensteak']['vm_list']:
    p.list(name)
print()
# p.ask_validation()

# ###################
# VM creation routine
# ###################

p.header("VM creation")
sleep = 5
for name in conf['opensteak']['vm_list']:
    payload = {
        "host": {
            "comment": conf['vm'][name]['description'],
            "compute_attributes": {
                "cpus": 2,
                "image_id": conf['controllersAttributes']['cloudImagePath'],
                "memory": '4194304000',
                "nics_attributes": {
                    "0": {
                        "_delete": "",
                        "bridge": "",
                        "model": 'virtio',
                        "network": conf['controllersAttributes'][
                            'adminBridge'],
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
            "compute_resource_id":  foreman.computeResources[
                conf['defaultController']]['id'],
            "domain_id": conf['domains'],
            "build": "true",
            "enabled": 1,
            "environment_id": conf['environments'],
            "hostgroup_id": conf['hostgroups'],
            "medium_id": conf['media'],
            "ptable_id": conf['ptables'],
            "architecture_id": foreman.architectures[
                conf['architectures']]['id'],
            "name": "{0}.{1}".format(name, conf['domains']),
            "operatingsystem_id": conf['operatingsystems'],
            "provision_method": 'image',
            "puppet_ca_proxy_id": conf['smart_proxies'],
            "puppet_proxy_id": conf['smart_proxies'],
            "puppetclass_ids": list(p_ids[name].values()),
            "subnet_id": conf['subnets'],
            "type": "Host::Managed",
            "interfaces_attributes": {
                "new_interfaces": {
                    "_destroy": "false",
                    "attached_to": "",
                    "domain_id": "",
                    "identifier": "",
                    "ip": "",
                    "mac": "",
                    "managed": 1,
                    "name": "",
                    "subnet_id": "",
                    "tag": "",
                    "type": "Nic::Managed",
                    "virtual": 0,
                },
            },
        }
    }
    foreman.hosts.createVM("{0}.{1}".format(name, conf['domains']),
                           payload, False)

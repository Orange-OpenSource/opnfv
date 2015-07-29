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
from foreman import Foreman
from opensteak.printer import OpenSteakPrinter
import argparse
import sys
from pprint import pprint as pp

p = OpenSteakPrinter()

##############################################
p.header("Check parameters")
##############################################
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

foreman = Foreman(  login=args["admin"],
                    password=args["password"],
                    ip=args["ip"])

##############################################
# p.header("Check configuration")
##############################################
# ids = {}
# for k, v in conf['environment'].items():
#     ids[k] = foreman.api.get_id_by_name(k, v)
#     p.config(k, v, ids[k])

##############################################
p.header("Check puppet classes")
##############################################
p_ids = {}
for name in conf['opensteak']['vm_list']:
    p_ids[name] = {}
    if conf['vm'][name]['puppet_classes']:
        for pclass in conf['vm'][name]['puppet_classes']:
            p_ids[name][pclass] = foreman.puppetClasses[pclass]['id']
            p.config('Puppet Class', pclass, p_ids[name][pclass])

##############################################
p.header("Controllers attributes")
##############################################
for k, v in conf['controllersAttributes'].items():
    p.config(k, v)

##############################################
p.header("List of VM to create")
##############################################

for name in conf['opensteak']['vm_list']:
    p.list(name)
print()
# p.ask_validation()

##############################################
p.header("VM creation")
##############################################
#sleep = 5
for name in conf['opensteak']['vm_list']:
    payload = {
        "host": {
            "name": name,
            "comment": conf['vm'][name]['description'],
            "enabled": True,
            "build": True,
            "managed": True,
            "type": "Host::Managed",
            "disk": "",
            "environment_id": foreman.environments[
                conf['environments']]['id'],
            "operatingsystem_id": foreman.operatingSystems[
                conf['operatingsystems']]['id'],
            "compute_resource_id": foreman.computeResources[
                conf['defaultController']]['id'],
            "ptable_id": foreman.ptables[
                conf['ptables']]['id'],
            "medium_id": foreman.media[
                conf['media']]['id'],
            "architecture_id": foreman.architectures[
                conf['architectures']]['id'],
            "hostgroup_id": foreman.hostgroups[
                "{0}_{1}".format(
                    conf['hostgroupTop']['name'],
                    conf['hostgroups'])]['id'],
            "puppet_ca_proxy_id": foreman.smartProxies[
                conf['smart_proxies']]['id'],
            "puppet_proxy_id": foreman.smartProxies[
                conf['smart_proxies']]['id'],
            "puppetclass_ids": list(p_ids[name].values()),
            "provision_method": "image",
            "interfaces_attributes": {
                "0": {
                    "identifier": "",
                    "mac": "",
                    "name": name,
                    "managed": True,
                    "primary": True,
                    "provision": True,
                    "type": "Nic::Managed",
                    "domain_id": foreman.domains[
                        conf['domains']]['id'],
                    "subnet_id": foreman.subnets[
                        conf['subnets']]['id'],
                    "virtual": False,
                    "compute_attributes": {
                        "bridge": "",
                        "model": "virtio",
                        "network": conf['controllersAttributes'][
                            'adminBridge'],
                        "type": "network",
                    },
                }
            },
            "compute_attributes": {
                "cpus": 2,
                "image_id": conf['controllersAttributes']['cloudImagePath'],
                "memory": "4194304000",
                "start": True,
                "volumes_attributes": {
                    "0": {
                        "allocation": '0G',
                        "capacity": '10G',
                        "format_type": 'qcow2',
                        "pool_name": 'default',
                    }
                },
            },
            "mac": "",
            "root_pass": "password",
        },
        "provider": "Libvirt",
        "capabilities": "build image",
    }

    foreman.hosts.createVM("{0}.{1}".format(name, conf['domains']), payload, p)

#pp(foreman.api.history)

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

from foreman import Foreman
import argparse
from pprint import pprint as pp

#
# Check for params
#
args = {}

# Update args with values from CLI
parser = argparse.ArgumentParser(description='This script will connect to'
                                             'foreman.',
                                 usage='%(prog)s [options]')
parser.add_argument('-a', '--admin', help='Foreman admin login',
                        default='admin')
parser.add_argument('-p', '--password', help='Foreman admin password',
                        default='password')
parser.add_argument('-i', '--ip', help='Foreman API IP',
                        default='127.0.0.1')
args.update(vars(parser.parse_args()))

#
# Prepare classes
#
foreman = Foreman(login=args["admin"],
                           password=args["password"],
                           ip=args["ip"])

#hostname = "mysql.infra.opensteak.fr"
#host = foreman.hosts[hostname]
#hg = foreman.hostgroups[host['hostgroup_id']]
#domain = foreman.domains[host['domain_id']]
#ret = host.getUserData(hostgroup=hg,domain=domain['name'],tplFolder='foreman/files/metadata/templates/')
#pp(ret)

# from opensteak.foreman_objects.operatingsystems import OperatingSystems
# from opensteak.foreman_objects.api import Api
# from opensteak.foreman_objects.configTemplates import ConfigTemplates
# api = Api(login=args["admin"], password=args["password"], ip=args["ip"],
               # printErrors=False)
# operatingSystems = OperatingSystems(api)
# configTemplates =  ConfigTemplates(api)
# osName = "Ubuntu 14.04.2 LTS"

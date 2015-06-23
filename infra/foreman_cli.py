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

#
# Check for params
#
p = OpenSteakPrinter()
p.header("Check parameters")
args = {}

# Update args with values from CLI
parser = argparse.ArgumentParser(description='This script will configure foreman.', usage='%(prog)s [options]')
parser.add_argument('-c', '--config', help='YAML config file to use (default is config/infra.yaml).', default='config/infra.yaml')
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

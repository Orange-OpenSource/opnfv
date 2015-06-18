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
import sys
from pprint import pprint as pp

foreman = OpenSteakForeman(login=sys.argv[1],
                           password=sys.argv[2],
                           ip=sys.argv[3])
conf = OpenSteakConfig(config_file='config/infra-test.yaml')

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

from opensteak.foreman_objects.objects import ForemanObjects
from opensteak.foreman_objects.itemConfigTemplate import ItemConfigTemplate


class ConfigTemplates(ForemanObjects):
    """
    Environments class
    """
    objName = 'config_templates'
    payloadObj = 'config_template'
    index = 'name'
    searchLimit = 999
    itemType = ItemConfigTemplate


    template_kind_ids = {
        'PXELinux': 1,
        'PXEGrub': 2,
        'iPXE': 3,
        'provision': 4,
        'finish': 5,
        'script': 6,
        'user_data': 7,
        'ZTP': 8 }

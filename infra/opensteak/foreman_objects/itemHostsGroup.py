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

from opensteak.foreman_objects.item import ForemanItem
from opensteak.foreman_objects.subItemParameter import SubItemParameter
from opensteak.foreman_objects.subItemPuppetClasses import SubItemPuppetClasses
from opensteak.foreman_objects.subItemPuppetClassIds\
    import SubItemPuppetClassIds
from opensteak.foreman_objects.subDict import SubDict
from opensteak.foreman_objects.itemSmartClassParameter\
    import ItemSmartClassParameter


class ItemHostsGroup(ForemanItem):
    """
    ItemHostsGroup class
    Represent the content of a foreman hostgroup as a dict
    """

    objName = 'hostgroups'
    payloadObj = 'hostgroup'

    def enhance(self):
        """ Function enhance
        Enhance the object with new item or enhanced items
        """
        self.update({'puppetclass_ids':
                     SubDict(self.api, self.objName,
                             self.payloadObj, self.key,
                             SubItemPuppetClassIds)})
        self.update({'puppetclasses':
                     SubDict(self.api, self.objName,
                             self.payloadObj, self.key,
                             SubItemPuppetClasses)})
        self.update({'parameters':
                     SubDict(self.api, self.objName,
                             self.payloadObj, self.key,
                             SubItemParameter)})
        self.update({'smart_class_parameters':
                    SubDict(self.api, self.objName,
                            self.payloadObj, self.key,
                            ItemSmartClassParameter)})

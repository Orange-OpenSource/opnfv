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
from opensteak.foreman_objects.itemComputeRessource import ItemComputeRessource
from pprint import pprint as pp


class ComputeResources(ForemanObjects):
    """
    HostGroups class
    """
    objName = 'compute_resources'
    payloadObj = 'compute_resource'
    itemType = ItemComputeRessource
    index = 'name'

    def __getitem__(self, key):
        """ Function __getitem__
        Get an hostgroup

        @param key: The hostgroup name or ID
        @return RETURN: The ForemanItem object of an host
        """
        if type(key) is not int:
            key = self.listName()[key]
        ret = self.api.get(self.objName, key)
        return ItemComputeRessource(self.api, key, self.objName,
                                    self.payloadObj, ret)

    def __delitem__(self, key):
        """ Function __delitem__
        Delete an hostgroup

        @param key: The hostgroup name or ID
        @return RETURN: The API result
        """
        # Because Hostgroup did not support get by name we need to do it by id
        if type(key) is not int:
            key = self[key]['id']
        return self.api.delete(self.objName, key)

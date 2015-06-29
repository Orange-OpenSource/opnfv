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
from opensteak.foreman_objects.item import ForemanItem


class ComputeResources(ForemanObjects):
    """
    HostGroups class
    """
    objName = 'compute_resources'
    payloadObj = 'compute_resource'

    def list(self):
        """ Function list
        list the hostgroups

        @return RETURN: List of ForemanItemHostsGroup objects
        """
        return list(map(lambda x: ForemanItem(self.api, x['id'], x),
                        self.api.list(self.objName)))

    def __getitem__(self, key):
        """ Function __getitem__
        Get an hostgroup

        @param key: The hostgroup name or ID
        @return RETURN: The ForemanItemHostsGroup object of an host
        """
        # Because Hostgroup did not support get by name we need to do it by id
        if type(key) is not int:
            key = self.getId(key)
        ret = self.api.get(self.objName, key)
        return ForemanItem(self.api, key, ret)

    def __delitem__(self, key):
        """ Function __delitem__
        Delete an hostgroup

        @param key: The hostgroup name or ID
        @return RETURN: The API result
        """
        # Because Hostgroup did not support get by name we need to do it by id
        if type(key) is not int:
            key = self.getId(key)
        return self.api.delete(self.objName, key)

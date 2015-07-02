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
from opensteak.foreman_objects.itemHostsGroup import ItemHostsGroup
from pprint import pprint as pp


class HostGroups(ForemanObjects):
    """
    HostGroups class
    """
    objName = 'hostgroups'
    payloadObj = 'hostgroup'
    itemType = ItemHostsGroup

    def __getitem__(self, key):
        """ Function __getitem__
        Get an hostgroup

        @param key: The hostgroup name or ID
        @return RETURN: The ItemHostsGroup object of an host
        """
        # Because Hostgroup did not support get by name we need to do it by id
        if type(key) is not int:
            key = self.listName()[key]
        return ForemanObjects.__getitem__(self, key)

    def __delitem__(self, key):
        """ Function __delitem__
        Delete an hostgroup

        @param key: The hostgroup name or ID
        @return RETURN: The API result
        """
        # Because Hostgroup did not support get by name we need to do it by id
        if type(key) is not int:
            key = self.listName()[key]
        return ForemanObjects.__delitem__(self, key)

    def checkAndCreate(self, key, payload,
                       hostgroupConf,
                       hostgroupParent,
                       puppetClassesId):
        """ Function checkAndCreate
        check And Create procedure for an hostgroup
        - check the hostgroup is not existing
        - create the hostgroup
        - Add puppet classes from puppetClassesId
        - Add params from hostgroupConf

        @param key: The hostgroup name or ID
        @param payload: The description of the hostgroup
        @param hostgroupConf: The configuration of the host group from the
                              foreman.conf
        @param hostgroupParent: The id of the parent hostgroup
        @param puppetClassesId: The dict of puppet classes ids in foreman
        @return RETURN: The ItemHostsGroup object of an host
        """
        if key not in self:
            self[key] = payload
        oid = self[key]['id']
        if not oid:
            return False

        # Create Hostgroup classes
        if 'classes' in hostgroupConf.keys():
            classList = list()
            for c in hostgroupConf['classes']:
                classList.append(puppetClassesId[c])
            if not self[key].checkAndCreateClasses(classList):
                print("Failed in classes")
                return False

        # Set params
        if 'params' in hostgroupConf.keys():
            if not self[key].checkAndCreateParams(hostgroupConf['params']):
                print("Failed in params")
                return False

        return oid

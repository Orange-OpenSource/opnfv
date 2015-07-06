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
from opensteak.foreman_objects.itemOperatingSystem import ItemOperatingSystem


class OperatingSystems(ForemanObjects):
    """
    OperatingSystems class
    """
    objName = 'operatingsystems'
    payloadObj = 'operatingsystem'
    itemType = ItemOperatingSystem
    index = 'title'
    searchLimit = 20

    def __getitem__(self, key):
        """ Function __getitem__

        @param key: The operating system id/name
        @return RETURN: The item
        """
        ret = self.api.list(self.objName,
                            filter='title = "{}"'.format(key))
        if len(ret):
            return self.itemType(self.api,
                                 ret[0]['id'],
                                 self.objName,
                                 self.payloadObj,
                                 ret[0])
        else:
            return None

    def checkAndCreate(self, key, payload):
        """ Function checkAndCreate
        Check if an object exists and create it if not

        @param key: The targeted object
        @param payload: The targeted object description
        @return RETURN: The id of the object
        """
        if key not in self:
            if 'templates' in payload:
                templates = payload.pop('templates')
            self[key] = payload
            self.reload()
        return self[key]['id']

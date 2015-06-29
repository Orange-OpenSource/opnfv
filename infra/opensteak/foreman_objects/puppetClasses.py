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
from pprint import pprint as pp


class PuppetClasses(ForemanObjects):
    """
    OperatingSystems class
    """
    objName = 'puppetclasses'
    payloadObj = 'puppetclass'

    def list(self, limit=20):
        """ Function list
        Get the list of all objects

        @param key: The targeted object
        @param limit: The limit of items to return
        @return RETURN: A ForemanItem list
        """
        puppetClassList = list()
        for v in self.api.list(self.objName, limit=limit).values():
            puppetClassList.extend(v)
        return list(map(lambda x:
                        ForemanItem(self.api, x['id'],
                                    self.objName, self.payloadObj,
                                    x),
                        puppetClassList))

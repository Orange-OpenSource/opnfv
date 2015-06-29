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


class Architectures(ForemanObjects):
    """
    Architectures class
    """
    objName = 'architectures'
    payloadObj = 'architecture'

    def checkAndCreate(self, key, payload, osIds):
        """ Function checkAndCreate
        Check if an architectures exists and create it if not

        @param key: The targeted architectures
        @param payload: The targeted architectures description
        @param osIds: The list of os ids liked with this architecture
        @return RETURN: The id of the object
        """
        if key not in self:
            self[key] = payload
        oid = self[key]['id']
        if not oid:
            return False
        #~ To be sure the OS list is good, we ensure our os are in the list
        for os in self[key]['operatingsystems']:
            osIds.add(os['id'])
        self[key]["operatingsystem_ids"] = list(osIds)
        if (len(self[key]['operatingsystems']) is not len(osIds)):
            return False
        return oid

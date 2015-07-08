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

from opensteak.foreman_objects.subItem import SubItem


class SubItemPuppetClasses(SubItem):
    """
    ItemOverrideValues class
    Represent the content of a foreman smart class parameter as a dict
    """

    objName = 'puppetclasses'
    payloadObj = 'puppetclass_id'
    objNameSet = 'puppetclass_ids'
    index = 'id'
    setInParentPayload = False

    def getPayloadStruct(self, attributes, objType):
        """ Function getPayloadStruct
        Get the payload structure to do a creation or a modification

        @param attribute: The data
        @param objType: SubItem type (e.g: hostgroup for hostgroup_class)
        @return RETURN: the payload
        """
        payload = {self.payloadObj: attributes,
                   objType + "_class":
                       {self.payloadObj: attributes}}
        return payload

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
from opensteak.foreman_objects.subDict import SubDict
from opensteak.foreman_objects.subItemImages import SubItemImages
from pprint import pprint as pp


class ItemComputeRessource(ForemanItem):
    """
    ItemHost class
    Represent the content of a foreman hostgroup as a dict
    """

    objName = 'compute_ressources'
    payloadObj = 'compute_ressource'

    def enhance(self):
        """ Function enhance
        Enhance the object with new item or enhanced items
        """
        self.update({'images':
                     SubDict(self.api, self.objName,
                             self.payloadObj, self.key,
                             SubItemImages)})

    def __setitem__(self, key, attributes):
        """ Function __setitem__
        Set a parameter of a foreman object as a dict

        @param key: The key to modify
        @param attribute: The data
        @return RETURN: The API result
        """

        if key in ['images']:
            return ForemanItem.__setitem__(self,
                                           self[key].objType.payloadObj,
                                           attributes)
        else:
            return ForemanItem.__setitem__(self, key, attributes)

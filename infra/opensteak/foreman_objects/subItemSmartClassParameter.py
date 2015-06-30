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
from opensteak.foreman_objects.item import ForemanItem
from opensteak.foreman_objects.itemSmartClassParameter import ItemSmartClassParameter


class SubItemSmartClassParameter(dict):
    """
    ItemOverrideValues class
    Represent the content of a foreman smart class parameter as a dict
    """

    objName = 'smart_class_parameters'
    payloadObj = 'smart_class_parameter'
    index = 'id'

    def __init__(self, api, key, parentName, parentKey, *args, **kwargs):
        """ Function __init__
        Represent the content of a foreman object as a dict

        @param api: The foreman api
        @param key: The object Key
        @param parentName: The object parent name (eg: smart_class_parameter)
        @param parentKey: The object parent key
        @param *args, **kwargs: the dict representation
        @return RETURN: Itself
        """
        self.parentName = parentName
        self.parentKey = parentKey
        self.api = api
        scp_ids = map(lambda x: x['id'],
                      self.api.list('{}/{}/smart_class_parameters'
                                    .format(self.objName, key)))
        scp_items = list(map(lambda x: ItemSmartClassParameter(self.api, x,
                             self.api.get('smart_class_parameters', x)),
                             scp_ids))
        scp = {'{}::{}'.format(x['puppetclass']['name'],
                               x['parameter']): x
               for x in scp_items}
        self.update({'smart_class_parameters_dict': scp})

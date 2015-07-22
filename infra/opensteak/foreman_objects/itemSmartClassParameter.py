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
from opensteak.foreman_objects.subItemOverrideValues\
    import SubItemOverrideValues
from opensteak.foreman_objects.subDict import SubDict
from pprint import pprint as pp


class ItemSmartClassParameter(ForemanItem):
    """
    ItemSmartClassParameter class
    Represent the content of a foreman smart class parameter as a dict
    """

    objName = 'smart_class_parameters'
    objNameSet = 'smart_class_parameters'
    payloadObj = 'smart_class_parameter'
    index = 'id'

    def __init__(self, api, key,
                 objName, payloadObj,
                 *args, **kwargs):
        """ Function __init__
        Represent the content of a foreman object as a dict

        @param api: The foreman api
        @param key: The object Key
        @param objName: NO USED HERE
        @param payloadObj: NO USED HERE
        @param *args, **kwargs: the dict representation
        @return RETURN: Itself
        """
        self.api = api
        self.key = key
        self.store = dict()
        if args[0]:
            self.load(dict(*args, **kwargs))

    def enhance(self):
        """ Function enhance
        Enhance the object with new item or enhanced items
        """
        self.update({'override_values':
                    SubDict(self.api, self.objName,
                            self.payloadObj, self.key,
                            SubItemOverrideValues)})

    def __setitem__(self, key, attributes):
        """ Function __setitem__
        Set a parameter of a foreman object as a dict

        @param key: The key to modify
        @param attribute: The data
        @return RETURN: The API result
        """
        if key in ['override_values']:
            print('Can not assign {} directly, use .append()'.format(key))
            return False
        else:
            return ForemanItem.__setitem__(self, key, attributes)


    def getOverrideValueForHost(self, hostname):
        for sc in self['override_values'].values():
            if sc['match'] == 'fqdn=' + hostname:
                return sc
        return False

    def setOverrideValue(self, attributes, hostName):
        """ Function __setitem__
        Set a parameter of a foreman object as a dict

        @param key: The key to modify
        @param attribute: The data
        @return RETURN: The API result
        """
        self['override'] = True
        attrType = type(attributes)
        if attrType is list:
            self['parameter_type'] = 'array'
        elif attrType is dict:
            self['parameter_type'] = 'hash'
        else:
            self['parameter_type'] = 'string'
        orv = self.getOverrideValueForHost(hostName)
        if orv:
            orv['value'] = attributes
            return True
        else:
            self.api.create('{}/{}/{}'.format(self.objName,
                                              self.key,
                                              'override_values'),
                            {"override_value":
                                {"match": "fqdn={}".format(hostName),
                                 "value": attributes}})

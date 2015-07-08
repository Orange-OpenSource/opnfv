#!/usr/bin/python3
# -*- coding: utf-8 -*-
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
#    Authors:
#     David Blaisonneau <david.blaisonneau@orange.com>
#     Arnaud Morin <arnaud1.morin@orange.com>

from pprint import pprint as pp
from opensteak.foreman_objects.subDict import SubDict


class ForemanItem(dict):
    """
    Item class
    Represent the content of a foreman object as a dict
    """

    def __init__(self, api, key,
                 objName, payloadObj,
                 *args, **kwargs):
        """ Function __init__
        Represent the content of a foreman object as a dict

        @param api: The foreman api
        @param key: The object Key
        @param objName: The object name to override the default one
        @param payloadObj: The payload object name to override the default one
        @param *args, **kwargs: the dict representation
        @return RETURN: Itself
        """
        self.api = api
        self.key = key
        if objName:
            self.objName = objName
        if payloadObj:
            self.payloadObj = payloadObj
        self.store = dict()
        if args[0]:
            self.load(dict(*args, **kwargs))
        # We get the smart class parameters for the good items

    def load(self, data):
        """ Function load
        Store the object data
        """
        self.clear()
        self.update(data)
        self.enhance()

    def enhance(self):
        """ Function enhance
        Enhance the object with new item or enhanced items
        """
        if self.objName in ['hosts', 'hostgroups',
                            'puppet_classes']:
            from opensteak.foreman_objects.itemSmartClassParameter\
                import ItemSmartClassParameter
            self.update({'smart_class_parameters':
                        SubDict(self.api, self.objName,
                                self.payloadObj, self.key,
                                ItemSmartClassParameter)})

    def reload(self):
        """ Function reload
        Sync the full object
        """
        self.load(self.api.get(self.objName, self.key))

    def __setitem__(self, key, attributes):
        """ Function __setitem__
        Set a parameter of a foreman object as a dict

        @param key: The key to modify
        @param attribute: The data
        @return RETURN: The API result
        """
        payload = {self.payloadObj: {key: attributes}}
        return self.api.set(self.objName, self.key, payload)

    def getParam(self, name=None):
        """ Function getParam
        Return a dict of parameters or a parameter value

        @param key: The parameter name
        @return RETURN: dict of parameters or a parameter value
        """
        if 'parameters' in self.keys():
            l = {x['name']: x['value'] for x in self['parameters']}
            if name:
                if name in l.keys():
                    return l[name]
                else:
                    return False
            else:
                return l

    def checkAndCreateClasses(self, classes):
        """ Function checkAndCreateClasses
        Check and add puppet class

        @param classes: The classes ids list
        @return RETURN: boolean
        """
        actual_classes = self['puppetclasses'].keys()
        for i in classes:
            if i not in actual_classes:
                self['puppetclasses'].append(i)
        self.reload()
        return set(classes).issubset(set((self['puppetclasses'].keys())))

    def checkAndCreateParams(self, params):
        """ Function checkAndCreateParams
        Check and add global parameters

        @param key: The parameter name
        @param params: The params dict
        @return RETURN: boolean
        """
        actual_params = self['parameters'].keys()
        for k, v in params.items():
            if k not in actual_params:
                self['parameters'].append({"name": k, "value": v})
        self.reload()
        return self['parameters'].keys() == params.keys()

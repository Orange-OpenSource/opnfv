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
            self.update(dict(*args, **kwargs))
        # We get the smart class parameters for the good items
        if objName in ['hosts', 'hostgroups',
                       'puppet_classes', 'environments']:
            from opensteak.foreman_objects.itemSmartClassParameter\
                import ItemSmartClassParameter
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

    def __setitem__(self, key, attributes):
        """ Function __setitem__
        Set a parameter of a foreman object as a dict

        @param key: The key to modify
        @param attribute: The data
        @return RETURN: The API result
        """
        if key is 'puppetclass_ids':
            payload = {"puppetclass_id": attributes,
                       self.payloadObj + "_class":
                           {"puppetclass_id": attributes}}
            return self.api.create("{}/{}/{}"
                                   .format(self.objName,
                                           self.key,
                                           "puppetclass_ids"),
                                   payload)
        elif key is 'parameters':
            payload = {"parameter": attributes}
            return self.api.create("{}/{}/{}"
                                   .format(self.objName,
                                           self.key,
                                           "parameters"),
                                   payload)
        else:
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
        Check and add puppet classe

        @param key: The parameter name
        @param classes: The classes ids list
        @return RETURN: boolean
        """
        actual_classes = self['puppetclass_ids']
        for v in classes:
            if v not in actual_classes:
                self['puppetclass_ids'] = v
        return list(classes).sort() is list(self['puppetclass_ids']).sort()

    def checkAndCreateParams(self, params):
        """ Function checkAndCreateParams
        Check and add global parameters

        @param key: The parameter name
        @param params: The params dict
        @return RETURN: boolean
        """
        actual_params = self['param_ids']
        for k, v in params.items():
            if k not in actual_params:
                self['parameters'] = {"name": k, "value": v}
        return self['param_ids'].sort() == list(params.values()).sort()

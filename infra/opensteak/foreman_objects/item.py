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


class ForemanItem(dict):
    """
    Item class
    Represent the content of a foreman object as a dict
    """

    def __init__(self, parent, key, *args, **kwargs):
        """ Function __init__
        Represent the content of a foreman object as a dict

        @param parent: The parent object class
        @param key: The parent object Key
        @param *args, **kwargs: the dict representation
        @return RETURN: Itself
        """
        self.parent = parent
        self.key = key
        self.store = dict()
        if args[0]:
            self.update(dict(*args, **kwargs))

    def __setitem__(self, key, attributes):
        """ Function __setitem__
        Set a parameter of a foreman object as a dict

        @param key: The key to modify
        @param attribute: The data
        @return RETURN: The API result
        """
        payload = {self.parent.payloadObj: {key: attributes}}
        return self.parent.api.set(self.parent.objName, self.key, payload)

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

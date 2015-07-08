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
from pprint import pprint as pp


class SubItem(dict):
    """
    ItemOverrideValues class
    Represent the content of a foreman smart class parameter as a dict
    """
    setInParentPayload = False

    def __init__(self, api, key, parentName, parentPayloadObject,
                 parentKey, *args, **kwargs):
        """ Function __init__
        Represent the content of a foreman object as a dict

        @param api: The foreman api
        @param key: The object Key
        @param parentName: The object parent name (eg: smart_class_parameters)
        @param parentPayloadObject: The object parent
                                    payload object (eg: smart_class_parameter)
        @param parentKey: The object parent key
        @param *args, **kwargs: the dict representation
        @return RETURN: Itself
        """
        self.key = key
        self.api = api
        self.parentName = parentName
        self.parentPayloadObject = parentPayloadObject
        self.parentKey = parentKey
        if args[0]:
            self.update(dict(*args, **kwargs))

    def getPayloadStruct(self, attributes, objType=None):
        """ Function getPayloadStruct
        Get the payload structure to do a creation or a modification

        @param key: The key to modify
        @param attribute: The data
        @param objType: NOT USED in this class
        @return RETURN: The API result
        """
        if self.setInParentPayload:
            return {self.parentPayloadObject:
                    {self.payloadObj: attributes}}
        else:
            return {self.payloadObj: attributes}

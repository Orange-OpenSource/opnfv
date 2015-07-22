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
from pprint import pprint as pp


class ForemanObjects(dict):
    """
    ForemanObjects class
    Parent class for Foreman Objects
    """
    searchLimit = 99
    index = 'name'
    itemType = ForemanItem
    forceFullSync = False

    def __init__(self, api, objName=None, payloadObj=None,
                 index=None, searchLimit=None):
        """ Function __init__
        Init the foreman object

        @param api: The foreman API
        @param objName: The object name (linked with the Foreman API)
        @param payloadObj: The object name inside the payload (in general
                           the singular of objName)
        @param index: The object index name
        @param searchLimit: limit of item to search
        @return RETURN: Itself
        """

        self.api = api
        if objName:
            self.objName = objName
        if payloadObj:
            self.payloadObj = payloadObj
        # For asynchronous creations
        self.async = False
        # Default params
        if index:
            self.index = index
        if searchLimit:
            self.searchLimit = searchLimit
        dict.__init__(self, self.load())

    def reload(self):
        """ Function reload
        Reload the full object to ensure sync
        """
        realData = self.load()
        self.clear()
        self.update(realData)


    def updateAfterDecorator(function):
        """ Function updateAfterDecorator
        Decorator to ensure local dict is sync with remote foreman
        """
        def _updateAfterDecorator(self, *args, **kwargs):
            ret = function(self, *args, **kwargs)
            self.reload()
            return ret
        return _updateAfterDecorator

    def updateBeforeDecorator(function):
        """ Function updateAfterDecorator
        Decorator to ensure local dict is sync with remote foreman
        """
        def _updateBeforeDecorator(self, *args, **kwargs):
            if self.forceFullSync:
                self.reload()
            return function(self, *args, **kwargs)
        return _updateBeforeDecorator

    def get(self, key):
        """ Alias to __getitem__ """
        return self.__getitem__(key)

    def __getitem__(self, key):
        """ Function __getitem__
        We get the object from the API at each time to avoid sync problems

        @param key: The targeted object
        @return RETURN: A ForemanItem
        """
        return self.itemType(self.api,
                             key,
                             self.objName,
                             self.payloadObj,
                             self.api.get(self.objName, key))

    def set(self, key, attributes):
        """ Alias to __setitem__ """
        return self.__setitem__(key, attributes)

    @updateAfterDecorator
    def __setitem__(self, key, attributes):
        """ Function __setitem__

        @param key: The targeted object
        @param attributes: The attributes to apply to the object
        @return RETURN: API result if the object was not present, or False
        """
        if key not in self:
            payload = {self.payloadObj: {self.index: key}}
            payload[self.payloadObj].update(attributes)
            return self.api.create(self.objName, payload, async=self.async)
        return False

    @updateAfterDecorator
    def __delitem__(self, key):
        """ Function __delitem__

        @return RETURN: API result
        """
        return self.api.delete(self.objName, key)

    def __contains__(self, key):
        """ Function __contains__

        @param key: The targeted object
        @return RETURN: True if the object exists
        """
        return bool(key in self.listName().keys())

    def load(self):
        """ Function load
        Get the list of all objects

        @return RETURN: A ForemanItem list
        """
        return {x[self.index]: self.itemType(self.api, x['id'],
                                             self.objName, self.payloadObj,
                                             x)
                for x in self.api.list(self.objName,
                                       limit=self.searchLimit)}

    @updateBeforeDecorator
    def listName(self):
        """ Function listName
        Get the list of all objects name with Ids

        @param key: The targeted object
        @return RETURN: A dict of obejct name:id
        """
        return {x[self.index]: x['id'] for x in self.values()}

    def checkAndCreate(self, key, payload):
        """ Function checkAndCreate
        Check if an object exists and create it if not

        @param key: The targeted object
        @param payload: The targeted object description
        @return RETURN: The id of the object
        """
        if key not in self:
            self[key] = payload
        return self[key]['id']

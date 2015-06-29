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


class ForemanObjects:
    """
    ForemanObjects class
    Parent class for Foreman Objects
    """

    def __init__(self, api, objName=None, payloadObj=None):
        """ Function __init__
        Init the foreman object

        @param api: The foreman API
        @param objName: The object name (linked with the Foreman API)
        @param payloadObj: The object name inside the payload (in general
                           the singular of objName)
        @return RETURN: Itself
        """

        self.api = api
        if objName:
            self.objName = objName
        if payloadObj:
            self.payloadObj = payloadObj
        # For asynchronous creations
        self.async = False

    def __iter__(self):
        """ Function __iter__

        @return RETURN: The iteration of objects list
        """
        return iter(self.list())

    def __getitem__(self, key):
        """ Function __getitem__

        @param key: The targeted object
        @return RETURN: A ForemanItem
        """
        return ForemanItem(self.api,
                           key,
                           self.objName,
                           self.payloadObj,
                           self.api.get(self.objName, key))

    def __setitem__(self, key, attributes):
        """ Function __setitem__

        @param key: The targeted object
        @param attributes: The attributes to apply to the object
        @return RETURN: API result if the object was not present, or False
        """
        if key not in self:
            payload = {self.payloadObj: {'name': key}}
            payload[self.payloadObj].update(attributes)
            return self.api.create(self.objName, payload, async=self.async)
        return False

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

    def getId(self, key):
        """ Function getId
        Get the id of an object

        @param key: The targeted object
        @return RETURN: The ID
        """
        return self.api.get_id_by_name(self.objName, key)

    def list(self, limit=20):
        """ Function list
        Get the list of all objects

        @param key: The targeted object
        @param limit: The limit of items to return
        @return RETURN: A ForemanItem list
        """
        return list(map(lambda x:
                        ForemanItem(self.api, x['id'],
                                    self.objName, self.payloadObj,
                                    x),
                        self.api.list(self.objName, limit=limit)))

    def listName(self):
        """ Function listName
        Get the list of all objects name with Ids

        @param key: The targeted object
        @return RETURN: A dict of obejct name:id
        """
        return self.api.list(self.objName, limit=999999, only_id=True)

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

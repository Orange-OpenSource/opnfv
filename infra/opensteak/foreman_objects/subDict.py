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


class SubDict(dict):
    """
    SubLists class
    """

    def __init__(self, api, parentObjName,
                 parentPayloadObj, parentKey,
                 objType):
        """ Function load
        To be rewriten

        @param id: The Domain ID
        @return RETURN: DESCRIPTION
        """
        self.api = api
        self.parentObjName = parentObjName
        self.parentPayloadObj = parentPayloadObj
        self.parentKey = parentKey
        self.objType = objType
        self.objName = objType.objName
        self.index = objType.index
        dict.__init__(self, self.get())

    def get(self, limit=9999):
        """ Function list
        Get the list of all interfaces

        @param key: The targeted object
        @param limit: The limit of items to return
        @return RETURN: A ForemanItem list
        """
        subItemList = self.api.list('{}/{}/{}'.format(self.parentObjName,
                                                      self.parentKey,
                                                      self.objName,
                                                      ),
                                    limit=limit)
        if self.objName == 'puppetclasses':
            sil_tmp = subItemList.values()
            subItemList = []
            for i in sil_tmp:
                subItemList.extend(i)
        return {x[self.index]: self.objType(self.api, x['id'],
                                            self.parentObjName,
                                            self.parentPayloadObj,
                                            x)
                for x in subItemList}

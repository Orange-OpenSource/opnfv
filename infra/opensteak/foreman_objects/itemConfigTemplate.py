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
from opensteak.foreman_objects.subItemOperatingSystem\
    import SubItemOperatingSystem
from opensteak.foreman_objects.subItemOsDefaultTemplate\
    import SubItemOsDefaultTemplate
from pprint import pprint as pp


class ItemConfigTemplate(ForemanItem):
    """
    ItemHost class
    Represent the content of a foreman hostgroup as a dict
    """

    objName = 'config_templates'
    payloadObj = 'config_template'

    def enhance(self):
        """ Function enhance
        Enhance the object with new item or enhanced items
        """
        self.update({'os_default_templates':
                     SubDict(self.api, self.objName,
                             self.payloadObj, self.key,
                             SubItemOsDefaultTemplate)})
        self.update({'operatingsystems':
                     SubDict(self.api, self.objName,
                             self.payloadObj, self.key,
                             SubItemOperatingSystem)})

    def __setitem__(self, key, attributes):
        """ Function __setitem__
        Set a parameter of a foreman object as a dict

        @param key: The key to modify
        @param attribute: The data
        @return RETURN: The API result
        """

        if key in ['os_default_templates']:
            pp(attributes)
            print('Can not assign {} directly, use +='.format(key))
            return False
        elif key in ['operatingsystems']:
            return ForemanItem.__setitem__(self,
                                           self[key].objType.payloadObj,
                                           attributes)
        else:
            return ForemanItem.__setitem__(self, key, attributes)

    def checkOrAddOS(self, osName, osId):
        if osName not in self['operatingsystems']:
            osL = list(map(lambda x: x['id'],
                           self['operatingsystems'].values()))
            osL.append(osId)
            self['operatingsystems'] = osL
            self.reload()
        return osName in self['operatingsystems']

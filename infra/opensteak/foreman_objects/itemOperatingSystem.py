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
from opensteak.foreman_objects.subItemOsDefaultTemplate\
    import SubItemOsDefaultTemplate
from opensteak.foreman_objects.subItemPTable import SubItemPTable
from opensteak.foreman_objects.subItemMedia import SubItemMedia
from opensteak.foreman_objects.subItemArchitecture import SubItemArchitecture
from opensteak.foreman_objects.subItemConfigTemplate\
    import SubItemConfigTemplate
from pprint import pprint as pp


class ItemOperatingSystem(ForemanItem):
    """
    ItemHost class
    Represent the content of a foreman hostgroup as a dict
    """

    objName = 'operatingsystems'
    payloadObj = 'operatingsystem'

    def enhance(self):
        """ Function enhance
        Enhance the object with new item or enhanced items
        """
        self.update({'os_default_templates':
                     SubDict(self.api, self.objName,
                             self.payloadObj, self.key,
                             SubItemOsDefaultTemplate)})
        self.update({'config_templates':
                     SubDict(self.api, self.objName,
                             self.payloadObj, self.key,
                             SubItemConfigTemplate)})
        self.update({'ptables':
                     SubDict(self.api, self.objName,
                             self.payloadObj, self.key,
                             SubItemPTable)})
        self.update({'media':
                     SubDict(self.api, self.objName,
                             self.payloadObj, self.key,
                             SubItemMedia)})
        self.update({'architectures':
                     SubDict(self.api, self.objName,
                             self.payloadObj, self.key,
                             SubItemArchitecture)})

    def __setitem__(self, key, attributes):
        """ Function __setitem__
        Set a parameter of a foreman object as a dict

        @param key: The key to modify
        @param attribute: The data
        @return RETURN: The API result
        """

        if key in ['os_default_templates']:
            return False
        elif key in ['config_templates',
                     'ptables',
                     'media',
                     'architectures']:
            return ForemanItem.__setitem__(self,
                                           self[key].objType.payloadObj,
                                           attributes)
        else:
            return ForemanItem.__setitem__(self, key, attributes)

    def checkOrAddDefaultTemplate(self, tpl):
        if tpl['name'] not in self['os_default_templates']:
            self['os_default_templates'] += {
                "config_template_id": tpl['id'],
                "template_kind_id": tpl['template_kind_id']}
            self.reload()
        return tpl['name'] in self['os_default_templates']

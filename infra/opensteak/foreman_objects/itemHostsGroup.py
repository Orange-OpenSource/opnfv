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

from opensteak.foreman_objects.item import ForemanItem


class ForemanItemHostsGroup(ForemanItem):
    """
    ForemanItemHostsGroup class
    Represent the content of a foreman hostgroup as a dict
    """

    def __init__(self, parent, key, *args, **kwargs):
        """ Function __init__
        Represent the content of a foreman hostgroup as a dict
        Add 2 keys:
        - puppetclass_ids: a list of puppet classes ids
        - param_ids: a list with the names of the params

        @param parent: The parent object class
        @param key: The parent object Key
        @param *args, **kwargs: the dict representation
        @return RETURN: Itself
        """
        ForemanItem.__init__(self, parent, key, *args, **kwargs)
        self.update({'puppetclass_ids':
                     self.parent.api.list('hostgroups/{}/puppetclass_ids'
                                          .format(key))})
        self.update({'param_ids':
                     list(self.parent.api.list('hostgroups/{}/parameters'
                                               .format(key), only_id=True)

                          .keys())})

    def __setitem__(self, key, attributes):
        """ Function __setitem__
        Set a parameter of a foreman object as a dict

        @param key: The key to modify
        @param attribute: The data
        @return RETURN: The API result
        """
        if key is 'puppetclass_ids':
            payload = {"puppetclass_id": attributes,
                       "hostgroup_class": {"puppetclass_id": attributes}}
            return self.parent.api.create("{}/{}/{}"
                                          .format(self.parent.objName,
                                                  self.key,
                                                  "puppetclass_ids"),
                                          payload)
        elif key is 'parameters':
            payload = {"parameter": attributes}
            return self.parent.api.create("{}/{}/{}"
                                          .format(self.parent.objName,
                                                  self.key,
                                                  "parameters"),
                                          payload)
        else:
            payload = {self.parent.payloadObj: {key: attributes}}
            return self.parent.api.set(self.parent.objName, self.key, payload)

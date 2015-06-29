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

from opensteak.foreman_objects.objects import ForemanObjects


class SmartProxies(ForemanObjects):
    """
    Domain class
    """
    objName = 'smart_proxies'
    payloadObj = 'smart_proxy'

    def importPuppetClasses(self, smartProxyId):
        """ Function importPuppetClasses
        Force the reload of puppet classes

        @param smartProxyId: smartProxy Id
        @return RETURN: the API result
        """
        return self.api.create('smart_proxies/{}/import_puppetclasses'.format(smartProxyId), '{}')

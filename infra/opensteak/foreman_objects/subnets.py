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


class Subnets(ForemanObjects):
    """
    Subnets class
    """
    objName = 'subnets'
    payloadObj = 'subnet'

    def checkAndCreate(self, key, payload, domainId):
        """ Function checkAndCreate
        Check if a subnet exists and create it if not

        @param key: The targeted subnet
        @param payload: The targeted subnet description
        @param domainId: The domainId to be attached wiuth the subnet
        @return RETURN: The id of the subnet
        """
        if key not in self:
            self[key] = payload
        oid = self[key]['id']
        if not oid:
            return False
        #~ Ensure subnet contains the domain
        subnetDomainIds = []
        for domain in self[key]['domains']:
            subnetDomainIds.append(domain['id'])
        if domainId not in subnetDomainIds:
            subnetDomainIds.append(domainId)
            self[key]["domain_ids"] = subnetDomainIds
            if len(self[key]["domains"]) is not len(subnetDomainIds):
                return False
        return oid

    def removeDomain(self, subnetId, domainId):
        """ Function removeDomain
        Delete a domain from a subnet

        @param subnetId: The subnet Id
        @param domainId: The domainId to be attached wiuth the subnet
        @return RETURN: boolean
        """
        subnetDomainIds = []
        for domain in self[subnetId]['domains']:
            subnetDomainIds.append(domain['id'])
        subnetDomainIds.remove(domainId)
        self[subnetId]["domain_ids"] = subnetDomainIds
        return len(self[subnetId]["domains"]) is len(subnetDomainIds)

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

from opensteak.foreman_objects.api import Api
from opensteak.foreman_objects.objects import ForemanObjects
from opensteak.foreman_objects.domains import Domains
from opensteak.foreman_objects.smart_proxies import SmartProxies
from opensteak.foreman_objects.operatingsystems import OperatingSystems
from opensteak.foreman_objects.hostgroups import HostGroups
from opensteak.foreman_objects.hosts import Hosts
from opensteak.foreman_objects.architectures import Architectures
from opensteak.foreman_objects.subnets import Subnets
from opensteak.foreman_objects.puppetClasses import PuppetClasses
from opensteak.foreman_objects.compute_resources import ComputeResources


class OpenSteakForeman:
    """
    HostGroup class
    """
    def __init__(self, password, login='admin', ip='127.0.0.1'):
        """ Function __init__
        Init the API with the connection params
        @param password: authentication password
        @param password: authentication login - default is admin
        @param ip: api ip - default is localhost
        @return RETURN: self
        """
        self.api = Api(login=login, password=password, ip=ip,
                       printErrors=False)
        self.domains = Domains(self.api)
        self.smartProxies = SmartProxies(self.api)
        self.puppetClasses = PuppetClasses(self.api)
        self.operatingSystems = OperatingSystems(self.api)
        self.architectures = Architectures(self.api)
        self.subnets = Subnets(self.api)
        self.hostgroups = HostGroups(self.api)
        self.hosts = Hosts(self.api)
        self.computeResources = ComputeResources(self.api)
        self.environments =  ForemanObjects(self.api,
                                            'environments',
                                            'environment')
        self.smartClassParameters =  ForemanObjects(self.api,
                                                   'smart_class_parameters',
                                                   'smart_class_parameter')

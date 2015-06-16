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

import base64
from string import Template
from opensteak.foreman_objects.item import ForemanItem
from pprint import pprint as pp


class ForemanItemHost(ForemanItem):
    """
    ForemanItemHostsGroup class
    Represent the content of a foreman hostgroup as a dict
    """

    def __init__(self, parent, key, *args, **kwargs):
        """ Function __init__
        Represent the content of a foreman host as a dict
        Add 2 keys:
        - puppetclass_ids: a list of puppet classes ids
        - param_ids: a list with the names of the params

        @param parent: The parent object class
        @param key: The parent object Key
        @param *args, **kwargs: the dict representation
        @return RETURN: Itself
        """
        ForemanItem.__init__(self, parent, key, *args, **kwargs)

    def getStatus(self):
        """ Function getStatus
        Get the status of an host

        @return RETURN: The host status
        """
        return self.parent.api.get('hosts', self.key, 'status')['status']

    def powerOn(self):
        """ Function powerOn
        Power on a host

        @return RETURN: The API result
        """
        return self.parent.api.set('hosts', self.key,
                                   {"power_action": "start"},
                                   'power', async=self.async)

    def getParamFromEnv(self, var, default = ''):
        """ Function getParamFromEnv
        Search a parameter in the host environment

        @param var: the var name
        @param hostgroup: the hostgroup item linked to this host
        @param default: default value
        @return RETURN: the value
        """
        if self.getParam(var):
            return self.getParam(var)
        if self.hostgroup:
            if self.hostgroup.getParam(var):
                return self.hostgroup.getParam(var)
        if self.domain.getParam('password'):
            return self.domain.getParam('password')
        else:
            return default

    def getUserData(self,
                    hostgroup,
                    domain,
                    defaultPwd = '',
                    defaultSshKey = '',
                    tplFolder='templates/'):
        """ Function getUserData
        Generate a userdata script for metadata server from Foreman API

        @param domain: the domain item linked to this host
        @param hostgroup: the hostgroup item linked to this host
        @param defaultPwd: the default password if no password is specified
                           in the host>hostgroup>domain params
        @param defaultSshKey: the default ssh key if no password is specified
                              in the host>hostgroup>domain params
        @param tplFolder: the templates folder
        @return RETURN: the user data
        """
        if 'user-data' in self.keys():
            return self['user-data']
        else:
            self.hostgroup = hostgroup
            self.domain = domain
            password = self.getParamFromEnv('password', defaultPwd)
            sshauthkeys = self.getParamFromEnv('global_sshkey', defaultSshKey)
            with open(tplFolder+'puppet.conf', 'rb') as puppet_file:
                content = puppet_file.read()
                enc_puppet_file = base64.b64encode(content)
            with open(tplFolder+'cloud-init.tpl', 'r') as content_file:
                tpl = content_file.read()
                s = MyTemplate(tpl)
                if sshauthkeys:
                    sshauthkeys = ' - '+sshauthkeys
                self.userdata = s.substitute(
                    password=password,
                    fqdn=self['name'],
                    sshauthkeys=sshauthkeys,
                    foremanurlbuilt="http://foreman.{}/unattended/built"
                                    .format(self.domain['name']),
                    puppet_conf_content=enc_puppet_file.decode('utf-8'))
                return self.userdata


class MyTemplate(Template):
    delimiter = '%'
    idpattern = r'[a-z][_a-z0-9]*'

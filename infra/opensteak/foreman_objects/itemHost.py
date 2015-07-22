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

import base64
from string import Template
from opensteak.foreman_objects.item import ForemanItem
from opensteak.foreman_objects.subItemInterface import SubItemInterface
from opensteak.foreman_objects.subItemParameter import SubItemParameter
from opensteak.foreman_objects.subItemPuppetClasses import SubItemPuppetClasses
from opensteak.foreman_objects.subItemPuppetClassIds\
    import SubItemPuppetClassIds
from opensteak.foreman_objects.subDict import SubDict
from opensteak.foreman_objects.subItemSmartClassParameter\
    import SubItemSmartClassParameter


class ItemHost(ForemanItem):
    """
    ItemHost class
    Represent the content of a foreman hostgroup as a dict
    """

    objName = 'hosts'
    payloadObj = 'host'

    def enhance(self):
        """ Function enhance
        Enhance the object with new item or enhanced items
        """
        self.update({'puppetclasses':
                     SubDict(self.api, self.objName,
                             self.payloadObj, self.key,
                             SubItemPuppetClasses)})
        self.update({'parameters':
                     SubDict(self.api, self.objName,
                             self.payloadObj, self.key,
                             SubItemParameter)})
        self.update({'interfaces':
                     SubDict(self.api, self.objName,
                             self.payloadObj, self.key,
                             SubItemInterface)})
        self.update({'smart_class_parameters':
                    SubDict(self.api, self.objName,
                            self.payloadObj, self.key,
                            SubItemSmartClassParameter)})

    def __setitem__(self, key, attributes):
        """ Function __setitem__
        Set a parameter of a foreman object as a dict

        @param key: The key to modify
        @param attribute: The data
        @return RETURN: The API result
        """
        if key in ['parameters', 'interfaces', 'smart_class_parameters']:
            print('Can not assign {} directly, use .append()'.format(key))
            return False
        elif key in ['puppetclasses']:
            return ForemanItem.__setitem__(self,
                                           self[key].objType.payloadObj,
                                           attributes)
        elif key in ['power']:
            return self.api.set(self.objName,
                                '{}/{}'.format(
                                               self.key,
                                               'power'),
                                {"power_action": attributes,"host": {}})
        elif key in ['boot']:
            return self.api.set(self.objName,
                                '{}/{}'.format(
                                               self.key,
                                               'boot'),
                                {"device": attributes,"host": {}})
        else:
            return ForemanItem.__setitem__(self, key, attributes)

    def getStatus(self):
        """ Function getStatus
        Get the status of an host

        @return RETURN: The host status
        """
        return self.api.get('hosts', self.key, 'status')['status']

    def puppetRun(self):
        """ Function puppetRun
        Force puppet run on a host

        @return RETURN: The API result
        """
        return self.api.set('hosts', self.key,
                            {"host": {}},
                            'puppetrun', async=False)

    def powerOn(self):
        """ Function powerOn
        Power on a host

        @return RETURN: The API result
        """
        return self.api.set('hosts', self.key,
                            {"power_action": "start"},
                            'power', async=False)

    def getParamFromEnv(self, var, default=''):
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
                    defaultPwd='',
                    defaultSshKey='',
                    proxyHostname='',
                    tplFolder='metadata/templates/'):
        """ Function getUserData
        Generate a userdata script for metadata server from Foreman API

        @param domain: the domain item linked to this host
        @param hostgroup: the hostgroup item linked to this host
        @param defaultPwd: the default password if no password is specified
                           in the host>hostgroup>domain params
        @param defaultSshKey: the default ssh key if no password is specified
                              in the host>hostgroup>domain params
        @param proxyHostname: hostname of the smartproxy
        @param tplFolder: the templates folder
        @return RETURN: the user data
        """
        if 'user-data' in self.keys():
            return self['user-data']
        else:
            self.hostgroup = hostgroup
            self.domain = domain
            if proxyHostname == '':
                proxyHostname = 'foreman.' + domain
            password = self.getParamFromEnv('password', defaultPwd)
            sshauthkeys = self.getParamFromEnv('global_sshkey', defaultSshKey)
            with open(tplFolder+'puppet.conf', 'rb') as puppet_file:
                p = MyTemplate(puppet_file.read())
                enc_puppet_file = base64.b64encode(p.substitute(
                    foremanHostname=proxyHostname))
            with open(tplFolder+'cloud-init.tpl', 'r') as content_file:
                s = MyTemplate(content_file.read())
                if sshauthkeys:
                    sshauthkeys = ' - '+sshauthkeys
                self.userdata = s.substitute(
                    password=password,
                    fqdn=self['name'],
                    sshauthkeys=sshauthkeys,
                    foremanurlbuilt="http://{}/unattended/built"
                                    .format(proxyHostname),
                    puppet_conf_content=enc_puppet_file.decode('utf-8'))
                return self.userdata


class MyTemplate(Template):
    delimiter = '%'
    idpattern = r'[a-z][_a-z0-9]*'

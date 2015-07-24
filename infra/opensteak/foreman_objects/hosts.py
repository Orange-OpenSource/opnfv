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
from opensteak.foreman_objects.itemHost import ItemHost
import time
from pprint import pprint as pp


class Hosts(ForemanObjects):
    """
    Host sclass
    """
    objName = 'hosts'
    payloadObj = 'host'
    itemType = ItemHost

    def __printProgression__(self, status, msg, eol):
        """ Function __printProgression__
        Print the creation progression or not
        It uses the foreman.printer lib

        @param status: Status of the message
        @param msg: Message
        @param eol: End Of Line (to get a new line or not)
        @return RETURN: None
        """
        if self.printHostProgress:
            self.__printProgression__(status, msg, eol=eol)

    def createController(self, key, attributes, ipmi, printHostProgress=False):
        """ Function createController
        Create a controller node

        @param key: The host name or ID
        @param attributes:The payload of the host creation
        @param printHostProgress: The link to opensteak.printerlib
                                to print or not the
                                progression of the host creation
        @return RETURN: The API result
        """
        if key not in self:
            self.printHostProgress = printHostProgress
            self.async = False
            # Create the VM in foreman
            self.__printProgression__('In progress',
                                      key + ' creation: push in Foreman',
                                      eol='\r')
            pp(attributes)
            self.api.create('hosts', attributes, async=self.async)
            pp(self.api.__dict__)
            self[key]['interfaces'].append(ipmi)
            # Wait for puppet catalog to be applied
            # self.waitPuppetCatalogToBeApplied(key)
            self.reload()
        # self[key]['build'] = 'true'
        # self[key]['boot'] = 'pxe'
        # self[key]['power'] = 'cycle'
        return self[key]

    def waitPuppetCatalogToBeApplied(self, key, sleepTime=5):
        """ Function waitPuppetCatalogToBeApplied
        Wait for puppet catalog to be applied

        @param key: The host name or ID
        @return RETURN: None
        """
        # Wait for puppet catalog to be applied
        loop_stop = False
        while not loop_stop:
            status = self[key].getStatus()
            if status == 'No Changes' or status == 'Active':
                self.__printProgression__(True,
                                          key + ' creation: provisioning OK')
                loop_stop = True
            elif status == 'Error':
                self.__printProgression__(False,
                                          key + ' creation: Error',
                                          failed="Error during provisioning")
                loop_stop = True
                return False
            else:
                self.__printProgression__('In progress',
                                          key + ' creation: provisioning ({})'
                                          .format(status),
                                          eol='\r')
            time.sleep(sleepTime)

    def createVM(self, key, attributes, printHostProgress=False):
        """ Function createVM
        Create a Virtual Machine

        The creation of a VM with libVirt is a bit complexe.
        We first create the element in foreman, the ask to start before
        the result of the creation.
        To do so, we make async calls to the API and check the results

        @param key: The host name or ID
        @param attributes:The payload of the host creation
        @param printHostProgress: The link to opensteak.printerlib
                                to print or not the
                                progression of the host creation
        @return RETURN: The API result
        """

        self.printHostProgress = printHostProgress
        self.async = True
        # Create the VM in foreman
        self.__printProgression__('In progress',
                                  key + ' creation: push in Foreman', eol='\r')
        future1 = self.api.create('hosts', attributes, async=False)

        #  Wait before asking to power on the VM
        sleep = 5
        for i in range(0, sleep):
            time.sleep(1)
            self.__printProgression__('In progress',
                                      key + ' creation: start in {0}s'
                                      .format(sleep - i),
                                      eol='\r')

        #  Power on the VM
        self.__printProgression__('In progress',
                                  key + ' creation: starting', eol='\r')
        future2 = self[key].powerOn()

        #  Show Power on result
        if future2.result().status_code is 200:
            self.__printProgression__('In progress',
                                      key + ' creation: wait for end of boot',
                                      eol='\r')
        else:
            self.__printProgression__(False,
                                      key + ' creation: Error',
                                      failed=str(future2.result().status_code))
            return False
        #  Show creation result
        if future1.result().status_code is 200:
            self.__printProgression__('In progress',
                                      key + ' creation: created',
                                      eol='\r')
        else:
            self.__printProgression__(False,
                                      key + ' creation: Error',
                                      failed=str(future1.result().status_code))
            return False

        # Wait for puppet catalog to be applied
        self.waitPuppetCatalogToBeApplied(key)

        return self[key]['id']

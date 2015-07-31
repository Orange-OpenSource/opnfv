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
# @author: Pawel Chomicki <pawel.chomicki@nokia.com>

"""
Parse arguments from CLI
"""

import argparse

class OpenSteakArgParser:

    def __init__(self):
        """
        Parse the command line
        """
        self.parser = argparse.ArgumentParser(description='This script will create config files for a VM in current folder.', usage='%(prog)s [options] name')
        self.parser.add_argument('name', help='Set the name of the machine')
        self.parser.add_argument('-i', '--ip', help='Set the ip address of the machine. (Default is 192.168.42.42)', default='192.168.42.42')
        self.parser.add_argument('-n', '--netmask', help='Set the netmask in short format. (Default is 24)', default='24')
        self.parser.add_argument('-g', '--gateway', help='Set the gateway to ping internet. (Default is 192.168.42.1)', default='192.168.42.1')
        self.parser.add_argument('-p', '--password', help='Set the ssh password. Login is ubuntu. (Default password is moutarde)', default='moutarde')
        self.parser.add_argument('-u', '--cpu', help='Set number of CPU for the VM. (Default is 2)', default='2')
        self.parser.add_argument('-r', '--ram', help='Set quantity of RAM for the VM in kB. (Default is 2097152)', default='2097152')
        self.parser.add_argument('-o', '--iso', help='Use this iso file. (Default is trusty-server-cloudimg-amd64-disk1.img)', default='trusty-server-cloudimg-amd64-disk1.img')
        self.parser.add_argument('-d', '--disksize', help='Create a disk with that size. (Default is 5G)', default='5G')
        self.parser.add_argument('-f', '--force', help='Force creation without asking questions. This is dangerous as it will delete old VM with same name.', default=False, action='store_true')

    def parse(self):
        return self.parser.parse_args()


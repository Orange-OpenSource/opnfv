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

"""
Virsh library
"""

import subprocess
import os

class OpenSteakVirsh:

    virsh = "/usr/bin/virsh"
    genisoimage = "/usr/bin/genisoimage"
    environment = ""

    ###
    # INIT
    ###
    def __init__(self):
        self.environment = dict(os.environ)  # Copy current environment
        self.environment['LANG'] = 'en_US.UTF-8'


    ###
    # VOLUMES
    ###
    def volumeList(self, pool="default"):
        """
        Return all volumes from a pool
        """
        p = subprocess.Popen([self.virsh, "-q", "vol-list", pool], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=self.environment)
        stdout, stderr = p.communicate()

        # Split lines
        lines = stdout.splitlines()

        # Foreach line, split with space and construct a dictionnary
        newLines = {}
        for line in lines:
            name, path = line.split(maxsplit=1)
            newLines[name.strip()] = path.strip()

        return newLines

    def volumeDelete(self, path):
        """
        Delete a volume
        """
        p = subprocess.Popen([self.virsh, "-q", "vol-delete", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=self.environment)
        stdout, stderr = p.communicate()

        return {"stdout":stdout, "stderr":stderr}

    def volumeClone(self, origin, name, pool="default"):
        """
        Clone a volume
        """
        p = subprocess.Popen([self.virsh, "-q", "vol-clone", "--pool", pool, origin, name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=self.environment)
        stdout, stderr = p.communicate()

        return {"stdout":stdout, "stderr":stderr}

    def volumeResize(self, name, size, pool="default"):
        """
        Resize a volume
        """
        p = subprocess.Popen([self.virsh, "-q", "vol-resize", "--pool", pool, name, size], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=self.environment)
        stdout, stderr = p.communicate()

        return {"stdout":stdout, "stderr":stderr}

    ###
    # POOLS
    ###
    def poolRefresh(self, pool="default"):
        """
        Refresh a pool
        """
        p = subprocess.Popen([self.virsh, "-q", "pool-refresh", pool], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=self.environment)
        stdout, stderr = p.communicate()

        return {"stdout":stdout, "stderr":stderr}

    ###
    # DOMAINS
    ###
    def domainList(self):
        """
        Return all domains (VM)
        """
        p = subprocess.Popen([self.virsh, "-q", "list", "--all"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=self.environment)
        stdout, stderr = p.communicate()

        # Split lines
        lines = stdout.splitlines()

        # Foreach line, split with space and construct a dictionnary
        newLines = {}
        for line in lines:
            id, name, status = line.split(maxsplit=2)
            newLines[name.strip()] = status.strip()

        return newLines

    def domainDefine(self, xml):
        """
        Define a domain (create a VM)
        """
        p = subprocess.Popen([self.virsh, "-q", "define", xml], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=self.environment)
        stdout, stderr = p.communicate()

        return {"stdout":stdout, "stderr":stderr}

    def domainUndefine(self, name):
        """
        Undefine a domain (delete a VM)
        """
        p = subprocess.Popen([self.virsh, "-q", "undefine", name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=self.environment)
        stdout, stderr = p.communicate()

        return {"stdout":stdout, "stderr":stderr}

    def domainStart(self, name):
        """
        Define a domain (create a VM)
        """
        p = subprocess.Popen([self.virsh, "-q", "start", name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=self.environment)
        stdout, stderr = p.communicate()

        return {"stdout":stdout, "stderr":stderr}

    def domainDestroy(self, name):
        """
        Destroy a domain (stop a VM)
        """
        p = subprocess.Popen([self.virsh, "-q", "destroy", name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=self.environment)
        stdout, stderr = p.communicate()

        return {"stdout":stdout, "stderr":stderr}

    ###
    # ISO
    ###
    def generateConfiguration(self, name, files):
        """
        Generate an ISO file
        """

        commandArray = [self.genisoimage, "-quiet", "-o", "/var/lib/libvirt/images/{0}-configuration.iso".format(name), "-volid", "cidata", "-joliet", "-rock"]
        for k, f in files.items():
            commandArray.append(f)

        # Generate the iso file
        p = subprocess.Popen(commandArray, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=self.environment)
        stdout, stderr = p.communicate()

        return {"stdout":stdout, "stderr":stderr}


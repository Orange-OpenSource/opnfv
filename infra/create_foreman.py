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
#     Arnaud Morin <arnaud1.morin@orange.com>
#     David Blaisonneau <david.blaisonneau@orange.com>

"""
Create Virtual Machines
"""

# TODO: be sure that we are runnning as root

from opensteak.conf import OpenSteakConfig
from opensteak.printer import OpenSteakPrinter
#from opensteak.argparser import OpenSteakArgParser
from opensteak.templateparser import OpenSteakTemplateParser
from opensteak.virsh import OpenSteakVirsh
from pprint import pprint as pp
from ipaddress import IPv4Address
import tempfile
import shutil
import os
import sys

p = OpenSteakPrinter()

## Validate the paramters
p.header("Check parameters")

# Deprecated way, with OpenSteakArgParser
#OpenSteakArgParser = OpenSteakArgParser()
#args = vars(OpenSteakArgParser.parse())

# Get the parameters from YAML file
OpenSteakConfig = OpenSteakConfig(config_file = "./config/infra.yaml")
#pp(OpenSteakConfig.dump())

args = {}
args["name"] = "foreman"
args["ip"] = OpenSteakConfig["foreman"]["ip"]
args["netmask"] = OpenSteakConfig["subnets"]["Admin"]["data"]["mask"]
args["netmaskshort"] = sum([bin(int(x)).count('1') for x in OpenSteakConfig["subnets"]["Admin"]["data"]["mask"].split('.')])
args["gateway"] = OpenSteakConfig["subnets"]["Admin"]["data"]["gateway"]
args["network"] = OpenSteakConfig["subnets"]["Admin"]["data"]["network"]
args["password"] = OpenSteakConfig["foreman"]["password"]
args["cpu"] = OpenSteakConfig["foreman"]["cpu"]
args["ram"] = OpenSteakConfig["foreman"]["ram"]
args["iso"] = OpenSteakConfig["foreman"]["iso"]
args["disksize"] = OpenSteakConfig["foreman"]["disksize"]
args["force"] = OpenSteakConfig["foreman"]["force"]
args["dhcprange"] = "{0} {1}".format(OpenSteakConfig["subnets"]["Admin"]["data"]["from"], OpenSteakConfig["subnets"]["Admin"]["data"]["to"])
args["domain"] = OpenSteakConfig["domains"]
reverse_octets = str(OpenSteakConfig["foreman"]["ip"]).split('.')[-2::-1]
args["reversedns"] = '.'.join(reverse_octets) + '.in-addr.arpa'
args["dns"] = OpenSteakConfig["foreman"]["dns"]
args["bridge"] = OpenSteakConfig["foreman"]["bridge"]
if OpenSteakConfig["foreman"]["bridge_type"] == "openvswitch":
    args["bridgeconfig"] = "<virtualport type='openvswitch'></virtualport>"
else
    # no specific config for linuxbridge
    args["bridgeconfig"] = ""

p.list_id(args)

# Ask confirmation
if args["force"] != True: p.ask_validation()

# Create the VM
p.header("Initiate configuration")

###
# Work on templates
###
# Create temporary folders and files
tempFolder = tempfile.mkdtemp(dir="/tmp")
tempFiles = {}

for f in os.listdir("templates_foreman/"):
    tempFiles[f] = "{0}/{1}".format(tempFolder,f)
    try:
        OpenSteakTemplateParser("templates_foreman/{0}".format(f), tempFiles[f], args)
    except Exception as err:
        p.status(False, msg="Something went wrong when trying to create the file {0} from the template templates_foreman/{1}".format(tempFiles[f],f), failed="{0}".format(err))

###
# Work on files
###
for f in os.listdir("files_foreman/"):
    tempFiles[f] = "{0}/{1}".format(tempFolder,f)
    shutil.copyfile("files_foreman/{0}".format(f),tempFiles[f])

p.status(True, msg="Temporary files created:")
p.list_id(tempFiles)


###
# Delete if already exists
###

# Get all volumes and VM
p.header("Virsh calls")
OpenSteakVirsh = OpenSteakVirsh()
volumeList = OpenSteakVirsh.volumeList()
domainList = OpenSteakVirsh.domainList()
#p.list_id(volumeList)
#p.list_id(domainList)

# TODO: check that the default image is in the list (trusty-server-cloudimg-amd64-disk1.img by default)

# Delete the volume if exists
try:
    oldVolume = volumeList[args["name"]]
    
    # Ask confirmation
    if args["force"] != True: p.ask_validation()
    
    status = OpenSteakVirsh.volumeDelete(volumeList[args["name"]])
    if (status["stderr"]):
        p.status(False, msg=status["stderr"])
    p.status(True, msg=status["stdout"])
except KeyError as err:
    # no old volume, do nothing
    pass

# Delete the VM if exists
try:
    vmStatus = domainList[args["name"]]
    
    # Ask confirmation
    if args["force"] != True: p.ask_validation()
    
    # Destroy (stop)
    if vmStatus == "running":
        status = OpenSteakVirsh.domainDestroy(args["name"])
        if (status["stderr"]):
            p.status(False,msg=status["stderr"])
        p.status(True, msg=status["stdout"])
    
    # Undefine (delete)
    status = OpenSteakVirsh.domainUndefine(args["name"])
    if (status["stderr"]):
        p.status(False, msg=status["stderr"])
    p.status(True, msg=status["stdout"])
except KeyError as err:
    # no old VM defined, do nothing
    pass

###
# Create the configuration image file from metadata and userdata
###
status = OpenSteakVirsh.generateConfiguration(args["name"], tempFiles)
if (status["stderr"]):
    p.status(False,msg=status["stderr"])
p.status(True, msg="Configuration generated successfully in /var/lib/libvirt/images/{0}-configuration.iso".format(args["name"]))

# Refresh the pool
status = OpenSteakVirsh.poolRefresh()
if (status["stderr"]):
    p.status(False,msg=status["stderr"])
p.status(True, msg=status["stdout"])

###
# Create the new VM
###
# Create the volume from a clone
status = OpenSteakVirsh.volumeClone(args["iso"], args["name"])
if (status["stderr"]):
    p.status(False,msg=status["stderr"])
p.status(True, msg=status["stdout"])

# Resize the volume
status = OpenSteakVirsh.volumeResize(args["name"], args["disksize"])
if (status["stderr"]):
    p.status(False,msg=status["stderr"])
p.status(True, msg=status["stdout"])

# Create the VM
status = OpenSteakVirsh.domainDefine(tempFiles["kvm-config"])
if (status["stderr"]):
    p.status(False,msg=status["stderr"])
p.status(True, msg=status["stdout"])


###
# Start the VM
###
status = OpenSteakVirsh.domainStart(args["name"])
if (status["stderr"]):
    p.status(False,msg=status["stderr"])
p.status(True, msg=status["stdout"])

p.status(True, msg="Log file is at: /var/log/libvirt/qemu/{0}-serial.log".format(args["name"]))

p.header("fini")

# Delete temporary dir
shutil.rmtree(tempFolder)


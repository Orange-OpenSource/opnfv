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
Create Virtual Machines
"""

# TODO: be sure that we are runnning as root

from opensteak.conf import OpenSteakConfig
from opensteak.printer import OpenSteakPrinter
# from opensteak.argparser import OpenSteakArgParser
from opensteak.templateparser import OpenSteakTemplateParser
from opensteak.virsh import OpenSteakVirsh
from pprint import pprint as pp
# from ipaddress import IPv4Address
import argparse
import tempfile
import shutil
import os
# import sys

p = OpenSteakPrinter()

#
# Check for params
#
p.header("Check parameters")
args = {}

# Update args with values from CLI
parser = argparse.ArgumentParser(description='This script will create a foreman VM.', usage='%(prog)s [options]')
parser.add_argument('-c', '--config', help='YAML config file to use (default is config/infra.yaml).', default='config/infra.yaml')
args.update(vars(parser.parse_args()))

# Open config file
conf = OpenSteakConfig(config_file=args["config"])
# pp(conf.dump())

a = {}
a["name"] = "foreman"
a["ip"] = conf["foreman"]["ip"]
a["netmask"] = conf["subnets"]["Admin"]["data"]["mask"]
a["netmaskshort"] = sum([bin(int(x)).count('1')
                            for x in conf["subnets"]["Admin"]
                                                    ["data"]["mask"]
                            .split('.')])
a["gateway"] = conf["subnets"]["Admin"]["data"]["gateway"]
a["network"] = conf["subnets"]["Admin"]["data"]["network"]
a["admin"] = conf["foreman"]["admin"]
a["password"] = conf["foreman"]["password"]
a["cpu"] = conf["foreman"]["cpu"]
a["ram"] = conf["foreman"]["ram"]
a["iso"] = conf["foreman"]["iso"]
a["disksize"] = conf["foreman"]["disksize"]
a["force"] = conf["foreman"]["force"]
a["dhcprange"] = "{0} {1}".format(conf["subnets"]["Admin"]
                                                    ["data"]["from"],
                                     conf["subnets"]["Admin"]
                                                    ["data"]["to"])
a["domain"] = conf["domains"]
reverse_octets = str(conf["foreman"]["ip"]).split('.')[-2::-1]
a["reversedns"] = '.'.join(reverse_octets) + '.in-addr.arpa'
a["dns"] = conf["foreman"]["dns"]
a["bridge"] = conf["foreman"]["bridge"]
if conf["foreman"]["bridge_type"] == "openvswitch":
    a["bridgeconfig"] = "<virtualport type='openvswitch'></virtualport>"
else:
    # no specific config for linuxbridge
    a["bridgeconfig"] = ""

# Update args with values from config file
args.update(a)
del a

p.list_id(args)

# Ask confirmation
if args["force"] is not True:
    p.ask_validation()

# Create the VM
p.header("Initiate configuration")

###
# Work on templates
###
# Create temporary folders and files
tempFolder = tempfile.mkdtemp(dir="/tmp")
tempFiles = {}

for f in os.listdir("templates_foreman/"):
    tempFiles[f] = "{0}/{1}".format(tempFolder, f)
    try:
        OpenSteakTemplateParser("templates_foreman/{0}".format(f),
                                tempFiles[f], args)
    except Exception as err:
        p.status(False, msg=("Something went wrong when trying to create "
                             "the file {0} from the template "
                             "templates_foreman/{1}").format(tempFiles[f], f),
                 failed="{0}".format(err))

###
# Work on files
###
for f in os.listdir("files_foreman/"):
    tempFiles[f] = "{0}/{1}".format(tempFolder, f)
    shutil.copyfile("files_foreman/{0}".format(f), tempFiles[f])

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
# p.list_id(volumeList)
# p.list_id(domainList)

# TODO: check that the default image is in the list
# (trusty-server-cloudimg-amd64-disk1.img by default)

# Delete the volume if exists
try:
    oldVolume = volumeList[args["name"]]

    # Ask confirmation
    if args["force"] is not True:
        p.ask_validation()

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
    if args["force"] is not True:
        p.ask_validation()

    # Destroy (stop)
    if vmStatus == "running":
        status = OpenSteakVirsh.domainDestroy(args["name"])
        if (status["stderr"]):
            p.status(False, msg=status["stderr"])
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
    p.status(False, msg=status["stderr"])
p.status(True, msg=("Configuration generated successfully in "
                    "/var/lib/libvirt/images/{0}-configuration.iso")
         .format(args["name"]))

# Refresh the pool
status = OpenSteakVirsh.poolRefresh()
if (status["stderr"]):
    p.status(False, msg=status["stderr"])
p.status(True, msg=status["stdout"])

###
# Create the new VM
###
# Create the volume from a clone
status = OpenSteakVirsh.volumeClone(args["iso"], args["name"])
if (status["stderr"]):
    p.status(False, msg=status["stderr"])
p.status(True, msg=status["stdout"])

# Resize the volume
status = OpenSteakVirsh.volumeResize(args["name"], args["disksize"])
if (status["stderr"]):
    p.status(False, msg=status["stderr"])
p.status(True, msg=status["stdout"])

# Create the VM
status = OpenSteakVirsh.domainDefine(tempFiles["kvm-config"])
if (status["stderr"]):
    p.status(False, msg=status["stderr"])
p.status(True, msg=status["stdout"])


###
# Start the VM
###
status = OpenSteakVirsh.domainStart(args["name"])
if (status["stderr"]):
    p.status(False, msg=status["stderr"])
p.status(True, msg=status["stdout"])

p.status(True, msg="Log file is at: /var/log/libvirt/qemu/{0}-serial.log"
                   .format(args["name"]))

p.header("fini")

# Delete temporary dir
shutil.rmtree(tempFolder)

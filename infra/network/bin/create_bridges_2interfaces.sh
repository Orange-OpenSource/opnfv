#!/bin/bash
##--------------------------------------------------------
# Copyright 2014 - 2015 Orange
#
# Licensed under the Apache License, Version 2.0 (the License);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# or see the LICENSE file for more details.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors     : Arnaud Morin <arnaud1.morin@orange.com>
#               David Blaisonneau <david.blaisonneau@orange.com>
#
#--------------------------------------------------------
# History
#
# 1.0.0 - 2015-01-27 : Release of the file
##

# Import local functions
. $( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/functions.inc.sh
eval $CHECKRESULT
eval $COLORED_ECHO
export -f checkResult
export -f echo_green
export -f echo_red
export -f echo_yellow

## Bridges
echo -n "Check if br-int exists... "
ovs-vsctl br-exists br-int
if [ $? -ne 0 ]; then
    echo_yellow '[NO] - add it'
    ovs-vsctl add-br br-int
else
    echo_green '[YES]'
fi

echo -n "Check if br-vm exists... "
ovs-vsctl br-exists br-vm
if [ $? -ne 0 ]; then
    echo_yellow '[NO] - add it'
    ovs-vsctl add-br br-vm
else
    echo_green '[YES]'
fi

echo -n "Check if br-adm exists... "
ovs-vsctl br-exists br-adm
if [ $? -ne 0 ]; then
    echo_yellow '[NO] - add it'
    ovs-vsctl add-br br-adm
else
    echo_green '[YES]'
fi

echo -n "Check if br-storage exists... "
ovs-vsctl br-exists br-storage
if [ $? -ne 0 ]; then
    echo_yellow '[NO] - add it'
    ovs-vsctl add-br br-storage
else
    echo_green '[YES]'
fi

## Ports
echo -n "Check if eth0 is in br-adm... "
PORT=$(ovs-vsctl list-ports br-adm |egrep "^eth0$")
if [ "Z$PORT" = "Z" ]; then
    echo_yellow '[NO] - add it'
    ovs-vsctl add-port br-adm eth0
else
    echo_green '[YES]'
fi

echo -n "Check if eth1 is in br-vm... "
PORT=$(ovs-vsctl list-ports br-vm |egrep "^eth1$")
if [ "Z$PORT" = "Z" ]; then
    echo_yellow '[NO] - add it'
    ovs-vsctl add-port br-vm eth1
else
    echo_green '[YES]'
fi

echo -n "Check if veth-storage0 and veth-storage1 exists... "
PORT=$(ip link show veth-storage0)
if [ $? -ne 0 ]; then
    echo_yellow '[NO] - add it'
    ip link add name veth-storage0 type veth peer name veth-storage1
    ovs-vsctl add-port br-storage veth-storage0
    ovs-vsctl add-port br-adm veth-storage1 tag=600
else
    echo_green '[YES]'
fi

echo -n "Check if veth-storage0 and veth-storage1 are up... "
PORT=$(ip link show veth-storage0 up |egrep "^veth-storage0$")
if [ $? -ne 0 ]; then
    echo_yellow '[NO] - do it'
    ip link set veth-storage0 up
    ip link set veth-storage1 up
else
    echo_green '[YES]'
fi

echo -n "Check if veth-storage0 is in br-storage... "
PORT=$(ovs-vsctl list-ports br-storage |egrep "^veth-storage0$")
if [ $? -ne 0 ]; then
    echo_yellow '[NO] - add it'
    ovs-vsctl add-port br-storage veth-storage0
else
    echo_green '[YES]'
fi

echo -n "Check if veth-storage1 is in br-adm... "
PORT=$(ovs-vsctl list-ports br-adm |egrep "^veth-storage1$")
if [ $? -ne 0 ]; then
    echo_yellow '[NO] - add it'
    ovs-vsctl add-port br-adm veth-storage1 tag=600
else
    echo_green '[YES]'
fi

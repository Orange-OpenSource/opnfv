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

echo -n "Check if br-ex exists... "
ovs-vsctl br-exists br-ex
if [ $? -ne 0 ]; then
    echo_yellow '[NO] - add it'
    ovs-vsctl add-br br-ex
else
    echo_green '[YES]'
fi

## Ports
echo -n "Check if em2 is in br-ex... "
PORT=$(ovs-vsctl list-ports br-ex |egrep "^em2$")
if [ "Z$PORT" = "Z" ]; then
    echo_yellow '[NO] - add it'
    ovs-vsctl add-port br-ex em2
else
    echo_green '[YES]'
fi

echo -n "Check if em3 is in br-adm... "
PORT=$(ovs-vsctl list-ports br-adm |egrep "^em3$")
if [ "Z$PORT" = "Z" ]; then
    echo_yellow '[NO] - add it'
    ovs-vsctl add-port br-adm em3
else
    echo_green '[YES]'
fi

echo -n "Check if em4 is in br-storage... "
PORT=$(ovs-vsctl list-ports br-storage |egrep "^em4$")
if [ "Z$PORT" = "Z" ]; then
    echo_yellow '[NO] - add it'
    ovs-vsctl add-port br-storage em4
else
    echo_green '[YES]'
fi

echo -n "Check if em5 is in br-vm... "
PORT=$(ovs-vsctl list-ports br-vm |egrep "^em5$")
if [ "Z$PORT" = "Z" ]; then
    echo_yellow '[NO] - add it'
    ovs-vsctl add-port br-vm em5
else
    echo_green '[YES]'
fi


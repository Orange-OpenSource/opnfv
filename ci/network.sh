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
# 1.0.0 - 2015-03-17 : Release of the file
##

ifdown eth0
ifdown eth1
ifdown eth3

cat <<EOF > /etc/network/interfaces
auto lo
iface lo inet loopback

source /etc/network/interfaces.d/*.cfg
EOF

cat <<EOF > /etc/network/interfaces.d/eth.cfg
auto eth0
iface eth0 inet manual
    up ip address add 0/0 dev \$IFACE
    up ip link set \$IFACE up
    down ip link set \$IFACE down

auto eth1
iface eth1 inet manual
    up ip address add 0/0 dev \$IFACE
    up ip link set \$IFACE up
    down ip link set \$IFACE down

auto eth3
iface eth3 inet manual
    up ip address add 0/0 dev \$IFACE
    up ip link set \$IFACE up
    down ip link set \$IFACE down
EOF

cat <<EOF > /etc/network/interfaces.d/bridges.cfg
# The br-adm network interface
auto br-adm
iface br-adm inet static
    address 192.168.1.98
    netmask 24
    network 192.168.1.0
    broadcast 192.168.1.255
    gateway 192.168.1.1
    dns-nameservers 192.168.1.201 8.8.8.8
    dns-search stack2.opensteak.fr
EOF

ovs-vsctl add-br br-int
ovs-vsctl add-br br-vm
ovs-vsctl add-br br-adm
ovs-vsctl add-br br-ex

ovs-vsctl add-port br-ex eth0
ovs-vsctl add-port br-adm eth1
ovs-vsctl add-port br-vm eth3

ifup eth0
ifup eth1
ifup eth3
ifdown br-adm && ifup br-adm
ifdown br-vm && ifup br-vm
service openvswitch-switch restart


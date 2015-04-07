#!/bin/bash
#
# Copyright (C) 2015 Orange Labs
# 
# This software is distributed under the terms and conditions of the 'Apache-2.0'
# license which can be found in the file 'LICENSE.txt' in this package distribution 
# or at 'http://www.apache.org/licenses/LICENSE-2.0'. 
#
# Authors: Arnaud Morin <arnaud1.morin@orange.com> 
#          David Blaisonneau <david.blaisonneau@orange.com>
#

# Script name
PRGNAME=$(basename $0)

# Root folder
ROOT=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

#################################################
# Usage
#################################################
function usage() {

    cat << EOF >&1
Usage: $PRGNAME [options]

Description: This script will create config files for a VM in 
             current folder

Options:
    --help, -h
        Print this help and exit.

    --network-script, -n
        Name of the network script to use in order to configure network
        on this machine. Network won't be configured is this script is 
        not provided.
        
EOF
    echo -n '0'
    exit 0
}

#################################################
# Get Args
#################################################

# Command line argument parsing, the allowed arguments are
# alphabetically listed, keep it this way please.
LOPT="help,network-script:"
SOPT="hn:"

# Note that we use `"$@"' to let each command-line parameter expand to a
# separate word. The quotes around `$@' are essential!
# We need TEMP as the `eval set --' would nuke the return value of getopt.
TEMP=$(getopt --options=$SOPT --long $LOPT -n $PRGNAME -- "$@")

if [[ $? -ne 0 ]]; then
    echo "Error while parsing command line args. Exiting..." >&2
    exit 1
fi
# Note the quotes around `$TEMP': they are essential!
eval set -- "$TEMP"

while true; do
  case $1 in
    --help|-h)
                        usage
                        exit 0
                        ;;
    --network-script|-n)
                        NETWORK_SCRIPT=$2; shift
                        ;;
    --)
                        shift
                        break
                        ;;
    *)
                        echo "Unknow argument \"$1\"" >&2
                        exit 1
                        ;;
  esac
  shift
done

#################################################
# Check args
#################################################

# Placeholder


#################################################
# Do the work
#################################################

# Non interactive
export DEBIAN_FRONTEND=noninteractive

# Base
if [ ! -e puppetlabs-release-trusty.deb ] ; then
    wget https://apt.puppetlabs.com/puppetlabs-release-trusty.deb
    dpkg -i puppetlabs-release-trusty.deb
    apt-get -y update
    apt-get -y upgrade
    apt-get -y dist-upgrade
    apt-get -y install vim git hiera ntp virtinst genisoimage curl qemu-system-x86 qemu-system-common qemu-keymaps ipxe-qemu openvswitch-switch puppet
    service ntp restart
    service libvirt-bin restart
fi

# Clone OpenSteak
if [ ! -d /usr/local/opensteak ] ; then
    cd /usr/local
    git clone https://github.com/Orange-OpenSource/opnfv.git opensteak
else
    cd /usr/local/opensteak/
    git pull
fi

# Get config
# Those files are built from templates available at:
# /usr/local/opensteak/infra/config/common.yaml.tpl
# /usr/local/opensteak/infra/config/physical-nodes.yaml.tpl
cp $ROOT/*.yaml /usr/local/opensteak/infra/config/

# Create default virsh pool
virsh pool-info default >/dev/null 2>&1
if [ $? -ne 0 ] ; then
    cd /usr/local/opensteak/infra/kvm/
    virsh pool-create default_pool.xml
fi

# Create binaries
cp /usr/local/opensteak/infra/kvm/bin/* /usr/local/bin/
chmod +x /usr/local/bin/opensteak*

# Configure networking
if [ "Z" != "Z$NETWORK_SCRIPT" ]; then
    bash $ROOT/$NETWORK_SCRIPT
fi

# Get ubuntu trusty cloud image
if [ ! -e /var/lib/libvirt/images/trusty-server-cloudimg-amd64-disk1.img ] ; then
    cd /var/lib/libvirt/images
    wget 'https://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-amd64-disk1.img'
    virsh pool-refresh default
fi

# Install controllers
cd /usr/local/opensteak/infra/kvm/vm_configs
opensteak-create-vm --name puppet --cloud-init puppet-master --force
opensteak-create-vm --name dns --cloud-init dns --force
opensteak-create-vm --name rabbitmq1 --force
opensteak-create-vm --name mysql1 --force
opensteak-create-vm --name keystone1 --force
opensteak-create-vm --name glance1 --force
opensteak-create-vm --name nova1 --force
opensteak-create-vm --name neutron1 --force
opensteak-create-vm --name cinder1 --force

# Install compute & network
puppet agent -t -v


exit 0

# Test
# To be done from keystone machine
source os-creds-admin
keystone service-list
openstack compute service list
openstack extension list --network -c Name -c Alias
neutron agent-list
neutron net-create Externe --router:external --provider:physical_network physnet-ex --provider:network_type flat
neutron subnet-create Externe --name "161.105.252.0/24" --allocation-pool start=161.105.252.107,end=161.105.252.108 --disable-dhcp --gateway 161.105.252.1 161.105.252.0/24
neutron net-create demo
neutron subnet-create demo --name "192.168.42.0/24" --gateway 192.168.42.1 192.168.42.0/24
neutron router-create demo-router
neutron router-gateway-set demo-router Externe
neutron router-interface-add demo-router "192.168.42.0/24"
neutron security-group-rule-create --protocol icmp --direction ingress default
neutron security-group-rule-create --protocol icmp --direction egress default
neutron security-group-rule-create --protocol tcp --port-range-min 1 --port-range-max 65000 --direction ingress default
neutron security-group-rule-create --protocol tcp --port-range-min 1 --port-range-max 65000 --direction egress default
neutron security-group-rule-create --protocol udp --port-range-min 1 --port-range-max 65000 --direction ingress default
neutron security-group-rule-create --protocol udp --port-range-min 1 --port-range-max 65000 --direction egress default
wget https://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-amd64-disk1.img
glance image-create \
 --name "Ubuntu 14.04.1 LTS" \
 --file trusty-server-cloudimg-amd64-disk1.img \
 --disk-format qcow2 \
 --container-format bare \
 --is-public True \
 --progress
glance image-list
ssh-keygen
openstack keypair create --public-key /root/.ssh/id_rsa.pub demo-key
NETID=$(neutron net-show demo | grep ' id ' | tr '|' ' ' | awk '{print $2}')
openstack server create --flavor m1.small --image "Ubuntu 14.04.1 LTS" --nic net-id=$NETID --security-group default --key-name demo-key demo-instance1
openstack server list
neutron floatingip-create Externe
nova floating-ip-associate demo-instance1 161.105.252.108
ssh -i .ssh/id_rsa ubuntu@161.105.252.108

# Uninstall
#virsh destroy cinder1
#virsh destroy neutron1/
#virsh destroy neutron1
#virsh destroy nova1
#virsh destroy glance1/
#virsh destroy glance1
#virsh destroy keystone1
#virsh destroy mysql1
#virsh destroy rabbitmq1
#virsh destroy dns
#virsh destroy puppet
#virsh undefine cinder1
#virsh undefine neutron1
#virsh undefine nova1
#virsh undefine glance1
#virsh undefine keystone1
#virsh undefine mysql1
#virsh undefine rabbitmq1
#virsh undefine dns
#virsh undefine puppet


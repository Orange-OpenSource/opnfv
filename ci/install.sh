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
LOPT="help,network-script"
SOPT="hn"

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
# Those files are built from templates one:
# /usr/local/opensteak/infra/config/common.yaml.tpl
# /usr/local/opensteak/infra/config/physical-nodes.yaml.tpl
cd /usr/local/opensteak/infra/config
wget "https://gist.githubusercontent.com/arnaudmorinol/408b8c829aafce91deba/raw/181f60111a8234e88cae96fd5dc7d3c8391ef92c/common.yaml"
wget "https://gist.githubusercontent.com/arnaudmorinol/5abc1e869eba97663ecf/raw/0b1bfcc9a280531634921e6623a6b88c3433650c/physical-nodes.yaml"

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


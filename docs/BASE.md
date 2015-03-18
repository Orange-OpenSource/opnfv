<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Base infra install](#base-infra-install)
  - [Dependencies](#dependencies)
  - [ Clone this repo](#clone-this-repo)
  - [ Create config file from template](#create-config-file-from-template)
  - [Libvirt default pool](#libvirt-default-pool)
  - [ Import binaries](#import-binaries)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Base infra install
Being here, we suppose that you already have an Ubuntu 14.04 server up and running.

## Dependencies

As **root**, run:

```bash
wget https://apt.puppetlabs.com/puppetlabs-release-trusty.deb
dpkg -i puppetlabs-release-trusty.deb
apt-get update
apt-get upgrade
apt-get dist-upgrade
apt-get install vim git hiera ntp virtinst genisoimage curl qemu-system-x86 qemu-system-common qemu-keymaps ipxe-qemu openvswitch-switch puppet
service ntp restart
service libvirt-bin restart
```

## Clone this repo

We expect you to clone this repo in /usr/local/ folder as most of the time, the script will try to find necessary files from this folder.

```bash
cd /usr/local
git clone https://github.com/Orange-OpenSource/opnfv.git opensteak
```

## Create config file from template

The common.yaml file is the only file that you should tweak in order to setup your OpenSteak installation.

```bash
cp /usr/local/opensteak/infra/config/common.yaml.tpl /usr/local/opensteak/infra/config/common.yaml
vim /usr/local/opensteak/infra/config/common.yaml
```

## Libvirt default pool
Libvirt needs a pool to store virtual machines:

```bash
cd /usr/local/opensteak/infra/kvm/
virsh pool-create default_pool.xml
```

## Import binaries
To help deploy future controller VM:

```bash
cp bin/* /usr/local/bin/
chmod +x /usr/local/bin/opensteak*
```

This will create at least the opensteak-create-vm script. This script will help you create automatically OpenSteak VM.

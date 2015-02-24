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
apt-get install vim git hiera ntp virtinst genisoimage curl qemu-system-x86 qemu-system-common qemu-keymaps ipxe-qemu openvswitch-switch
service ntp restart
service libvirt-bin restart
```

## Clone this repo

```bash
cd /usr/local
git clone https://github.com/Orange-OpenSource/opnfv.git opensteak
```

## Create config file from template

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

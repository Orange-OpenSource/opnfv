<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Controllers VM installation](#controllers-vm-installation)
  - [Puppet master](#puppet-master)
  - [DNS](#dns)
  - [RabbitMQ](#rabbitmq)
  - [MySQL](#mysql)
  - [Keystone](#keystone)
  - [Glance](#glance)
    - [With Ceph](#with-ceph)
      - [Convert from qcow2 to raw](#convert-from-qcow2-to-raw)
      - [Upload to glance](#upload-to-glance)
  - [Nova (controller part)](#nova-controller-part)
  - [Neutron (controller part)](#neutron-controller-part)
  - [Cinder](#cinder)
- [Move a VM](#move-a-vm)
  - [Shutdown VM on host A](#shutdown-vm-on-host-a)
  - [ Create the VM on host B (new host)](#create-the-vm-on-host-b-new-host)
  - [Start the VM](#start-the-vm)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Controllers VM installation

Each controller part of OpenStack is installed in a KVM based virtual machine.

```bash
cd /usr/local/opensteak/infra/kvm/vm_configs
```

## Puppet master

This is the first machine that we install, as it contains all the configuration for others machines.

To create the machine, run:

```bash
opensteak-create-vm --name puppet --cloud-init puppet-master -c
```

It should configure itself by grabbing the *common.yaml* file from */usr/local/opensteak/infra/config/common.yaml*

r10k will also update all the puppet modules that will be needed

## DNS

```bash
opensteak-create-vm --name dns --cloud-init dns -c
```

## RabbitMQ

```bash
opensteak-create-vm --name rabbitmq -c
```

## MySQL

```bash
opensteak-create-vm --name mysql -c
```

Check that it listen on 0.0.0.0:3306 port correctly:

```bash
netstat -laputen |grep 3306
```

You can connect over mysql with: (password is defined in your common.yaml file)

```bash
mysql -u root -p
```

## Keystone

```bash
opensteak-create-vm --name keystone -c
```

Test if it works well with (ssh on VM before):

```bash
cd /root
source os-creds-admin
keystone service-list
```

You should have:

```bash
+----------------------------------+----------+-----------+------------------------------+
|                id                |   name   |    type   |         description          |
+----------------------------------+----------+-----------+------------------------------+
| aff808b962074b989a9ccc61c4aa6acb |  glance  |   image   |   Openstack Image Service    |
| 4c535dbd4d134c829ba1c1710c1c148e | keystone |  identity |  OpenStack Identity Service  |
| 05f8d1c690bf4894b761e95ef1ba9ce8 | neutron  |  network  |  Neutron Networking Service  |
| 1cb4f7b5d6e34e5f90d86d7a59f636aa |   nova   |  compute  |  Openstack Compute Service   |
| 578a642af4a74e3cac03e58a579691e0 | nova_ec2 |    ec2    |         EC2 Service          |
| 1ca23d8f2d2c44ce8f96a66cb384d19b |  novav3  | computev3 | Openstack Compute Service v3 |
+----------------------------------+----------+-----------+------------------------------+
```

## Glance

```bash
opensteak-create-vm --name glance --storage -c
```

In our lab, this machine needs a specific connection to the storage network in order to mount an NFS folder in /var/lib/images (to store the glance images).

If you don't need that, you won't need the *--storage* option. You will also have to comment out some NFS related block in the manifest file corresponding to glance (https://github.com/Orange-OpenSource/opnfv-puppet/blob/production/manifests/glance.pp)

from keystone node:
```bash
root@keystone:~# cd /root
root@keystone:/root# source os-creds-admin
root@keystone:/root# glance image-list
+--------------------------------------+--------------+-------------+------------------+----------+--------+
| ID                                   | Name         | Disk Format | Container Format | Size     | Status |
+--------------------------------------+--------------+-------------+------------------+----------+--------+
+--------------------------------------+--------------+-------------+------------------+----------+--------+
root@keystone:/root# mkdir images && cd images
root@keystone:/root/images# wget http://cdn.download.cirros-cloud.net/0.3.3/cirros-0.3.3-x86_64-disk.img
root@keystone:/root/images# glance image-create \
 --name "cirros-0.3.3-x86_64" \
 --file cirros-0.3.3-x86_64-disk.img \
--disk-format qcow2 \
--container-format bare \
--is-public True \
--progress
+------------------+--------------------------------------+
| Property         | Value                                |
+------------------+--------------------------------------+
[...]
root@keystone:/root/images# glance image-list
root@keystone:/root/images# wget https://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-amd64-disk1.img
root@keystone:/root/images# glance image-create \
 --name "Ubuntu 14.04.1 LTS" \
 --file trusty-server-cloudimg-amd64-disk1.img \
--disk-format qcow2 \
--container-format bare \
--is-public True \
--progress
root@keystone:/root/images# glance image-list
+--------------------------------------+--------------------+-------------+------------------+-----------+--------+
| ID                                   | Name               | Disk Format | Container Format | Size      | Status |
+--------------------------------------+--------------------+-------------+------------------+-----------+--------+
| 5d01c794-d63a-43e2-a356-3d0912b6b046 | CirrOS 0.3.1       | qcow2       | bare             | 13147648  | active |
| 92ad5e49-12fa-4d29-8a7a-c7dea05823cd | Ubuntu 14.04.1 LTS | qcow2       | bare             | 267452928 | active |
+--------------------------------------+--------------------+-------------+------------------+-----------+--------+


```

### With Ceph
When ceph is installed as a backend for Glance, you must upload image in raw format instead of qcow2:

#### Convert from qcow2 to raw

```bash
qemu-img convert -f qcow2 -O raw trusty-server-cloudimg-amd64-disk1.img trusty-server-cloudimg-amd64-disk1.raw
```

#### Upload to glance

```bash
glance image-create  --name "ubuntu-14-10-64b-test"  --file trusty-server-cloudimg-amd64-disk1.raw --disk-format raw --container-format bare --is-public True --progress
```

## Nova (controller part)

```bash
opensteak-create-vm --name nova -c
```

Test if it works well from keystone:

```bash
cd /root
source os-creds-admin
openstack
(openstack) compute service list
+------------------+------+----------+---------+-------+----------------------------+
| Binary           | Host | Zone     | Status  | State | Updated At                 |
+------------------+------+----------+---------+-------+----------------------------+
| nova-consoleauth | nova | internal | enabled | up    | 2015-02-20T09:21:18.000000 |
| nova-scheduler   | nova | internal | enabled | up    | 2015-02-20T09:17:44.000000 |
| nova-conductor   | nova | internal | enabled | up    | 2015-02-20T09:18:28.000000 |
| nova-cert        | nova | internal | enabled | up    | 2015-02-20T09:21:18.000000 |
+------------------+------+----------+---------+-------+----------------------------+
(openstack) host list
+-----------+-------------+----------+
| Host Name | Service     | Zone     |
+-----------+-------------+----------+
| nova      | consoleauth | internal |
| nova      | scheduler   | internal |
| nova      | conductor   | internal |
| nova      | cert        | internal |
+-----------+-------------+----------+

```


## Neutron (controller part)

```bash
opensteak-create-vm --name neutron -c
```

Test if it works well from keystone:

```bash
cd /root
source os-creds-admin
openstack
(openstack) extension list --network -c Name -c Alias
+-----------------------------------------------+-----------------------+
| Name                                          | Alias                 |
+-----------------------------------------------+-----------------------+
| security-group                                | security-group        |
| L3 Agent Scheduler                            | l3_agent_scheduler    |
| Neutron L3 Configurable external gateway mode | ext-gw-mode           |
| Port Binding                                  | binding               |
| Provider Network                              | provider              |
| agent                                         | agent                 |
| Quota management support                      | quotas                |
| DHCP Agent Scheduler                          | dhcp_agent_scheduler  |
| Multi Provider Network                        | multi-provider        |
| Neutron external network                      | external-net          |
| Neutron L3 Router                             | router                |
| Allowed Address Pairs                         | allowed-address-pairs |
| Neutron Extra DHCP opts                       | extra_dhcp_opt        |
| Neutron Extra Route                           | extraroute            |
+-----------------------------------------------+-----------------------+
```


## Cinder


```bash
opensteak-create-vm --name cinder -c
```

Test if it works well from keystone:

```bash
cd /root
source os-creds-admin
cinder service-list
+------------------+--------+------+---------+-------+----------------------------+-----------------+
|      Binary      |  Host  | Zone |  Status | State |         Updated_at         | Disabled Reason |
+------------------+--------+------+---------+-------+----------------------------+-----------------+
| cinder-scheduler | cinder | nova | enabled |   up  | 2015-03-04T14:35:10.000000 |       None      |
|  cinder-volume   | cinder | nova | enabled |   up  | 2015-03-04T14:35:11.000000 |       None      |
+------------------+--------+------+---------+-------+----------------------------+-----------------+

```

# Move a VM
If you need to move a VM from a controller server to another one, you can do that with the following help.

We suppose that the VM disk is located in the ceph mount point (/mnt/cephfs/)

## Shutdown VM on host A
First, shutdown the VM:

```bash
virsh destroy glance
```

This will **NOT** destroy the VM, it will just shut it down. You can check the result with:

```bash
virsh list --all
```

## Create the VM on host B (new host)
Now create the VM on the new host:

```bash
cd /usr/local/opensteak/infra/kvm/vm_configs
opensteak-create-vm --name glance1
```

This will just create the vm config in a subfolder named glance1:

```bash
ls glance1
config.log  glance1.xml  meta-data  user-data
```

## Start the VM

```bash
virsh define glance1/glance1.xml
virsh autostart glance1
virsh start glance1 --console
```


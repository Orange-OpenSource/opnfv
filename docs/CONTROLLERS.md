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
  - [ On host A (old host)](#on-host-a-old-host)
    - [Shutdown VM](#shutdown-vm)
    - [Delete the VM](#delete-the-vm)
  - [ On host B (new host)](#on-host-b-new-host)
    - [ Create the VM](#create-the-vm)
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
opensteak-create-vm --name puppet --cloud-init puppet-master
```

It should configure itself by grabbing the *common.yaml* file from */usr/local/opensteak/infra/config/common.yaml*

r10k will also update all the puppet modules that will be needed

## DNS

```bash
opensteak-create-vm --name dns --cloud-init dns
```

## RabbitMQ

```bash
opensteak-create-vm --name rabbitmq1
```

## MySQL

```bash
opensteak-create-vm --name mysql1
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
opensteak-create-vm --name keystone1
```

Test if it works well with (ssh on VM before):

```bash
cd /root
source os-creds-admin
openstack service list
```

You should have:

```bash
+----------------------------------+----------+-----------+
| ID                               | Name     | Type      |
+----------------------------------+----------+-----------+
| 28efd5d67e444d4abde377562394ff05 | neutron  | network   |
| 41c2b2f2603944a4ae141ad10ad9b436 | cinderv2 | volumev2  |
| 7443585082eb4b0bbb7ff062831d5ce8 | nova_ec2 | ec2       |
| 96bf087f57514478b73474d3ec5b5050 | cinder   | volume    |
| b4f2a47081e94b98bc5cff5d13bc4999 | nova     | compute   |
| dfba7dbe490e4dce9c5b4b93e647df15 | keystone | identity  |
| ef303427135847abbb2e979fb03ff819 | glance   | image     |
| f3144de7a2e244768486237fbcfd4819 | novav3   | computev3 |
+----------------------------------+----------+-----------+
```

## Glance

```bash
opensteak-create-vm --name glance1
```
### First test
from keystone node:
```bash
cd /root
source os-creds-admin
glance image-list
+--------------------------------------+--------------+-------------+------------------+----------+--------+
| ID                                   | Name         | Disk Format | Container Format | Size     | Status |
+--------------------------------------+--------------+-------------+------------------+----------+--------+
+--------------------------------------+--------------+-------------+------------------+----------+--------+
```

### Import cirros image

```bash
mkdir images && cd images
wget http://cdn.download.cirros-cloud.net/0.3.3/cirros-0.3.3-x86_64-disk.img
glance image-create \
 --name "cirros-0.3.3-x86_64" \
 --file cirros-0.3.3-x86_64-disk.img \
--disk-format qcow2 \
--container-format bare \
--is-public True \
--progress
```

### Import Ubuntu 14.04 image

```bash
wget https://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-amd64-disk1.img
glance image-create \
 --name "Ubuntu 14.04.1 LTS" \
 --file trusty-server-cloudimg-amd64-disk1.img \
--disk-format qcow2 \
--container-format bare \
--is-public True \
--progress
```

### Check image list
```bash
glance image-list
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
glance image-create \
 --name "Ubuntu 14.04.1 LTS" \
 --file trusty-server-cloudimg-amd64-disk1.img \
--disk-format raw \
--container-format bare \
--is-public True \
--progress
```

## Nova (controller part)

```bash
opensteak-create-vm --name nova1
```

Test if it works well from keystone:

```bash
cd /root
source os-creds-admin
openstack compute service list
+------------------+------+----------+---------+-------+----------------------------+
| Binary           | Host | Zone     | Status  | State | Updated At                 |
+------------------+------+----------+---------+-------+----------------------------+
| nova-consoleauth | nova | internal | enabled | up    | 2015-02-20T09:21:18.000000 |
| nova-scheduler   | nova | internal | enabled | up    | 2015-02-20T09:17:44.000000 |
| nova-conductor   | nova | internal | enabled | up    | 2015-02-20T09:18:28.000000 |
| nova-cert        | nova | internal | enabled | up    | 2015-02-20T09:21:18.000000 |
+------------------+------+----------+---------+-------+----------------------------+
openstack host list
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
opensteak-create-vm --name neutron1
```

Test if it works well from keystone:

```bash
cd /root
source os-creds-admin
openstack extension list --network -c Name -c Alias
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
opensteak-create-vm --name cinder1
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

## On host A (old host)
### Shutdown VM
First, shutdown the VM:

```bash
virsh destroy glance1
```

This will **NOT** destroy the VM, it will just shut it down. You can check the result with:

```bash
virsh list --all
```

### Delete the VM

```bash
virsh undefine glance1
```

## On host B (new host)
### Create the VM
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

### Start the VM

```bash
virsh define glance1/glance1.xml
virsh autostart glance1
virsh start glance1 --console
```


# Compute
Each compute node is configured through puppet as well. To continue, be sure to have a base install with a valid network configuration

## Puppet

Check if you can ping puppet to be sure:

```bash
ping puppet

PING puppet.stack.opensteak.fr (192.168.1.202) 56(84) bytes of data.
64 bytes from puppet.stack.opensteak.fr (192.168.1.202): icmp_seq=1 ttl=64 time=0.864 ms
64 bytes from puppet.stack.opensteak.fr (192.168.1.202): icmp_seq=2 ttl=64 time=0.340 ms

```

The apply config:

```bash
puppet agent -t -v
```bash

Test if it works well from keystone:

```bash
cd /root
source os-creds-admin
openstack
(openstack) compute service list
+------------------+-------------+----------+----------+-------+----------------------------+
| Binary           | Host        | Zone     | Status   | State | Updated At                 |
+------------------+-------------+----------+----------+-------+----------------------------+
| nova-consoleauth | nova        | internal | enabled  | up    | 2015-02-26T14:09:04.000000 |
| nova-scheduler   | nova        | internal | enabled  | up    | 2015-02-26T14:09:03.000000 |
| nova-conductor   | nova        | internal | enabled  | up    | 2015-02-26T14:09:04.000000 |
| nova-cert        | nova        | internal | enabled  | up    | 2015-02-26T14:09:04.000000 |
| nova-compute     | opensteak93 | nova     | enabled  | up    | 2015-02-26T14:08:57.000000 |
+------------------+-------------+----------+----------+-------+----------------------------+
(openstack) host list
+-------------+-------------+----------+
| Host Name   | Service     | Zone     |
+-------------+-------------+----------+
| nova        | consoleauth | internal |
| nova        | scheduler   | internal |
| nova        | conductor   | internal |
| nova        | cert        | internal |
| opensteak93 | compute     | nova     |
+-------------+-------------+----------+

```


Test if neutron-openvswitch-agent is here as well

```bash
root@keystone:~/images# neutron agent-list
+--------------------------------------+--------------------+-------------+-------+----------------+---------------------------+
| id                                   | agent_type         | host        | alive | admin_state_up | binary                    |
+--------------------------------------+--------------------+-------------+-------+----------------+---------------------------+
| f7447c91-6cf5-49b1-a83d-4defc330e6eb | Open vSwitch agent | opensteak93 | :-)   | True           | neutron-openvswitch-agent |
+--------------------------------------+--------------------+-------------+-------+----------------+---------------------------+
```


## Create a volume
When your compute node will be ready, you will be able to test if the volume is well created in ceph with:

From keystone, create a volume:


```bash
cd /root
source os-creds-admin

cinder create --display-name demo-volume1 1
+---------------------+--------------------------------------+
|       Property      |                Value                 |
+---------------------+--------------------------------------+
|     attachments     |                  []                  |
|  availability_zone  |                 nova                 |
|       bootable      |                false                 |
|      created_at     |      2015-03-04T14:36:12.422919      |
| display_description |                 None                 |
|     display_name    |             demo-volume1             |
|      encrypted      |                False                 |
|          id         | 6d343dde-1525-488f-85a3-1985614551ea |
|       metadata      |                  {}                  |
|         size        |                  1                   |
|     snapshot_id     |                 None                 |
|     source_volid    |                 None                 |
|        status       |               creating               |
|     volume_type     |                 None                 |
+---------------------+--------------------------------------+

cinder list
+--------------------------------------+-----------+--------------+------+-------------+----------+-------------+
|                  ID                  |   Status  | Display Name | Size | Volume Type | Bootable | Attached to |
+--------------------------------------+-----------+--------------+------+-------------+----------+-------------+
| 6d343dde-1525-488f-85a3-1985614551ea | available | demo-volume1 |  1   |     None    |  false   |             |
+--------------------------------------+-----------+--------------+------+-------------+----------+-------------+


```

From a compute node, try: 

```bash
rbd -p vms ls

```

Should return a line with the volume id, like:

```bash
volume-6d343dde-1525-488f-85a3-1985614551ea
```


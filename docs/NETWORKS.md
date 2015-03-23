<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [External network machine configuration (the one with neutron)](#external-network-machine-configuration-the-one-with-neutron)
  - [Puppet](#puppet)
  - [Verification](#verification)
  - [ Create networks](#create-networks)
  - [Run a VM to test](#run-a-vm-to-test)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# External network machine configuration (the one with neutron)

## Puppet
puppet agent -t -v

## Verification
Test from keystone:

```bash
root@keystone:~/images# neutron agent-list
+--------------------------------------+--------------------+-------------+-------+----------------+---------------------------+
| id                                   | agent_type         | host        | alive | admin_state_up | binary                    |
+--------------------------------------+--------------------+-------------+-------+----------------+---------------------------+
| 541ccb55-de6f-4e5b-bc28-0e362b42e672 | DHCP agent         | opensteak99 | :-)   | True           | neutron-dhcp-agent        |
| 83e43c64-c8ec-49cc-b9ce-0a1da2a62758 | Metadata agent     | opensteak99 | :-)   | True           | neutron-metadata-agent    |
| a7088fa9-d6c1-44a5-af40-3071e1933bd8 | L3 agent           | opensteak99 | :-)   | True           | neutron-l3-agent          |
| a7768722-aa0f-48a8-bff8-d4af9c3d0992 | Open vSwitch agent | opensteak99 | :-)   | True           | neutron-openvswitch-agent |
| f7447c91-6cf5-49b1-a83d-4defc330e6eb | Open vSwitch agent | opensteak93 | :-)   | True           | neutron-openvswitch-agent |
+--------------------------------------+--------------------+-------------+-------+----------------+---------------------------+
```

## Create networks
Commandes to create network:

```bash
neutron net-create Externe --router:external --provider:physical_network physnet-ex --provider:network_type flat
neutron subnet-create Externe --name "161.105.252.0/24" --allocation-pool start=161.105.252.107,end=161.105.252.108 --disable-dhcp --gateway 161.105.252.1 161.105.252.0/24
neutron net-create demo
neutron subnet-create demo --name "192.168.42.0/24" --gateway 192.168.42.1 192.168.42.0/24
neutron router-create demo-router
neutron router-gateway-set demo-router Externe
neutron router-interface-add demo-router "192.168.42.0/24"
```

## Run a VM to test

From keystone:

```bash
neutron security-group-rule-create --protocol icmp --direction ingress default
neutron security-group-rule-create --protocol icmp --direction egress default
neutron security-group-rule-create --protocol tcp --port-range-min 1 --port-range-max 65000 --direction ingress default
neutron security-group-rule-create --protocol tcp --port-range-min 1 --port-range-max 65000 --direction egress default
neutron security-group-rule-create --protocol udp --port-range-min 1 --port-range-max 65000 --direction ingress default
neutron security-group-rule-create --protocol udp --port-range-min 1 --port-range-max 65000 --direction egress default
```

From keystone:

```bash
ssh-keygen
openstack keypair create --public-key /root/.ssh/id_rsa.pub demo-key
openstack server create --flavor m1.small --image "Ubuntu 14.04.1 LTS" --nic net-id=replace_me --security-group default --key-name demo-key demo-instance1

```

Then add a floating IP:

```bash
neutron floatingip-create Externe
nova floating-ip-associate demo-instance1 161.105.252.108
```

And try to connect to the VM:

```bash
ssh -i .ssh/id_rsa ubuntu@161.105.252.108
```

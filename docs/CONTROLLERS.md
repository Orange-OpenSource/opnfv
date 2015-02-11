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


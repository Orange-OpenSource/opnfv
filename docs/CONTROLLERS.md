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
source os-creds
keystone service-list
```

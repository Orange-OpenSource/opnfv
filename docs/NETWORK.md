# Network configuration
Before proceeding, be sure to have already complete the [base](docs/BASE.md) install

Info on network config for OpenStack:

* https://openstack.redhat.com/Networking_in_too_much_detail
* http://docs.openstack.org/juno/install-guide/install/apt/content/neutron-initial-networks.html


## Installation

We provide two bash script to automate the configuration.

* 1 script for servers with 4 interfaces (which is the default)
* 1 script for servers with 2 interfaces (with trunk access on eth0 to allow both br-adm & br-storage to share the interface)

### 4 interfaces configuration 

```bash
cd /usr/local/opensteak/
cp infra/network/interfaces /etc/network/interfaces
cp infra/network/interfaces.d/4_interfaces_servers/* /etc/network/interfaces.d/
```

Then you should replace **XXX** with the ip address of your server. Here is an example for 92:
```bash
perl -i -pe 's/XXX/92/g' /etc/network/interfaces.d/*
```

### 2 interfaces configuration

Do the same, but take care of the configuration. We use eth0 as a trunk port with access mode for br-adm & VLAN 600 for br-storage.

```bash
cd /usr/local/opensteak/
cp infra/network/interfaces /etc/network/interfaces
cp infra/network/interfaces.d/2_interfaces_servers/* /etc/network/interfaces.d/
```

Then you should replace **XXX** with the ip address of your server. Here is an example for 92:
```bash
perl -i -pe 's/XXX/92/g' /etc/network/interfaces.d/*
```

# Openstack Get Starting Installation

Openstack install and config by Orange Labs.

## Introduction
This repo contain tools and scripts to install a full Openstack Juno over Ubuntu 14.04 with OpenDayLight as SDN manager.

It aims to propose an **High Availability** deployment with **Bare Metal** provisioning.

The configuration is automatically done with **Puppet**, based on specific modules that rely on the stackforge ones (see https://github.com/stackforge/?query=puppet).

To keep the module dependencies up to date (and to download modules automatically), we use **r10k**.

The storage is handled by **Ceph**.

The only thing you should do is to provide a valid **Hiera** configuration file.


## Status
* Puppet modules: Mysql, Rabbit, Keystone, Glance, Nova are OK. Neutron is still WiP (Work in Progress)
* Bare metal provisioning: WiP
* OpenDayLight: WiP
* High Availability: WiP

## Architecture
### Basic setup

In a lab configuration, to avoid waste of resources:

* All nodes are *compute* and *storage*: they all contains nova-compute, neutron-compute and ceph OSD
* 2 nodes are also *controllers* containing KVM VMs for Openstack bricks, a DNS node and HAproxy
* 1 node is a network gateway to external networks

On each server, we have at least 4 networks:

* **br-int** : Integration bridge. Tag/untag VLAN for VM. veth for VM will be in this bridge.
* **br-vm** : Distributed bridge between compute nodes. Used to transport VM flows. In our case, we use the physical interface name **em5** as support for this bridge.
* **br-adm** : Administration bridge. This is used by controller part of OpenStack (which are in KVM) and other administrative tasks. In our case, we use the physical interface named **em3** as support for this bridge. This network needs an internet access through a default gateway to proceed installation.
* **br-storage**: Storage bridge, used by the ceph cluster. In our case, we use the physical interface name **em4** as support for this bridge.

The network server will also have one other bridge:

* **br-ex** : Bridge to communicate with external networks. In our case, we use the physical interface named **em2** as support for this bridge.


![Image of Basic setup](https://github.com/Orange-OpenSource/opnfv/raw/master/docs/archi_reseau.png)


### How do we handle OpenStack functions
Each controller part of Openstack is created separatly in a KVM machine. So that it can easily be updated or redeployed.

Each KVM machine is automatically created by a script and basic configuration comes through cloud-init. Openstack related configuration is handled by puppet.

### How do we provide HA
The work is still in progress, but we plan to use HAProxy in front of nodes, with VRRP IPs and weighted routes.

![Image of HA](https://raw.githubusercontent.com/Orange-OpenSource/opnfv/master/docs/opensteak_ha.png)


## Installation
### PXE boot for server

TODO

### Steps
Follow these steps when you have at least 3 ubuntu 14.04 servers up and running.

* Install [base infra](/docs/BASE.md) to support KVM
* Configure [network](/docs/NETWORK.md) correctly
* Optional: install [Ceph](/docs/CEPH.md) as a backend storage
* Install [Controller VM](/docs/CONTROLLERS.md)

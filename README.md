# Openstack Get Starting Installation

Openstack install and config by Orange Labs.

## Introduction
This repo contain tools and scripts to install a full Openstack Juno over Ubuntu 14.04 with OpenDayLight as SDN manager.

It aims to propose an **High Availability** deployment with **Bare Metal** provisioning.

The configuration is automatically done with **Puppet**, based on specific modules that rely on the stackforge ones (see https://github.com/stackforge/?query=puppet). 

To maintain the modules dependency up to date (and to download modules automatically), we use **r10k**.

The storage is handle by **Ceph**.

The only thing you should do is to provide a valid **Hiera** configuration file.


## Status
* Puppet modules: Mysql, Rabbit, Keystone, Glance, Nova are OK. Neutron is still in WiP (Work in Progress)
* Bare metal provisioning: WiP
* High Availability: WiP

## Architecture
### Basic setup

![Image of Basic setup](https://github.com/Orange-OpenSource/opnfv/raw/master/docs/archi_reseau.png)

### How do we provide HA
Each controller part of Openstack is created separatly in a KVM machine. So that it can easily be updated or redeploy.

Each KVM machine is automatically created by a script (opensteak-create-vm) and basic configuration comes through Cloud-init. Openstack related configuration is handled by puppet.

![Image of HA](https://raw.githubusercontent.com/Orange-OpenSource/opnfv/master/docs/opensteak_ha.png)

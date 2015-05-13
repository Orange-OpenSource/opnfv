# OpenSteak install with Foreman

## Pre requisits

This part will be automatical in a futur version:

 1. Foreman must be installed and prepared [(see INSTALL_FOREMAN.md)](INSTALL_FOREMAN.md)
 2. Prepare the foreman configurations (names are examples):
    * domains: "infra.myopensteak.com"
    * subnets: "Admin"
        * in domain "infra.myopensteak.com"
        * with DHCP proxy: "foreman.infra.myopensteak.com"
    * environments: "production"
    * hostgroups: "controller_VM"
        * with puppet classes:
            * opensteak::apt
        * with parameters:
            * global::global_sshkey: an ssh key
            * global::password: the password for user 'ubuntu'
    * operatingsystems: "Ubuntu14.04Cloud"
    * smart_proxies: "foreman.infra.myopensteak.com"
 5. A physical node to host infra VM:
    * hostgroups: "controller"
        * with puppet classes:
            * opensteak::base-network
            * opensteak::libvirt
        * with parameters:
            * opensteak::base-network::ovs_config: the openvswitch bridge configuration (for example: ["br-adm:em3:dhcp","br-vm:em5:dhcp","br-ex:em2:none"])
            * opensteak::libvirt::ovs_config: the openvswitch bridge configuration (for example: ["br-adm:em3:dhcp","br-vm:em5:dhcp","br-ex:em2:none"])
            * global::global_sshkey: an ssh key

## Configuration

* Edit file config/infra.yaml to edit the infrastucture parameters
* Edit file config/common.yaml to edit the openstack parameters

## Launch the metadata server

[See INSTALL_METADATA_SERVER.md](INSTALL_METADATA_SERVER.md)

Metadata server must run

## Install the infrastructure

With foreman login/password:

```/home/ubuntu/opnfv/infra# python3 install_opensteak.py admin password```

* Launch
* Check the printed parameters, all vars shall be OK. if no, check __config/infra.yaml__ parameters
* Confirm the VM creation

## Add physical servers in a 'compute' hostgroup
with puppet classes:

* opensteak::base-network
* opensteak::libvirt

## Enjoy
That all folks !



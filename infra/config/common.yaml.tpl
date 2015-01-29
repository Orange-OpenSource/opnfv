# config.yaml
---

###
## DNS
###
domain: opensteak.fr
dns::external:
 - 8.8.8.8
 - 8.8.4.4
dns::internal: "%{hiera('infra::dns')}"

###
##  OpenStack passwords
###
admin::password: 'strongpassword'           
mysql::service-password: "strongpassword"
rabbitmq::password: "strongpassword"
glance::password: "strongpassword"
nova::password: "strongpassword"
neutron::shared-secret: "strongpassword"
neutron::password: "strongpassword"
cinder::password: "strongpassword"

###
## Admin stuff
###
admin::mail: "admin@%{hiera('domain')}"
admin::tenant: 'admin'

###
## Log Levels & misc
####
verbose: 'False'
debug: 'False'
region: 'Orange'

###
## Infrastructure : servers out of openstack
###
# Network
infra::network: 192.168.1.0
infra::network_mask: 255.255.255.0
infra::network_broadcast: 192.168.1.255
infra::network_gw: 192.168.1.1
storage::network: 192.168.2.0
storage::network_mask: 255.255.255.0
storage::network_broadcast: 192.168.2.255

# DNS
infra::reverse_zone: 1.168.192.in-addr.arpa
infra::dns: 192.168.1.201 

# Machines
infra::puppet: 192.168.1.202
infra::nodes:
 compute96: 192.168.1.96
 compute97: 192.168.1.97
 compute98: 192.168.1.98
 network99: 192.168.1.99
infra::ceph_admin: 192.168.1.200
infra::nas: 192.168.0.2

# Ceph Password
ceph::password: 'strongpassword'
ceph::mount: '/mnt/cephfs'
ceph::pool: 'ceph'

###
## KVM
###
# KVM password for user ubuntu for OpenSteak infra VM
kvm::password: 'strongpassword'

# Default KVM sizing
kvm::default::cpu: 2
kvm::default::ram: 1048576
kvm::default::pool::name: 'default'
kvm::default::pool::mount: '/var/lib/libvirt/images'
kvm::default::init: 'kvm/templates/cloud-init/basic'
kvm::default::net: 'kvm/templates/meta-data/basic'
kvm::default::net_storage: 'kvm/templates/meta-data/storage'
kvm::default::conf: 'kvm/templates/kvm_config/basic'
kvm::default::conf_storage: 'kvm/templates/kvm_config/storage'

###
## Stack : servers for openstack (vm.stack.DOMAIN)
###
stack::domain: "stack.%{hiera('domain')}"
stack::vm:
 rabbitmq: 192.168.1.203
 keystone: 192.168.1.204
 mysql: 192.168.1.205
 glance: 192.168.1.208
 glance-storage: 192.168.0.208
 nova: 192.168.1.206
 neutron: 192.168.1.207

###
## OpenStack stuff
###
horizon::fqdn: "www.%{hiera('domain')}"

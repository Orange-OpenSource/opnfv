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
dns::contact: "contact@%{hiera('domain')}"

###
## HA
###
stack::ha::enabled: true

##
# KVM password for user ubuntu for OpenSteak infra VM
##
kvm::password: 'strongpassword'

###
##  OpenStack passwords
###
ceph::password: "strongpassword"
admin::password: "strongpassword"
mysql::service-password: "strongpassword"
mysql::root-password: "strongpassword"
rabbitmq::password: "strongpassword"
glance::password: "strongpassword"
nova::password: "strongpassword"
neutron::shared-secret: "strongpassword"
neutron::password: "strongpassword"
cinder::password: "strongpassword"
keystone::admin-token: "strongpassword"
horizon::secret_key: "12345"

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
infra::network_mask: 24
infra::network_broadcast: 192.168.1.255
infra::network_gw: 192.168.1.1
storage::network: 192.168.2.0
storage::network_mask: 255.255.255.0
storage::network_broadcast: 192.168.2.255

# DNS
infra::reverse_zone: 1.168.192.in-addr.arpa
infra::dns: 192.168.1.249

# Phyiscal Machines
infra::nodes:
 opensteak93: 192.168.1.93
 opensteak94: 192.168.1.94
 opensteak95: 192.168.1.95
 opensteak96: 192.168.1.96
 
# Infra tools
infra::puppet: 192.168.1.241
infra::ceph-admin: 192.168.1.240

###
## Stack : servers for openstack (vm.stack.DOMAIN)
###
stack::domain: "stack.%{hiera('domain')}"
stack::vm:
 ha1: 192.168.1.200
 rabbitmq1: 192.168.1.201
 mysql1: 192.168.1.202
 keystone1: 192.168.1.203
 glance1: 192.168.1.204
 glance-storage1: 192.168.0.204
 nova1: 192.168.1.205
 neutron1: 192.168.1.206
 cinder1: 192.168.1.207
 horizon1: 192.168.1.208
 ha2: 192.168.1.220
 rabbitmq2: 192.168.1.221
 mysql2: 192.168.1.222
 keystone2: 192.168.1.223
 glance2: 192.168.1.224
 glance-storage2: 192.168.0.224
 nova2: 192.168.1.225
 neutron2: 192.168.1.226
 cinder2: 192.168.1.227
 horizon2: 192.168.1.228
stack::ha::vip: 192.168.1.250

###
## OpenStack stuff
###
horizon::publicfqdn: "www.%{hiera('domain')}"

###
## Ceph stuff
###
cephfs::mount: '/mnt/cephfs'
cephfs::pool: 'ceph'
rbd_secret_uuid: '457eb676-33da-42ec-9a8c-9293d545c337'

###
## KVM
###

# Default KVM sizing
kvm::default::cpu: 2
kvm::default::ram: 1048576

# Default Pool
kvm::default::pool::name: 'default'
kvm::default::pool::mount: '/var/lib/libvirt/images'

# Default configs
kvm::default::init::folder: 'kvm/templates/cloud-init'
kvm::default::init::name: 'basic'
kvm::default::net::folder: 'kvm/templates/meta-data'
kvm::default::net::name: 'basic'
kvm::default::net::storage: 'storage'
kvm::default::conf::folder: 'kvm/templates/kvm_config'
kvm::default::conf::name: 'config'
kvm::default::conf::storage: 'storage'

# Default SSH authorizd keys for user ubuntu
kvm::default::ssh-auth-keys:
 - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC0g+ZTxC7weoIJLUafOgrm+h...
 - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC0g+ZTxC7weoIJLUafOgrm+h...

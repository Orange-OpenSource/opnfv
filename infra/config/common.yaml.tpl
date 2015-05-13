# common.yaml
---

###
##  OpenStack passwords
###
ceph_password: "password"
admin_password: "password"
mysql_service_password: "password"
mysql_root_password: "password"
rabbitmq_password: "password"
glance_password: "password"
nova_password: "password"
neutron_shared_secret: "password"
neutron_password: "password"
cinder_password: "password"
keystone_admin_token: "password"
horizon_secret_key: "12345"

domain: "infra.opensteak.fr"

###
## Class parameters
###
# Rabbit
opensteak::rabbitmq::rabbitmq_password: "%{hiera('rabbitmq_password')}"

# MySQL
opensteak::mysql::root_password: "%{hiera('mysql_root_password')}"
opensteak::mysql::mysql_password: "%{hiera('mysql_service_password')}"

# Key
opensteak::key::password: "%{hiera('admin_password')}"
opensteak::key::stack_domain: "%{hiera('domain')}"

# Keystone
opensteak::keystone::mysql_password: "%{hiera('mysql_root_password')}"
opensteak::keystone::rabbitmq_password: "%{hiera('rabbitmq_password')}"
opensteak::keystone::keystone_token: "%{hiera('keystone_admin_token')}"
opensteak::keystone::stack_domain: "%{hiera('domain')}"
opensteak::keystone::admin_mail: "admin@opensteak.fr"
opensteak::keystone::admin_password: "%{hiera('admin_password')}"
opensteak::keystone::glance_password: "%{hiera('glance_password')}"
opensteak::keystone::nova_password: "%{hiera('nova_password')}"
opensteak::keystone::neutron_password: "%{hiera('neutron_password')}"
opensteak::keystone::cinder_password: "%{hiera('cinder_password')}"

# Glance
opensteak::glance::mysql_password: "%{hiera('mysql_root_password')}"
opensteak::glance::rabbitmq_password: "%{hiera('rabbitmq_password')}"
opensteak::glance::stack_domain: "%{hiera('domain')}"
opensteak::glance::glance_password: "%{hiera('glance_password')}"

# Nova
opensteak::nova::mysql_password: "%{hiera('mysql_root_password')}"
opensteak::nova::rabbitmq_password: "%{hiera('rabbitmq_password')}"
opensteak::nova::stack_domain: "%{hiera('domain')}"
opensteak::nova::nova_password: "%{hiera('nova_password')}"
opensteak::nova::neutron_password: "%{hiera('neutron_password')}"
opensteak::nova::neutron_shared: "%{hiera('neutron_shared_secret')}"

# Cinder
opensteak::cinder::mysql_password: "%{hiera('mysql_root_password')}"
opensteak::cinder::rabbitmq_password: "%{hiera('rabbitmq_password')}"
opensteak::cinder::stack_domain: "%{hiera('domain')}"
opensteak::cinder::nova_password: "%{hiera('cinder_password')}"

# Compute
opensteak::nova-compute::mysql_password: "%{hiera('mysql_root_password')}"
opensteak::nova-compute::rabbitmq_password: "%{hiera('rabbitmq_password')}"
opensteak::nova-compute::stack_domain: "%{hiera('domain')}"
opensteak::nova-compute::neutron_password: "%{hiera('neutron_password')}"


# Neutron controller
opensteak::neutron-controller::mysql_password: "%{hiera('mysql_root_password')}"
opensteak::neutron-controller::rabbitmq_password: "%{hiera('rabbitmq_password')}"
opensteak::neutron-controller::stack_domain: "%{hiera('domain')}"
opensteak::neutron-controller::nova_password: "%{hiera('nova_password')}"
opensteak::neutron-controller::neutron_password: "%{hiera('neutron_password')}"
# Neutron compute
opensteak::neutron-compute::mysql_password: "%{hiera('mysql_root_password')}"
opensteak::neutron-compute::rabbitmq_password: "%{hiera('rabbitmq_password')}"
opensteak::neutron-compute::stack_domain: "%{hiera('domain')}"
opensteak::neutron-compute::neutron_password: "%{hiera('neutron_password')}"
opensteak::neutron-compute::neutron_shared: "%{hiera('neutron_shared_secret')}"
opensteak::neutron-compute::infra_nodes:
 server186:
  ip: 192.168.1.27
  bridge_uplinks:
   - 'br-vm:p3p1'
 server187:
  ip: 192.168.1.155
  bridge_uplinks:
   - 'br-vm:p3p1'
 server188:
  ip: 192.168.1.116
  bridge_uplinks:
   - 'br-vm:p3p1'
 server189:
  ip: 192.168.1.117
  bridge_uplinks:
   - 'br-vm:p3p1'
# Neutron network
opensteak::neutron-network::mysql_password: "%{hiera('mysql_root_password')}"
opensteak::neutron-network::rabbitmq_password: "%{hiera('rabbitmq_password')}"
opensteak::neutron-network::stack_domain: "%{hiera('domain')}"
opensteak::neutron-network::neutron_password: "%{hiera('neutron_password')}"
opensteak::neutron-network::neutron_shared: "%{hiera('neutron_shared_secret')}"
opensteak::neutron-network::infra_nodes:
 server98:
  ip: 192.168.1.58
  bridge_uplinks:
   - 'br-ex:em2'
   - 'br-vm:em5'

# Horizon
opensteak::horizon::stack_domain: "%{hiera('domain')}"
opensteak::horizon::secret_key: "%{hiera('horizon_secret_key')}"

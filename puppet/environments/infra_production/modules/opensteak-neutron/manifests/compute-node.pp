#
# Copyright (C) 2014 Orange Labs
# 
# This software is distributed under the terms and conditions of the 'Apache-2.0'
# license which can be found in the file 'LICENSE.txt' in this package distribution 
# or at 'http://www.apache.org/licenses/LICENSE-2.0'. 
#
# Authors: Arnaud Morin <arnaud1.morin@orange.com> 
#          David Blaisonneau <david.blaisonneau@orange.com>
#

#
#  The profile to install neutron
#
class opensteak-neutron::compute-node {
  # Recupere le password pour les services
  $password = hiera('mysql::service-password')

  # Récupere les domaines
  $stack_domain = hiera('stack::domain')


  ##
  # Forwarding plane
  ##
  ::sysctl::value { 'net.ipv4.ip_forward':
    value     => '1',
  }

  ::sysctl::value { 'net.ipv4.conf.all.rp_filter':
    value     => '0',
  }

  ::sysctl::value { 'net.ipv4.conf.default.rp_filter':
    value     => '0',
  }


  ##
  # Neutron
  ##
  class { '::neutron':
    debug                 => hiera('debug'),
    verbose               => hiera('verbose'),
    rabbit_host           => "rabbitmq.${stack_domain}",
    rabbit_password       => hiera('rabbitmq::password'),
    core_plugin           => 'ml2',
    service_plugins       => ['router'],
    allow_overlapping_ips => true,
  }

  class { '::neutron::plugins::ml2':
    type_drivers          => ['vlan'],
    tenant_network_types  => ['vlan'],
    network_vlan_ranges   => ['physnet-vm:701:899'],
    enable_security_group => true,
    #require               => Package['neutron-plugin-openvswitch', 'neutron-plugin-linuxbridge', 'neutron-plugin-ml2'],
    require               => Package['neutron-plugin-openvswitch', 'neutron-plugin-ml2'],
  }

  class { '::neutron::config':
    # Ajout config keystone
    server_config =>
    {
      'keystone_authtoken/auth_uri'           => { value => "http://keystone.${stack_domain}:5000" }, 
      'keystone_authtoken/auth_host'          => { value => "keystone.${stack_domain}" }, 
      'keystone_authtoken/auth_protocol'      => { value => 'http' },
      'keystone_authtoken/auth_port'          => { value => '35357' },
      'keystone_authtoken/admin_tenant_name'  => { value => 'services' },
      'keystone_authtoken/admin_user'         => { value => 'neutron' },
      'keystone_authtoken/admin_password'     => { value => hiera('neutron::password') },
    },
    # Ajout config ovs
    plugin_ml2_config =>
    {
      'ovs/enable_tunneling'    => { value  => 'False' },
      'ovs/integration_bridge'  => { value  => 'br-int' },
      'ovs/bridge_mappings'     => { value  => 'physnet-vm:br-vm' },
    },
  }


  class { '::neutron::agents::ovs': 
    bridge_mappings   => ['physnet-vm:br-vm'],
    bridge_uplinks    => ['br-vm:em5'],
  }

  package { [
      'neutron-plugin-ml2',
      'neutron-plugin-openvswitch',
      #      'neutron-plugin-linuxbridge',
    ]:
    ensure  => present,
  }
}

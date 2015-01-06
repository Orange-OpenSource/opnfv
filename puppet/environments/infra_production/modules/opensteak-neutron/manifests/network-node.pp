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
class opensteak-neutron::network-node {
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
  # neutron.conf
  class { '::neutron':
    debug                 => hiera('debug'),
    verbose               => hiera('verbose'),
    rabbit_host           => "rabbitmq.${stack_domain}",
    rabbit_password       => hiera('rabbitmq::password'),
    core_plugin           => 'ml2',
    service_plugins       => ['router'],
    allow_overlapping_ips => true,
  }

  # neutron api
  class { '::neutron::server':
    auth_host           => "keystone.${stack_domain}",
    auth_password       => hiera('neutron::password'),
    database_connection => "mysql://neutron:${password}@mysql.${stack_domain}/neutron",
    enabled             => true,
    #sync_db             => true,
    mysql_module        => '2.3',
  }

  # neutron notifications depuis nova
  class { '::neutron::server::notifications':
    nova_url            => "http://nova.${stack_domain}:8774/v2",
    nova_admin_auth_url => "http://keystone.${stack_domain}:35357/v2.0",
    nova_admin_password => hiera('nova::password'),
    nova_region_name    => hiera('region'),
  }

  # neutron plugin ml2
  class { '::neutron::plugins::ml2':
    type_drivers          => ['vlan','flat'],
    flat_networks         => ['physnet-ex'],
    tenant_network_types  => ['vlan','flat'],
    network_vlan_ranges   => ['physnet-vm:701:899'],
    mechanism_drivers     => ['openvswitch'],
    enable_security_group => true,
    require               => Package['neutron-plugin-openvswitch', 'neutron-plugin-ml2'],
  }

  # neutron plugin ml2 agent ovs
  class { '::neutron::agents::ml2::ovs': 
    bridge_uplinks    => ['br-ex:em2', 'br-vm:em5'],
    bridge_mappings   => ['physnet-ex:br-ex', 'physnet-vm:br-vm'],
  }

  class { '::neutron::agents::l3': 
    debug          => hiera('debug'),
    use_namespaces => true,
  }

  class { '::neutron::agents::dhcp':
    debug   => hiera('debug'),
  }

  class { '::neutron::agents::metadata':
    auth_password => hiera('neutron::password'),
    shared_secret => hiera('neutron::shared-secret'),
    auth_url      => "http://keystone.${stack_domain}:35357/v2.0",
    debug         => hiera('debug'),
    auth_region   => hiera('region'),
    metadata_ip   => "nova.${stack_domain}",
  }


  package { [
      'neutron-plugin-ml2',
      'neutron-plugin-openvswitch',
    ]:
    ensure  => present,
  }
}

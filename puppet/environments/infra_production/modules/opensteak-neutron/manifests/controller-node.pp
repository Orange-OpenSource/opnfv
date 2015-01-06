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
class opensteak-neutron::controller-node {
  # Recupere le password pour les services
  $password = hiera('mysql::service-password')

  # Récupere les domaines
  $stack_domain = hiera('stack::domain')

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

  # Ajout d'une conf pas prise en charge par la classe neutron::plugins::ml2
  class { '::neutron::config':
    plugin_ml2_config =>
    {
      'securitygroup/firewall_driver'       => { value => 'neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver'},
# Will be deprecated soon
#      'securitygroup/enable_security_group' => { value => 'True'},
    },
    require               => Package['neutron-plugin-openvswitch', 'neutron-plugin-ml2'],
  }

  package { [
      'neutron-plugin-ml2',
      'neutron-plugin-openvswitch',
    ]:
    ensure  => present,
  }
}

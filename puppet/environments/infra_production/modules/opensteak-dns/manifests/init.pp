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
# The profile to install the dns machine
#
class opensteak-dns {
  include bind

  $domain = hiera('domain')
  $stack_domain = hiera('stack::domain')
  $infra_reverse = hiera('infra::reverse_zone')
  $infra_vm = hiera('infra::vm')
  $infra_vm_names = keys($infra_vm)
  $stack_vm = hiera('stack::vm')
  $stack_vm_names = keys($stack_vm)
  $infra_nodes = hiera('infra::nodes')
  $infra_nodes_names = keys($infra_nodes)
  $forwarders = hiera('dns::external')

  file { '/etc/bind/named.conf.options': 
    content => template('opensteak-dns/named.conf.options.erb'),
  }

  # Pour toutes les zones
  Bind::Zone {
    zone_contact => hiera('dns::contact'),
    zone_ns      => "dns.$domain",
    zone_serial  => '2014100201',
    zone_ttl     => '3800',
    zone_origin  => $domain,
  }

  # opensteak.fr
  bind::zone { $domain: }
  # reverse
  bind::zone { $infra_reverse: }
  # stack.opensteak.fr
  bind::zone { $stack_domain: 
    zone_origin => $stack_domain,
  }

  # Pour tous les records type A
  Bind::A {
    ensure    => 'present',
    zone_arpa => $infra_reverse,
    ptr       => true,
  }

  # Create all records for stack
  create_a_record { $stack_vm_names:
    domain     => $stack_domain,
    vm_ip_hash => $stack_vm,
  }

  # Create all records for infra
  create_a_record { $infra_vm_names:
    domain     => $domain,
    vm_ip_hash => $infra_vm,
  }

  # Create all records for nodes
  create_a_record { $infra_nodes_names:
    domain     => $domain,
    vm_ip_hash => $infra_nodes,
  }

  # CNAME puppet.stack vers puppet
  bind::record {"CNAME puppet.${domain}.":
    zone        => $stack_domain,
    record_type => 'CNAME',
    hash_data   => {
      'puppet'      => { owner => "puppet.${domain}.", },
    }
  }

  #
  # Create record type A in bind
  #
  define create_a_record( $vm_name = $title, $domain, $vm_ip_hash){
    bind::a { $vm_name:
      zone      => $domain,
      hash_data => {"$vm_name" => { owner => $vm_ip_hash[$vm_name], }, },
    }
  }
}



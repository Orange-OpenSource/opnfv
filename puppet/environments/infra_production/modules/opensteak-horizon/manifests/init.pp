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
class opensteak-horizon {

  $domain = hiera('domain')
  $stack_domain = hiera('stack::domain')

##### A COMPLETER #####

  $management_address = hiera('ip-management')
  class { '::horizon':
    django_debug => hiera('debug'),
    log_level => 'INFO',
    fqdn => hiera('horizon::fqdn'),
    servername => hiera('horizon::fqdn'),
    secret_key => hiera('horizon::secret-key'),
    cache_server_ip => hiera('ip-management'),
    listen_ssl => true,
    horizon_cert => '/etc/ssl/certs/ssl-cert-snakeoil.pem',
    horizon_ca => '/etc/ssl/certs/ssl-cert-snakeoil.pem',
    horizon_key => '/etc/ssl/private/ssl-cert-snakeoil.key',
    keystone_url => "http://${management_address}:5000/v2.0",
    neutron_options => {
      'enable_vpn' => true,
      'enable_firewall' => true,
    },
  }
  if $::selinux and str2bool($::selinux) != false {
    selboolean{'httpd_can_network_connect':
      value => on,
      persistent => true,
    }
  }
}

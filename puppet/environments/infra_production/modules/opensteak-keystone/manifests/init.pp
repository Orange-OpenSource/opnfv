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
#  The profile to install keystone
#
class opensteak-keystone {
  # Recupere le password pour les services
  $password = hiera('mysql::service-password')

  # Récupere les domaines
  $domain = hiera('domain')
  $stack_domain = hiera('stack::domain')

  class { '::keystone':
    verbose           => hiera('verbose'),
    debug             => hiera('debug'),
    admin_token       => hiera('keystone::admin-token'),
    sql_connection    => "mysql://keystone:${password}@mysql.${stack_domain}/keystone",
    catalog_type      => 'sql',
    mysql_module      => '2.3',
  }

  class { '::keystone::roles::admin':
    email        => hiera('admin::mail'),
    password     => hiera('admin::password'),
    admin_tenant => hiera('admin::tenant'),
  }

  class { 'keystone::endpoint':
    public_address   => "keystone.${stack_domain}",
    admin_address    => "keystone.${stack_domain}",
    internal_address => "keystone.${stack_domain}",
    region           => hiera('region'),
  }

  class { '::glance::keystone::auth':
    password         => hiera('glance::password'),
    public_address   => "glance.${stack_domain}",
    admin_address    => "glance.${stack_domain}",
    internal_address => "glance.${stack_domain}",
    region           => hiera('region'),
  }

  class { '::nova::keystone::auth':
    password         => hiera('nova::password'),
    public_address   => "nova.${stack_domain}",
    admin_address    => "nova.${stack_domain}",
    internal_address => "nova.${stack_domain}",
    region           => hiera('region'),
  }

  class { '::neutron::keystone::auth':
    password         => hiera('neutron::password'),
    public_address   => "neutron.${stack_domain}",
    admin_address    => "neutron.${stack_domain}",
    internal_address => "neutron.${stack_domain}",
    region           => hiera('region'),
  }

  class { '::cinder::keystone::auth':
    password         => hiera('cinder::password'),
    public_address   => "cinder.${stack_domain}",
    admin_address    => "cinder.${stack_domain}",
    internal_address => "cinder.${stack_domain}",
    region           => hiera('region'),
  }

 
}

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
class opensteak-cinder {

  $domain = hiera('domain')
  $stack_domain = hiera('stack::domain')

  # Recupere le password pour les services
  $password = hiera('mysql::service-password')

##### A COMPLETER #####

  # Recupere l'adresse ip pour tgt (iscsi target daemon)
  $tgt_listen_ip = hiera('cinder::tgt-listen-ip')

  class { '::cinder':
    sql_connection    => "mysql://cinder:${password}@$mysql.${stack_domain}/cinder",
    rabbit_host       => "rabbitmq.${stack_domain}",
    rabbit_password   => hiera('rabbitmq::password'),
    debug             => hiera('debug'),
    verbose           => hiera('verbose'),
    mysql_module      => '2.2',
  }

  class { '::cinder::volume': }

  class { '::cinder::volume::iscsi':
    iscsi_ip_address  => $tgt_listen_ip,
    volume_group      => hiera('cinder::vg-name'),
  }

  class { '::cinder::glance':
    glance_api_servers  => "glance.${stack_domain}:9292",
    glance_api_version  => '1',
  }

  class { '::cinder::api':
    keystone_password   => hiera('cinder::password'),
    keystone_auth_host  => "keystone.${stack_domain}",
    enabled             => true,
  }

  class { '::cinder::scheduler':
    scheduler_driver => 'cinder.scheduler.filter_scheduler.FilterScheduler',
    enabled          => true,
  }

  # On a besoin de sheepdog
  # voir ici : https://lists.launchpad.net/openstack/msg21163.html
  package { 'sheepdog':
    ensure => 'present',
  }

  # Mise a jour du fichier init de tgt
  file { '/etc/init/tgt.conf':
    content => template("opensteak-cinder/tgt.conf.erb"),
    notify  => Service['tgt'],
  }  


}

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
#  The profile to install rabbitmq
#
class opensteak-rabbitmq {
  $rabbitmq_password = hiera('rabbitmq::password')

  package { 'rabbitmq-server':
    ensure => installed,
  }

  exec { 'rabbitmq-change-guest-password':
    command     => "rabbitmqctl change_password guest $rabbitmq_password",
    subscribe => Package['rabbitmq-server'],
    refreshonly => true
  }
}

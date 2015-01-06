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
class opensteak-heat {

  $domain = hiera('domain')
  $stack_domain = hiera('stack::domain')

##### A COMPLETER #####

  # Common class
  class { 'heat':
  # The keystone_password parameter is mandatory
    keystone_password => 'password',
    sql_connection => 'mysql://heat:heat@localhost/heat'
  }
  # Install heat-engine
  class { 'heat::engine':
    auth_encryption_key => 'whatever-key-you-like',
  }
  # Install the heat-api service
  class { 'heat::api': }

}

# Installs & configure the heat CloudWatch API service

class heat::api_cloudwatch (
  $enabled           = true,
  $bind_host         = '0.0.0.0',
  $bind_port         = '8003',
  $workers           = '0',
  $use_ssl           = false,
  $cert_file         = false,
  $key_file          = false,
) {

  include heat
  include heat::params

  Heat_config<||> ~> Service['heat-api-cloudwatch']

  Package['heat-api-cloudwatch'] -> Heat_config<||>
  Package['heat-api-cloudwatch'] -> Service['heat-api-cloudwatch']

  if $use_ssl {
    if !$cert_file {
      fail('The cert_file parameter is required when use_ssl is set to true')
    }
    if !$key_file {
      fail('The key_file parameter is required when use_ssl is set to true')
    }
  }

  package { 'heat-api-cloudwatch':
    ensure => installed,
    name   => $::heat::params::api_cloudwatch_package_name,
  }

  if $enabled {
    $service_ensure = 'running'
  } else {
    $service_ensure = 'stopped'
  }

  Package['heat-common'] -> Service['heat-api-cloudwatch']

  service { 'heat-api-cloudwatch':
    ensure     => $service_ensure,
    name       => $::heat::params::api_cloudwatch_service_name,
    enable     => $enabled,
    hasstatus  => true,
    hasrestart => true,
    subscribe  => Exec['heat-dbsync'],
  }

  heat_config {
    'heat_api_cloudwatch/bind_host'  : value => $bind_host;
    'heat_api_cloudwatch/bind_port'  : value => $bind_port;
    'heat_api_cloudwatch/workers'    : value => $workers;
  }

  # SSL Options
  if $use_ssl {
    heat_config {
      'heat_api_cloudwatch/cert_file' : value => $cert_file;
      'heat_api_cloudwatch/key_file' :  value => $key_file;
    }
  } else {
    heat_config {
      'heat_api_cloudwatch/cert_file' : ensure => absent;
      'heat_api_cloudwatch/key_file' :  ensure => absent;
    }
  }

}

# private define
# $name will be an index into the $mcollective::middleware_hosts array + 1
define mcollective::server::config::connector::rabbitmq::hosts_iteration {
  if $mcollective::middleware_ssl {
    mcollective::server::setting { "plugin.rabbitmq.pool.${name}.ssl.cert":
      value => "${mcollective::confdir}/server_public.pem",
    }

    mcollective::server::setting { "plugin.rabbitmq.pool.${name}.ssl.key":
      value => "${mcollective::confdir}/server_private.pem",
    }
  }
}

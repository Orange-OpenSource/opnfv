# -*- coding: utf-8 -*-
"""
:author: Pawel Chomicki
:contact: pawel.chomicki@nokia.com
"""


class VMConfigBuilder(object):
    """Virtual machine configuration builder.

    Based on command line parameters and Hiera configuration parameters generates virtual machine
    configuration object.

    ::

        builder = VMConfigBuilder(args, hiera)
        config = builder.build()
        config.name     # Get VM name
        config.ip_net   # Get VM IP network
        config.mask     # Get VM network mask

    """

    def __init__(self, cmd_args, hiera_config):
        """
        :param cmd_args: Object which contains command line parameters provided by the user.
        :param hiera_config: Object which contains Hiera YAML configuration parameters.
        """
        self._hiera_config = hiera_config
        self._cmd_args = cmd_args
        self._vm_config = VMConfig()

    def build(self):
        """Creates VM configuration file based."""
        self._vm_config.name = self._set_name()
        self._vm_config.ip_net = self._hiera_config.infra.network
        self._vm_config.mask = self._hiera_config.infra.network_mask
        self._vm_config.bc = self._hiera_config.infra.broadcast_network
        self._vm_config.gw = self._hiera_config.infra.nework_gw
        self._vm_config.ip_ext_dns = self._set_external_dns()
        self._vm_config.ip_int_dns = self._hiera_config.infra.dns
        self._vm_config.ip_dns = "{} {}".format(self._vm_config.ip_ext_dns, self._vm_config.ip_int_dns)
        self._vm_config.ip_dnssearch = self._hiera_config.stack.domain

    def _set_name(self):
        if self._cmd_args.name == 'dns' or self._cmd_args.name == 'puppet' or self._cmd_args.name == 'ceph-admin':
            return self._hiera_config.infra.name
        return self._hiera_config.stack.vm[self._cmd_args.name]

    def _set_external_dns(self):
        raise Exception("Not implemented")


class VMConfig(dict):
    """Virtual machine configuration object. This is dict like object with additional DOT syntax.

    ::

        vmconfig = VMConfig()
        vmconfig.something = '1'    # Set something attr. Equals vmconfig['something'] = '1'
        vmconfig.something          # Get something attr. Equals vmconfig['something']

    """
    def __setattr__(self, key, value):
        if key not in self.__dict__:
            self.__dict__[key] = value
        raise ValueError("Attribute {} can't be overridden.".format(key))

    def __getattr__(self, item):
        return self.__dict__[item]

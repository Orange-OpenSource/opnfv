#!/usr/bin/python
# -*-coding:utf8 -*

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class OpenSteakConfig:
    """OpenSteak config class
    Use this object as a dict
    """

    def __init__(self,
                 config_file="/usr/local/opensteak/infra/config/common.yaml",
                 autosave=False):
        """ Function __init__
        Load saved opensteak config.

        @param PARAM: DESCRIPTION
        @return RETURN: DESCRIPTION
        @param config_file: the yaml config file to read.
            default is '/usr/local/opensteak/infra/config/common.yaml'
        @param autosave: save automaticly the config at destroy
            default is False
        """
        self.config_file = config_file
        self.autosave = autosave
        with open(self.config_file, 'r') as stream:
            self._data = load(stream, Loader=Loader)

    def __getitem__(self, index):
        """Get an item of the configuration"""
        return self._data[index]

    def __setitem__(self, index, value):
        """Set an item of the configuration"""
        self._data[index] = value

    def list(self):
        """Set an item of the configuration"""
        return self._data.keys()

    def dump(self):
        """Dump the configuration"""
        return dump(self._data, Dumper=Dumper)

    def save(self):
        """Save the configuration to the file"""
        with open(self.config_file, 'w') as f:
            f.write(dump(self._data, Dumper=Dumper))

    def __del__(self):
        if self.autosave:
            self.save()

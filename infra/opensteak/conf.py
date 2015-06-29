#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# Authors:
# @author: David Blaisonneau <david.blaisonneau@orange.com>
# @author: Arnaud Morin <arnaud1.morin@orange.com>

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

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

#~ from foreman.api import Api
import requests
from bs4 import BeautifulSoup
import sys
import json

class FreeIP:
    """ FreeIP return an available IP in the targeted network """

    def __init__ (self, login, password):
        """ Init: get authenticity token """
        with requests.session() as self.session:
            try:
                #~ 1/ Get login token and authentify
                payload = {}
                log_soup = BeautifulSoup(self.session.get('https://127.0.0.1/users/login', verify=False).text)
                payload['utf8'] = log_soup.findAll('input',attrs={'name':'utf8'})[0].get('value')
                payload['authenticity_token'] = log_soup.findAll('input',attrs={'name':'authenticity_token'})[0].get('value')
                if payload['authenticity_token'] == None:
                    raise requests.exceptions.RequestException("Bad catch of authenticity_token")
                payload['commit']='Login'
                payload['login[login]'] = login
                payload['login[password]'] = password
                #~ 2/ Log in
                r = self.session.post('https://127.0.0.1/users/login', verify=False, data=payload)
                if r.status_code != 200:
                    raise requests.exceptions.RequestException("Bad login or password")
                #~ Get token for host creation
                log_soup = BeautifulSoup(self.session.get('https://127.0.0.1/hosts/new', verify=False).text)
                self.authenticity_token = log_soup.findAll('input',attrs={'name':'authenticity_token'})[0].get('value')
                if payload['authenticity_token'] == None:
                    raise requests.exceptions.RequestException("Bad catch of authenticity_token")
            except requests.exceptions.RequestException as e:
                print("Error connection Foreman to get a free ip")
                print(e)
                sys.exit(1)
        pass

    def get(self, subnet, mac = ""):
        payload = {"host_mac": mac, "subnet_id": subnet}
        payload['authenticity_token'] = self.authenticity_token
        try:
            self.last_ip = json.loads(self.session.post('https://127.0.0.1/subnets/freeip', verify=False, data=payload).text)['ip']
            if payload['authenticity_token'] == None:
                raise requests.exceptions.RequestException("Error getting free IP")
        except requests.exceptions.RequestException as e:
            print("Error connection Foreman to get a free ip")
            print(e)
            sys.exit(1)
        return self.last_ip



if __name__ == "__main__":
    import pprint
    import sys
    if len(sys.argv) == 4:
        f = FreeIP(sys.argv[1], sys.argv[2])
        print(f.get(sys.argv[3]))
    else:
        print('Error: Usage\npython {} foreman_user foreman_password subnet'.format(sys.argv[0]))

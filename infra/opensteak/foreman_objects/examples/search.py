#!/usr/bin/python3
from pprint import pprint as pp
from foreman.foremanAPI import ForemanAPI
import json

import sys
foreman_auth = (sys.argv[1], sys.argv[2])
foreman = ForemanAPI(foreman_auth, '192.168.1.4')
filter = 'name = opensteak::horizon'
#~ pp( foreman.list('puppetclasses', filter=filter, only_id=True) )
#~ pp( foreman.list('puppetclasses', only_id=True, limit=999) )
#~ pp( foreman.list('hosts', only_id=True) )
pp( foreman.get_id_by_name('compute_resources', 'controller2.opensteak.fr' ))
pp( foreman.get_id_by_name('hostgroups', 'controller_VM' ) )

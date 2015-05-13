#!/usr/bin/python3
from pprint import pprint as pp
from foreman.foremanAPI import ForemanAPI
import json
import time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_id_and_print(obj, name):
    id = foreman.get_id_by_name(obj, name )
    if id:
        print(" - {0:40} > {} [{}]: ".format(obj, name, id), bcolors.OKBLUE, 'OK', bcolors.ENDC)
    else:
        print(" - {0:40} > {}: ".format(msg), bcolors.FAIL, 'KO', bcolors.ENDC)
        print("   ", failed)
        exit



if __name__ == "__main__":

    import sys

    vm_name = sys.argv[3]
    input("Création d'une VM du nom de '{}'\nPress Enter to continue...".format(vm_name))
    vm_comment = "Test avec l'api"
    bridge_name = 'ovs-br-adm'
    image_id = '/var/lib/libvirt/images/trusty-server-cloudimg-amd64-disk1.img'
    compute_resource_id = "3"
    domain_id = "1"
    environment_id = "1"
    hostgroup_id = "8"
    medium_id = "6"
    ptable_id = "8"
    operatingsystem_id = "1"
    puppet_ca_proxy_id = "1"
    puppet_proxy_id = "1"
    subnet_id = "1"

    sleep = 5

    payload ={
            "capabilities": "build image",
            "host": {
                "comment": vm_comment,
                "compute_attributes": {
                    "cpus":1,
                    "image_id": image_id,
                    "memory":'805306368',
                    "nics_attributes": {
                        "0": {
                            "_delete": "",
                            "bridge": "",
                            "model":'virtio',
                            "network":bridge_name,
                            "type":'network',
                        },
                        "new_nics": {
                            "_delete": "",
                            "bridge": "",
                            "model":'virtio',
                            "type":'bridge',
                        },
                    },
                    "start":1,
                    "volumes_attributes": {
                        "0": {
                            "_delete": "",
                            "allocation":'0G',
                            "capacity":'10G',
                            "format_type":'qcow2',
                            "pool_name":'default',
                        },
                        "new_volumes": {
                            "_delete": "",
                            "allocation":'0G',
                            "capacity":'10G',
                            "format_type":'raw',
                            "pool_name":'default',
                        },
                    },
                },
                "compute_resource_id":compute_resource_id,
                "domain_id":domain_id,
                "build":"true",
                "enabled":1,
                "environment_id":environment_id,
                "hostgroup_id":hostgroup_id,
                "medium_id":medium_id,
                "ptable_id":ptable_id,
                "name": vm_name,
                "operatingsystem_id":operatingsystem_id,
                "provision_method":'image',
                "puppet_ca_proxy_id":puppet_ca_proxy_id,
                "puppet_proxy_id":puppet_proxy_id,
                "puppetclass_ids":[],
                "subnet_id":subnet_id,
                "type":"Host::Managed",
                "interfaces_attributes":{
                    "new_interfaces":{
                        "_destroy":"false",
                        "attached_to": "",
                        "domain_id": "",
                        "identifier": "",
                        "ip": "",
                        "mac": "",
                        "managed":0,
                        "managed":1,
                        "name": "",
                        "subnet_id": "",
                        "tag": "",
                        "type":"Nic::Managed",
                        "virtual":0,
                    },
                },
            },
            "provider":"Libvirt",
            "utf8":"✓"
        }
    print(json.dumps(payload))

    foreman_auth = (sys.argv[1], sys.argv[2])
    foreman = ForemanAPI(foreman_auth, '192.168.1.4')
    #~ foreman.create_vm(vm_name, payload)
    future1 = foreman.create('hosts', payload, async = True)
    for i in range(0, sleep):
        time.sleep(1)
        print('Wait... {}'.format(sleep-i))
    future2 = foreman.set('hosts', vm_name, 'power', {"power_action": "start","host": {},}, async = True)
    print(future1.result())
    print(future2.result())




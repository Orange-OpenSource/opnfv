#!/usr/bin/python
# -*-coding:utf8 -*

from subprocess import check_output
import json
import collections

def hiera(key, ordered=False):
    """Ugly way to access hiera data with the hiera config file"""
    obj_pair_hook=collections.OrderedDict if ordered else None
    args = ['/usr/bin/hiera', key, '-c', '/usr/local/opensteak/infra/hiera.yaml']
    o = check_output(args,universal_newlines=True)).rstrip()

    if o == 'nil':
        return None
    else:
        try:
            i = o.replace('=>', ':')
            return json.loads(i, object_pairs_hook=obj_pair_hook)
        except:
            return o

if __name__ == "__main__":
    print("Ask value:")
    print(hiera('dns::internal'))
    print("Ask list:")
    print(hiera('dns::external'))
    print("Ask dict:")
    print(hiera('infra::nodes'))

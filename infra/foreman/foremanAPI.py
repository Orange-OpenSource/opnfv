#!/usr/bin/python3
import json
import requests
from requests_futures.sessions import FuturesSession
from pprint import pprint, pformat


class ForemanAPI:
    """
    HostGroup class
    """
    def __init__(self, auth, ip='127.0.0.1'):
        """ Function __init__
        Init the API with the connection params
        @param auth: authentication tuple (login, password)
        @param ip: api ip
        @return RETURN: self
        """
        self.base_url = 'http://{}/api/v2/'.format(ip)
        self.headers = {'Accept': 'version=2',
                        'Content-Type': 'application/json; charset=UTF-8'}
        self.auth = auth

    def list(self, obj, filter=False, only_id=False, limit=20):
        """ Function list
        Get the list of an object
        @param obj: object name ('hosts', 'puppetclasses'...)
        @param filter: filter for objects
        @param only_id: boolean to only return dict with name/id
        @return RETURN: the list of the object
        """
        self.url = self.base_url+obj+'/?per_page={}'.format(limit)
        if filter:
            self.url += '&search={}'.format(filter)
        self.resp = requests.get(url=self.url, auth=self.auth,
                                 headers=self.headers)
        if only_id:
            if self.__process_resp__(obj) is False:
                return False
            if type(self.res['results']) is list:
                return dict((x['name'], x['id']) for x in self.res['results'])
            elif type(self.res['results']) is dict:
                r = {}
                for v in self.res['results'].values():
                    for vv in v:
                        r[vv['name']] = vv['id']
                return r
            else:
                return False
        else:
            return self.__process_resp__(obj)

    def get(self, obj, id, sub_object = None):
        """ Function get
        Get an object by id
        @param obj: object name ('hosts', 'puppetclasses'...)
        @param id: the id of the object (name or id)
        @return RETURN: the targeted object
        """
        self.url = self.base_url+obj+'/{}'.format(id)
        if sub_object:
            self.url += '/'+sub_object
        self.resp = requests.get(url=self.url, auth=self.auth,
                                 headers=self.headers)
        if self.__process_resp__(obj):
            return self.res
        return False

    def get_id_by_name(self, obj, name):
        """ Function get_id_by_name
        Get the id of an object
        @param obj: object name ('hosts', 'puppetclasses'...)
        @param id: the id of the object (name or id)
        @return RETURN: the targeted object
        """
        list = self.list(obj, filter='name = "{}"'.format(name),
                         only_id=True, limit=1)
        return list[name] if len(list)>0 else False


    def set(self, obj, id, action, payload, async=False):
        """ Function set
        Set an object by id
        @param obj: object name ('hosts', 'puppetclasses'...)
        @param id: the id of the object (name or id)
        @param payload: the dict of the payload
        @param async: should this request be async, if true use
                        return.result() to get the response
        @return RETURN: the server response
        """
        self.url = self.base_url+obj+'/{}/{}'.format(id, action)
        payload = json.dumps(payload)
        if async:
            session = FuturesSession()
            return session.put(url=self.url, auth=self.auth,
                               headers=self.headers, data=payload)
        else:
            self.resp = requests.put(url=self.url, auth=self.auth,
                                     headers=self.headers, data=payload)
            if self.__process_resp__(obj):
                return self.res
            return False

    def create(self, obj, payload, async=False):
        """ Function create
        Create an new object
        @param obj: object name ('hosts', 'puppetclasses'...)
        @param payload: the dict of the payload
        @param async: should this request be async, if true use
                        return.result() to get the response
        @return RETURN: the server response
        """
        self.url = self.base_url+obj
        payload = json.dumps(payload)
        if async:
            session = FuturesSession()
            return session.post(url=self.url, auth=self.auth,
                                headers=self.headers, data=payload)
        else:
            self.resp = requests.post(url=self.url, auth=self.auth,
                                      headers=self.headers,
                                      data=payload)
            return self.__process_resp__(obj)

    def delete(self, obj, id):
        """ Function delete
        Delete an object by id
        @param obj: object name ('hosts', 'puppetclasses'...)
        @param id: the id of the object (name or id)
        @return RETURN: the server response
        """
        self.url = self.base_url+obj+'/{}'.format(id)
        self.resp = requests.delete(url=self.url,
                                    auth=self.auth,
                                    headers=self.headers, )
        return self.__process_resp__(obj)

    def __process_resp__(self, obj):
        """ Function __process_resp__
        Process the response sent by the server and store the result
        @param obj: object name ('hosts', 'puppetclasses'...)
        @return RETURN: the server response
        """
        self.last_obj = obj
        if self.resp.status_code > 299:
            self.ret = json.loads(self.resp.text)
            print(">> Error {} for object '{}'".format(self.resp.status_code,
                                                       self.last_obj))
            pprint(self.ret[list(self.ret.keys())[0]])
            return False
        self.res = json.loads(self.resp.text)
        if 'results' in self.res.keys():
            return self.res['results']
        return self.res

    def __str__(self):
        ret = pformat(self.base_url)+"\n"
        ret += pformat(self.headers)+"\n"
        ret += pformat(self.auth)+"\n"
        return ret

if __name__ == "__main__":
    import sys
    foreman_auth = (sys.argv[1], sys.argv[2])
    api = ForemanAPI(foreman_auth, "192.168.1.4")

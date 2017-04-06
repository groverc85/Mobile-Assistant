# -*- coding:utf-8 -*-

from bae_memcache import BaeMemcache
import uuid

cache_id = "yTLxNglqAjQqnvTmozrE"
cache_addr = "cache.duapp.com:20243"
api_key = "Nx80Sg2TOypzPcKRHz6P8TtE"
secret_key = "rrriA03MeG4MAkQeD5Zg8f76WDbRCjCf"

_cache = BaeMemcache(cache_id, cache_addr, api_key, secret_key)
_exception = None

import log
logger = log.getLogger('cccc')

def setcache(key, value, time = 3600):
    global _exception
    try:
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if _cache.set(key, value, time):
            return True
    except Exception as e:
        _exception = e
    return False
    
def getcache(key):
    global _exception
    try:
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        return _cache.get(key)
    except Exception as e:
        _exception = e
        return None
        
def delcache(key, time = 0):
    global _exception
    try:
        return _cache.delete(key, time)
    except Exception as e:
        _exception = e
        return False
        
def getlasterror():
    return _exception
        
def randkey(prefix = 'x'):
    return "%s-%s" % (prefix, uuid.uuid4())
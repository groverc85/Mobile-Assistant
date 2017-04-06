# -*- coding:utf-8 -*-

import requests
import sys
from . import maps
app_key = "Nx80Sg2TOypzPcKRHz6P8TtE"

'''
baidu direction api doc: http://developer.baidu.com/map/index.php?title=webapi/direction-api
'''

def GetRoutingByWalking(origin, destination, city):    
    params = {
        'mode': 'walking', 'ak': app_key, 'output': 'json',
        'origin': '%s,%s' % origin,
        'destination': '%s,%s' % destination,
        'region': city,
    }
    return requests.get("http://api.map.baidu.com/direction/v1", params = params).json()
def GetRoutingByDriving(origin, destination, city):    
    params = {
        'mode': 'driving', 'ak': app_key, 'output': 'json',
        'origin': '%s,%s' % origin,
        'destination': '%s,%s' % destination,
        'region': city,
    }
    return requests.get("http://api.map.baidu.com/direction/v1", params = params).json()
    
def GetRoutingByTransit(origin, destination, city):
    params = {
        'mode': 'transit', 'ak': app_key, 
        'output': 'json', 'region': city,
        'origin': '%s,%s' % origin, 'destination':'%s,%s' % destination,
    }   
    return requests.get("http://api.map.baidu.com/direction/v1", params = params).json()
    
def GetRoutingByTaxi(origin, destination, city):
    params = {
        'mode': 'transit', 'ak': app_key, 
        'output': 'json', 'region': city,
        'origin': '%s,%s' % origin, 'destination':'%s,%s' % destination,
    }    
    resp = requests.get('http://api.map.baidu.com/direction/v1', params = params).json()
    if resp['status'] == 0:
        if resp['type'] == 1:
            resp['status'] = 400001
            resp['message'] = u'模糊的起始点，无法查询线路'
        elif resp['type'] == 2:
            resp['result'] = resp['result']['taxi']
        del resp['type']
    return resp
    
if __name__ == '__main__':
    start = (30.270067,120.129649) #浙大玉泉校区
    end = (30.295812,120.217858)   #杭州东站
    print(GetRoutingByTransit(start, end, u'杭州'))
    #print(GetRoutingByWalking(start, end, u'杭州'))
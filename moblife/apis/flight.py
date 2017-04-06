# -*- coding: utf-8 -*-
#author:zhaolang 2015-01-08
import requests
import json
import time,datetime

def GetRoutingByPlane(origin_city, destination_city, date_time):
    #url = 'http://api.ok-api.cn:11380/Zhaolang/flightzl/2/flightzl?%s'
    url = 'http://api.open.baidu.com/pae/channel/data/asyncqury?%s'
    params = {'cb':'', 'date':date_time, 'dep': origin_city, 'arr': destination_city, 'appid': '4047', '_':'1420682712390'}
    r = requests.get(url, params = params)
    resp = json.loads(r.text)
    return resp

def GetFlightNum(flightNum):
    url = 'http://api.open.baidu.com/pae/channel/data/asyncqury?%s'
    today = datetime.date.today().strftime("%Y-%m-%d")
    params = {'cb':'', 'flightno':flightNum, 'date':today, 'appid':'4047', '_':'1420682712434'}

    r = requests.get(url, params = params)
    resp = json.loads(r.text)
    return resp

def GetNewPlane(origin_city, destination_city, date_time):
    url = 'http://api.ok-api.cn:11380/Zhaolang/flightzl/2/flightzl?%s'
    params = {'dc':origin_city,'ac':destination_city,'t':date_time}
    r = requests.get(url, params = params)
    resp = json.loads(r.text)
    return resp

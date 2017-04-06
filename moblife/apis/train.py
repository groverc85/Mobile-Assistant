# -*- coding: utf-8 -*-
#author:zhaolang 2015-01-09 16:47
import requests
import requests
import json
import time,datetime


def GetRoutingByTrain(origin_city, destination_city):
    url = 'http://apis.juhe.cn/train/s2s?%s'
    params = {'key': 'dee91d0a96e2263dde91530f0bc67424', 'dtype': 'json', 'start': origin_city, 'end': destination_city, 'sp': '', 'traintype': ''}
    r = requests.get(url, params = params)
    resp = json.loads(r.text)
    return resp

def GetTrainNum(train_num):
	url = 'http://api.ok-api.cn:11380/sunzuhan/TrainService/6/Train/' + train_num
	r = requests.get(url)
	resp = json.loads(r.text)
	return resp

def GetNewTrain(origin_city, destination_city, date_time):
	url = 'http://api.ok-api.cn:11380/coffee/testApi/6/train/s2s'
	params = {'from':origin_city, 'to':destination_city, 'date':date_time}
	r = requests.get(url, params = params)
	resp = r.json()
	return resp
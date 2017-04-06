# -*- coding: utf-8 -*-
import requests
import json
import time,datetime

def getSearchHotel(city,startTime,endTime,keyWord,star,price):
	url=""
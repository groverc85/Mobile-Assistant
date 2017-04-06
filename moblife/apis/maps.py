# -*- coding: utf-8 -*- 

import requests

app_key = "Nx80Sg2TOypzPcKRHz6P8TtE"

'''

'''

def GetLocationCity(location):
    '''
    get the city name where the location
    location: 2-tuple consists latitude and longitude
       
    >>> GetLocationCity((39.93659245,116.25595093))
    '北京市'
    '''
    params = {'ak': app_key, 'output': 'json', 'location' : '%s,%s' % location}
    resp = requests.get('http://api.map.baidu.com/geocoder/v2/', params = params).json()    
    if resp['status'] == 0:
        return resp['result']['addressComponent']['city']

def GetLocationParam(address, city = None):
    '''
    get latitude and longitude from an address
    >>> GetLocationParam(u'浙江大学玉泉校区')
    (30.275835738742, 120.13107027731)
    >>> GetLocationParam(u'沃尔玛超市', u'北京市')
    (39.914812498896, 116.47702460013)
    '''
    params = {'ak': app_key, 'output': 'json', 'address': address}
    if city:
        params['city'] = city
    resp = requests.get('http://api.map.baidu.com/geocoder/v2/', params = params).json()
    if resp['status'] == 0:
        return resp['result']['location']['lat'], resp['result']['location']['lng']

        
if __name__ == '__main__':
    print(GetLocationParam(u'青芝屋', u'杭州'))
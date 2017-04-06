# -*- coding: utf-8 -*- 

import requests

app_key = "Nx80Sg2TOypzPcKRHz6P8TtE"

def GetWeather(city):
    '''
    baidu weather api doc: http://developer.baidu.com/map/index.php?title=car/api/weather
    '''
    params = {
        'ak': app_key, 
        'output': 'json', 
        'location': city
    }
    resp = requests.get('http://api.map.baidu.com/telematics/v3/weather', params = params).json()
    return resp
    
if __name__ == '__main__':
    import pprint
    pprint.pprint(GetWeather(u'杭州'))
    pprint.pprint(GetWeather(u'永登县'))
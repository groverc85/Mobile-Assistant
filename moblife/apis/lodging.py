# -*- coding: utf-8 -*- 

import requests

app_key = "Nx80Sg2TOypzPcKRHz6P8TtE"

agent_id='6950885'
agent_md='be648f3026f6db23'

def baiduGetLodging(location,price_section):

    '''
    调用百度的酒店api
    baidu place api doc:http://developer.baidu.com/map/index.php?title=webapi/guide/webservice-placeapi    
    
    example url:http://api.map.baidu.com/place/v2/search?radius=2000&location=30.275835738742%2C120.13107027731&ak=Nx80Sg2TOypzPcKRHz6P8TtE&scope=2&output=json&page_size=10&page_num=1&query=%E9%85%92%E5%BA%97%24%E6%97%85%E5%BA%97
    '''

    params = {
        'ak': app_key, 
        'output': 'json',  
        'query': u'酒店$旅店', 
        'scope':2, 
        'page_size':20, 
        'page_num':1, 
        'location': '%s,%s' % location, 
        'radius':2000,
        'price_section':'%s' % price_section
    }

    return requests.get('http://api.map.baidu.com/place/v2/search', params = params).json()

def zhuNaHotel():
    '''
    调用住哪的酒店api
    '''
    
if __name__ == '__main__':
    import maps
    from pprint import pprint
    loc = maps.GetLocationParam(u'浙江大学玉泉校区', u'杭州市')
    pprint(baiduGetLodging(loc))
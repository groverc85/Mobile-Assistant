# -*- coding: utf-8 -*- 

import requests

app_key = "6b21db867235087b215876b4438f52bc"

def get_catering(location, radius, query):
    '''
    baidu place api doc:http://developer.baidu.com/map/index.php?title=webapi/guide/webservice-placeapi
    
    example url:http://api.map.baidu.com/place/v2/search?page_size=10&radius=2000&output=json&location=30.275835738742%2C120.13107027731&scope=2&page_num=1&ak=Nx80Sg2TOypzPcKRHz6P8TtE&query=%E9%A5%AD%E5%BA%97%24%E5%B0%8F%E5%90%83
    '''
    params = {
        'location': location, 
        'radius':radius,
        'query': query,
        'output': 'json',
        'scope':2, 
		'page_size':10, 
		'page_num':0,
        'ak': app_key,
        'industry_type': 'hotel',
        'sort_name': 'default',
        'sort_rule': 0,
    }

    return requests.get('http://api.map.baidu.com/place/v2/search', params=params).json()
    
if __name__ == '__main__':
    import maps
    from pprint import pprint
    loc = maps.GetLocationParam(u'浙江大学玉泉校区', u'杭州市')
    loc_str = '%s,%s' % (loc[0],loc[1])
    print(loc_str)
    pprint(get_catering(loc_str, 2000, u'快捷酒店'))
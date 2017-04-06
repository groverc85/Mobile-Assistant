#-*- coding:utf-8 -*-
from moblife import app
from flask import request, render_template, url_for

from moblife.apis import weather, maps, lodging, catering, flight, train, routing

from . import wechat_api

from datetime import datetime, timedelta, date
import time
import re

from moblife.models_wechat import WechatUserInfo, WechatUserLoc

def rating_stars(f):
    f = float(f)
    n = int(round(f))
    d = u'★' * n
    w = u'☆' * (5 - n)
    return ''.join( [d, w, ' (%.1f/5)' % f] )

class Message(wechat_api.MessageBase):

    def __init__(self, content):
        self.user = None
        self.user_location = None
        super(Message, self).__init__(content)
        
    # common protocols, s is the detail semantic
    def common_datetime(self, s, type = 0):
        pass
        if type == 0:
            return ' '.join( [obj['date'], obj['time']] )
        elif type == 1:
            return obj['date'] # YYYY-MM-DD default to today
        elif type == 2:
            return obj['time'] # HH:MM:SS defalut to 00:00:00
    def common_location(self, s):
        pass
    def common_number(self, s):
        pass

    # vertical services protocols, s is the detail semantic
    def service_flight(self, s): 
        s = s['details']
        if 'start_loc' in s and 'end_loc' in s:
            origin = s['start_loc']['city_simple']
            destination = s['end_loc']['city_simple']
            if 'start_date' in s:
                dt = s['start_date']['date']
            else:
                dt = date.today().strftime("%Y-%m-%d")
            self.reply_flight(origin, destination, dt)        

        else:
            self.reply_text(u'起止城市不明确')
    def service_map(self, s):
        intent = s['intent']
        s = s['details']
        city = self.user.city
        start, end = '',''
        if 'start_area' in s:
            start += s['start_area']['loc_ori']
        if 'start_loc' in s:
            start += s['start_loc']['loc_ori']
        if 'end_area' in s:
            end += s['end_area']['loc_ori']
        if 'end_loc' in s:
            end += s['end_loc']['loc_ori']
        start_cor, end_cor = None, None
        if start:
            start_cor = maps.GetLocationParam(start, city)
        if end:
            end_cor = maps.GetLocationParam(end, city)        
        if intent == 'SEARCH':
            if start_cor:
                self.reply_location(start, start_cor[0], start_cor[1])
            elif end_cor:
                self.reply_location(end, end_cor[0], end_cor[1])
            else:
                self.reply_text(u'您所要查询的位置不明确')
        elif intent == 'ROUTE':
            if not start_cor:
                if self.user_location:
                    start_cor = (self.user_location.latitude, self.user_location.longitude)
                else:
                    return self.reply_text(u'无法获取您当前位置，请允许微信号获取地理位置或者指定出发地')
            if not end_cor:
                self.reply_text(u'您所要去的目的地不清楚')
                return
            pref = 'bus'
            if 'route_type' in s:
                pref = s['route_type']
            if pref == 'taxi':
                route = routing.GetRoutingByTaxi(start_cor, end_cor, city)
                if route['status'] == 0:
                    route = route['result']
                    info = u'距离:%s公里\n耗时:%s分钟' % (route['distance']/1000, route['duration']/60)
                    price = []
                    for d in route['detail']:
                        price.append(u'%s元(%s)' % (d['total_price'], d['desc']))
                    article = {
                        'title': u'从%s打的至%s' % (start,end),
                        'description': u'%s\n价格：%s\n备注：%s' % (info, ','.join(price), route['remark']),
                        'url': url_for('.index', _external = True)
                    }
                    return self.reply_news([article])
                else:
                    self.reply_text(u'未能查到打的线路及费用')
            elif pref == 'bus':
                route = routing.GetRoutingByTransit(start_cor, end_cor, city)
                if route['status'] == 0:
                    route = route['result']
                    articles = [{
                        'title': u'从%s至%s的公交线路' % (start,end),
                        'picurl': url_for('.static', filename = 'images/wechat/routing.jpg', _external = True)
                    }]
                    cnt = 0
                    for path in route['routes']:
                        if cnt >= 6:
                            break
                        cnt += 1
                        path = path['scheme'][0]
                        duration = path['duration']
                        walk_meters = 0
                        transit = []
                        for step in path['steps']:
                            step = step[0]
                            if step['type'] == 5:
                                walk_meters += step['distance']
                            elif step['type'] == 3:
                                transit.append(step['vehicle']['name'])
                        t1 = u'公交线：%s' % '->'.join(transit)
                        t4 = u'换乘：%s' % (len(transit) - 1)
                        t2 = u'耗时：%s分钟' % (duration / 60)
                        t3 = u'步行：%s米' % walk_meters
                        article = {
                            'title': '\n'.join([t1, t2, t3]),
                            'url': url_for('.index', _external = True),
                            'picurl': url_for('.static', filename = 'images/wechat/bus.png', _external = True)
                        }
                        articles.append(article)
                    taxi = route['taxi']
                    info = u'%s公里\n耗时：%s分钟' % (taxi['distance']/1000, taxi['duration']/60)
                    price = []
                    for d in taxi['detail']:
                        price.append(u'%s元(%s)' % (d['total_price'], d['desc']))                
                    articles.append({
                        'title': u'打车：%s\n价格：%s' % (info,','.join(price)),
                        'url': url_for('.index', _external = True),
                        'picurl': url_for('.static', filename = 'images/wechat/taxi.png', _external = True)
                    })
                    return self.reply_news(articles)
                else:
                    return self.reply_text(u'未能查到公交线路及费用')    
            elif pref == 'drive':
                route = routing.GetRoutingByDriving(start_cor, end_cor, city)
                if route['status'] == 0:
                    route = route['result']
                    articles = [{
                        'title': u'从%s至%s的驾车线路' % (start,end),
                        'picurl': url_for('.static', filename = 'images/wechat/routing.jpg', _external = True)
                    }]
                    cnt = 0
                    for path in route['routes']:
                        if cnt >= 6:
                            break
                        cnt += 1
                        distance = path['distance']
                        duration = path['duration']
                        toll = path['toll']
                        article = {
                            'title': u'距离：%s公里\n耗时：%s分钟\n过路费：%s元' % (distance / 1000, duration /60, toll),
                            'url': url_for('.index', _external = True),
                            'picurl': url_for('.static', filename = 'images/wechat/taxi.png', _external = True)
                        }
                        articles.append(article)
                    taxi = route['taxi']
                    info = u'%s公里\n耗时：%s分钟' % (taxi['distance']/1000, taxi['duration']/60)
                    price = []
                    for d in taxi['detail']:
                        price.append(u'%s元(%s)' % (d['total_price'], d['desc']))                
                    articles.append({
                        'title': u'打车：%s\n价格：%s' % (info,','.join(price)),
                        'url': url_for('.index', _external = True),
                        'picurl': url_for('.static', filename = 'images/wechat/taxi.png', _external = True)
                    })
                    return self.reply_news(articles)
                else:
                    return self.reply_text(u'未能查到驾车线路')
            elif pref == 'walk':
                route = routing.GetRoutingByWalking(start_cor, end_cor, city)
                if route['status'] == 0:
                    route = route['result']
                    path = []
                    for p in route['routes']:
                        path.append((p['distance'], p['duration']))
                    path = list(sorted(path))
                    text = u'步行从%s到%s共有%s条线路，最近的一条%s米，耗时%s分钟' % (start, end, len(route['routes']), path[0][0], path[0][1] / 60)
                    return self.reply_text(text)
                else:
                    return self.reply_text(u'未能查到步行线路')
            self.reply_text(u'查询线路，方式%s' % pref)

    def service_hotel(self, s):
        if s['details'] is None:
            self.reply_text(u'您的语义类型为酒店服务，但是没有具体的语义结果。')
            return
        s = s['details']
        if 'location' in s and 'poi' in s['location']:
            city = s['location']['city_simple'] if 'city_simple' in s['location'] else self.user.city
            location = maps.GetLocationParam(s['location']['poi'], city)
        else:
            location = self.user_location

        price_section = '300'
        # process returned object from logding api
        r = lodging.baiduGetLodging(location, price_section)
        if r['status'] != 0:
            self.reply_text(u'获取酒店列表失败')
            return
        news = [{
            'title' : u'酒店查询结果共有 %d 条' % r['total'],
            'description' : u'查看详情',
            'picurl': url_for('.static', filename = 'images/wechat/hotel.jpg', _external = True),
            'url': url_for('.basic_hotel_list', lat = location[0], lon = location[1], price = price_section, _external = True)
        }]
        cnt = 0
        for item in r['results']:
            if cnt >= 5:
                break
            cnt += 1
            try:
                p = u'价格：%s' % item['detail_info']['price']
                r_overall = u'总体评分：%s' % rating_stars(item['detail_info']['overall_rating'])
                detail = u'，'.join( [p, r_overall] )
            except:
                continue
            a_item = {
                'title': '\n'.join( [item['name'], item['address'], detail] ),
                'description': u'待我细细道来。',
                'picurl': url_for('.static', filename = 'images/wechat/hotel.jpg', _external = True),
                'url': item['detail_info']['detail_url']
            }
            news.append(a_item)
        self.reply_news(news)

    def service_weather(self, s):
        s = s['details']
        if s is None:
            self.reply_text(u'请您精确说明您查询天气的时间，比如“后三天”')
            return 
        if 'location' in s and 'city_simple' in s['location']:
            city = s['location']['city_simple']
        else:
            city = self.user.city
        dates = []
        today = datetime.today().date()
        if 'datetime' in s:
            d = s['datetime']
            if d['type'] in ['DT_SINGLE', 'DT_ORI', 'DT_INFER']:
                dt = datetime.strptime(d['date'], '%Y-%m-%d').date()
                interval = (dt - today).days
                if interval >= 0 and interval <= 4:
                    dates.append(interval)
            elif d['type'] == 'DT_INTERVAL':
                start = datetime.strptime(d['date'], '%Y-%m-%d').date()
                end = datetime.strptime(d['end_date'], '%Y-%m-%d').date()
                for i in range((end - start).days + 1):
                    dt = start + timedelta(days = i)
                    interval = (dt - today).days
                    if interval >= 0 and interval <= 4:
                        dates.append(interval)
            if len(dates) == 0:
                self.reply_text(u'只能查到今天到4天以内的天气情况')
                return
        else:
            dates.append(0)
        self.reply_weather(city, dates)
    def reply_train(self, origin, destination, dt):
        resp = train.GetRoutingByTrain(origin, destination)
        count = len(resp['result']['data'])
        if resp['result']['data']:
            articles = [
                {
                    'title' : u'%s至%s列车共%s辆' % (origin, destination, count),
                    'description' : u'查看详情',
                    'picurl': url_for('.static', filename='images/wechat/train.jpg', _external = True),
                    'url': url_for('.train_list', origin= origin, destination = destination)
                }]
            i = 0
            for info in resp['result']['data']:
                i = i+1
                if i > 5:
                    break
                article = {
                    'title': "%s\t%s-%s\n%s-%s" % (info['trainOpp'], info['leave_time'], info['arrived_time'], info['start_staion'], info['end_station']),
                    'description' : '',
                    'picurl': url_for('.static', filename = 'images/wechat/train_common.jpg', _external = True), 
                    'url': url_for('.index', _external = True)
                }
                articles.append(article)
            self.reply_news(articles)
        else:
            self.reply_text(u'查询不到结果！')
    def reply_flight(self, origin, destination, dt):
        resp = flight.GetRoutingByPlane(origin, destination, dt)
        count = len(resp['data'])
        if resp['data']:
            articles = [
                {
                    'title' : u'%s%s至%s航班共%s条' % (dt, origin, destination, count),
                    'description' : u'查看详情',
                    'picurl': url_for('.static', filename = 'images/wechat/plane.jpg', _external = True), 
                    'url': url_for('.plane_list', origin = origin, destination = destination, dt = dt, _external = True)
                }]
            i = 0
            for info in resp['data']:
                i = i+1
                if i > 5:
                    break
                article = {
                    'title': "%s\t%s-%s\n%s-%s" % (info['flightNO'], info['planDptTime'][11:], info['planArrTime'][11:], info['dptAirport'], info['arrAirport']),
                    'description' : '',
                    'picurl': 'http://pic.c-ctrip.com/flight_intl/airline_logo/40x35/%s.png' % info['flightNO'][:2],
                    'url': url_for('.plane_detail', flightNum = info['flightNO'], _external = True)
                }
                articles.append(article)
            self.reply_news(articles)
        else:
            self.reply_text(u'查询不到结果！')
    def reply_weather(self, city, days):
        today = datetime.today().date()
        resp = weather.GetWeather(city)
        if resp['error'] != 0:
            self.reply_text(u'天气服务暂时不可用,原因:%s' % resp['status'])
        else:
            resp = resp['results'][0]
            rt = resp['weather_data'][0]['date']
            articles = [
                {
                    'title' : u'%s天气查询 %s' % (city, rt),
                    'description' : u'查看详情',
                    'picurl': url_for('.static', filename = 'images/wechat/weather.jpg', _external = True), 
                    'url': url_for('.index')
                }]
            for i in days:
                if i < 0 or i >= len(resp['weather_data']):
                    break
                wd = resp['weather_data'][i]
                if i == 0:
                    d = u'今天'
                elif i == 1:
                    d = u'明天'
                elif i == 2:
                    d = u'后天'
                else:
                    d = u'%s月%s日' % ((today + timedelta(i)).month, (today + timedelta(i)).day)
                article = {
                    'title': "%s\t%s,%s\n%s" % (d, wd['temperature'],wd['weather'],wd['wind']),
                    'description' : '',
                    'picurl': wd['dayPictureUrl'],
                    'url': url_for('.index')
                }
                articles.append(article)
            self.reply_news(articles)
    
    def reply_location(self, addr, lon, lat):
        article = {
            'title': addr,
            'description': '',
            'picurl': 'http://api.map.baidu.com/staticimage?width=360&heigth=200&center=%s,%s&zoom=15' % (lat, lon),
            'url': url_for('.index')
        }
        self.reply_news([article])
        
    def service_train(self, s):
        s = s['details']
        if 'start_loc' in s and 'end_loc' in s:
            origin = s['start_loc']['city_simple']
            destination = s['end_loc']['city_simple']
            if 'start_date' in s:
                dt = s['start_date']['date']
            else:
                dt = date.today().strftime("%Y-%m-%d")
            self.reply_train(origin, destination, dt)        

        else:
            self.reply_text(u'起止城市不明确')
    def service_nearby(self, s):
        pass
    def service_restaurant(self, s):
        if s['details'] is None:
            self.reply_text(u'您的语义类型为饭店服务，但是没有具体的语义结果。')
            return
        s = s['details']
        if 'location' in s and 'poi' in s['location']:
            city = s['location']['city_simple'] if 'city_simple' in s['location'] else self.user.city
            location = maps.GetLocationParam(s['location']['poi'], city)
        else:
            location = self.user_location
        price_section = '100'
        # process returned object from logding api
        r = catering.baiduGetCatering(location, price_section)
        if r['status'] != 0:
            self.reply_text(u'获取饭店列表失败')
            return
        news = [{
            'title' : u'饭店查询结果共有 %d 条' % r['total'],
            'description' : u'查看详情',
            'picurl': url_for('.static', filename = 'images/wechat/restaurant.jpg', _external = True),
            'url': url_for('.basic_catering_list', lat = location[0], lon = location[1], price = price_section,_external = True)
        }]
        cnt = 0

        for item in r['results']:
            if cnt >= 5:
                break;
            cnt += 1
            try:
                p = u'价格：%s' % item['detail_info']['price']
                r_overall = u'总体评分：%s' % rating_stars(item['detail_info']['overall_rating'])
                detail = u'，'.join( [p, r_overall] )
            except:
                continue
            a_item = {
                'title': '\n'.join( [item['name'], item['address'], detail] ),
                'description': u'待我细细道来。',
                'picurl': url_for('.static', filename = 'images/wechat/restaurant.jpg', _external = True),
                'url': item['detail_info']['detail_url']
            }
            news.append(a_item)
        self.reply_news(news)


    def analyze(self, text):
    
        if self.user_location:
            lat = self.user_location.latitude
            lon = self.user_location.longitude
        else:
            lat = None
            lon = None
            
        s = wechat_api.get_semantic(text, uid = self.user.openid, lat = lat, lon = lon,city=self.user.city, category=['map','weather','restaurant','hotel','flight','train'])
        if 'errcode' in s :
            if s['errcode'] == 0:
                self.reply_text(u'我知道了，您需要服务%s. \n我们还没有推出此项服务...程序员正在努力中...' % s['type'])
                try:
                    eval('self.service_%s' % s['type'])(s['semantic'])
                except Exception as e:
                    self.reply_text(u'处理%s时发生了异常：\n%s' % (s['type'], e))
                return
            if s['errcode'] == 45000:
                self.reply_text(u'我无法理解您的意思：%s' % text)
                return
            if 'errmsg' in s:
                msg = '%s(%s)' % (s['errmsg'], s['errcode'])
            else:
                msg = '(%s)' % s['errcode']
            self.reply_text(u'语义理解服务出现了问题，原因%s' % msg)
            return
        else:
            self.reply_text(u'语义理解服务出现了问题，返回值%s' % s)


    def detect_semantic(self, text):
        # text containing only chinese characters is considered valid
        #r = re.match(ur'[\u4e00-\u9fa5]+', text.decode('utf8'))
        r = len(text) >= 5
        return r
    
    def on_message(self):
        user = WechatUserInfo.query_by_openid(self.from_id)
        if user is None:
            info = wechat_api.get_user_info(self.from_id)
            user = WechatUserInfo.insert(info)
        loc = WechatUserLoc.query_by_openid(self.from_id)
            
        self.user = user
        self.user_location = loc

    def on_text(self):
        if self.detect_semantic(self.text):
            self.analyze(self.text)
        else:
            self.reply_text(u'您输入的内容包含乱码，或者并无明确的语义！')

    def on_voice(self):
        if not self.recognition:
            self.reply_text(u'抱歉，您没有输入任何语音信息或者您的手机暂不支持语音识别功能。')
        else:            
            self.analyze(self.recognition)
    def event_click(self):
        if self.click_key == 'basic_weather':
            if self.user_location:
                city = maps.GetLocationCity((self.user_location.latitude, self.user_location.longitude))
            else:
                city = self.user.city
            self.reply_weather(city, range(7))
    
    def event_location(self):
        WechatUserLoc.insert(self.from_id, self.loc_lat, self.loc_lon)
        self.reply_text('you sent a location event, and we have record it to our database')

    def event_subscribe(self):
        info = wechat_api.get_user_info(self.from_id)
        if self.user == None:
            WechatUserInfo.insert(info)
        else:
            if WechatUserInfo.update(self.from_id, info) == False:
                pass
                #self.reply_text(u'用户信息更新失败')
        self.reply_text(u'欢迎您关注移动生活小秘书!')

    def event_unsubscribe(self):
        info = wechat_api.get_user_info(self.from_id)
        if WechatUserInfo.update(self.from_id, info) == False:
            pass
            #self.reply_text(u'用户信息更新失败')


@app.route('/wechat', methods=['POST', 'GET'])
def wechat():
  signature = request.args.get('signature', '')
  timestamp = request.args.get('timestamp', '')
  nonce = request.args.get('nonce', '')
  if not wechat_api.check_signature(signature, timestamp, nonce):
    return "Messages not From Wechat"
  if request.method == 'POST':
    msg = Message(request.data)
    return msg.reply() 
  return request.args.get('echostr', '')
  

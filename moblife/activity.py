#-*- coding:utf-8 -*-

import threading, sys, json, traceback, urllib
from datetime import datetime, timedelta

from flask import render_template, url_for, redirect, request, session, flash
from sqlalchemy import asc
from functools import wraps

import moblife
from moblife import app, wechat_api
from moblife.service import *
from moblife.models import User
from moblife.models_wechat import WechatUserInfo, WechatUserLoc
from moblife.models_activity import ActTour, ActPref, Timeline, db

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        state = request.args.get('state')
        code = request.args.get('code')
        #state = request.args.get('state')
        if state == 'from_wechat' and code:
            resp = wechat_api.get_web_token(code)
            openid = resp['openid']
            user = WechatUserInfo.query_by_openid(openid)
            nickname = user.nickname
            sex = user.sex
            country = user.country
            province = user.province
            city = user.city
            user_record = User.query.filter_by(openid=openid).first()
            if not user_record:
                user=User('', openid, '', nickname, '', sex, '', '', False, '', False, country, province, city)
                db.session.add(user)
                db.session.commit()
                user_record = User.query.filter_by(openid=openid).first()
            session['user'] = {
                #'subscribe': user.subscribe,
                'userid': user_record.id,
                'nickname': user_record.nickname,
                'sex': user_record.sex,
                'country': user_record.country,
                'province': user_record.province,
                'city': user_record.city,
                #'language': user.language,
                #'headimgurl': user.headimgurl,
                #'subscribe_time': user.subscribe_time
            }
        if 'user' not in session:
            ua = request.headers.get('User_Agent', '').lower()
            if 'micromessenger' in ua:
                request_url = urllib.quote(request.url, '')
                redirect_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx205afe2dc89bf1bb&redirect_uri=%s&response_type=code&scope=snsapi_base&state=from_wechat#wechat_redirect' % request_url
                return redirect(redirect_url)
            else:
                # request_url = urllib.quote(request.url, '')
                flash(u'请用微信扫描二维码，关注公共号/或登录后进入', 'message')
                return redirect(url_for('.login', request_url=request.url))
        return f(*args, **kwargs)

    return decorated_function

def act_list():
    user = session['user']
    acts = []
    records = ActTour.query.filter_by(userid=user['userid']).order_by(asc(ActTour.id )).all()
    for record in records:
        act = {
            'id': record.id,
            'userid': record.userid,
            'title': record.title,
            'note': record.note,
            'start_city': record.start_city,
            'start_address': record.start_address,
            'dest_city': record.dest_city,
            'dest_address': record.dest_address,
            'begin_datetime': record.begin_datetime,
            'end_datetime': record.end_datetime,
            #'timeline': record.timeline
        }
        acts.append(act)
    return render_template('act_list.html', user=user, acts=acts)
    
@app.route('/act/new/', methods=['GET', 'POST'])
@login_required
def act_new():
    if request.method == 'GET':
        actid = request.args.get('actid')
        #print(actid)
        if actid:
            user = session['user']
            record =  ActTour.query.filter_by(id=actid, userid=user['userid']).first()
            #print(record.title)
            act = {
                'id': record.id,
                'title': record.title,
                'note': record.note,
                # 'start_city': record.start_city,
                'start_address': record.start_address,
                # 'dest_city': record.dest_city,
                'dest_address': record.dest_address,
                'begin_datetime': record.begin_datetime,
                'end_datetime': record.end_datetime,
                # 'timeline': record.timeline,
            }
        else:
            user = session['user']
            begin_datetime = datetime.now()+timedelta(days=3)
            begin_datetime_str = begin_datetime.strftime('%Y-%m-%d %H:%M')
            end_datetime = datetime.now()+timedelta(days=5)
            end_datetime_str = end_datetime.strftime('%Y-%m-%d %H:%M')
            openid = User.query.filter_by(id=user['userid'])
            user_loc = WechatUserLoc.query_by_openid(openid=openid)
            if user_loc:
                addr_info = coor_to_addr(user_loc.latitude, user_loc.longitude, 'wgs84ll')
                start_address = addr_info['formatted_address']
            else:
                start_address = u'杭州市 西湖区 浙江大学玉泉校区'
            act = {
                'id': None,
                'title': u'出差',
                'note': '',
                # 'start_city': user['city'],
                'start_address': start_address,
                # 'dest_city': u'北京',
                'dest_address': u'北京市 海淀区 清华大学',
                'begin_datetime': begin_datetime_str,
                'end_datetime': end_datetime_str,
                #'timeline': None,
            }
        return render_template('act_creat.html', user=user, act=act)
        
    if request.method == 'POST':
        #从session获得openid
        user = session['user']
        userid = user['userid']
        title = request.form.get('title')
        note = request.form.get('note')
        #start_city = request.form.get('start_city')
        start_address = request.form.get('start_address')
        #dest_city = request.form.get('dest_city')
        dest_address = request.form.get('dest_address')
        begin_datetime = request.form.get('begin_datetime')
        end_datetime = request.form.get('end_datetime')
        #timeline = request.form['timeline']
        start_city = get_city(start_address)
        dest_city = get_city(dest_address)
        id = request.form.get('id')
        if id:
            record =  ActTour.query.filter_by(id=id, userid=userid).first()
            #record.id = id
            #record.userid = userid
            record.title = title
            record.note = note
            record.start_city = start_city
            record.start_address = start_address
            record.dest_city = dest_city
            record.dest_address = dest_address
            record.begin_datetime = begin_datetime
            record.end_datetime = end_datetime
        else:
            record = ActTour(userid, title, note, start_city, start_address, dest_city, dest_address, begin_datetime, end_datetime, False)
            db.session.add(record)
        try:
            db.session.commit()

            # generate timeline for act
            act = {
                'id': record.id,
                'userid': record.userid,
                'title': record.title,
                'note': record.note, 
                'start_city':  record.start_city,
                'start_address': record.start_address,
                'dest_city': record.dest_city,
                'dest_address': record.dest_address,
                'begin_datetime': record.begin_datetime,
                'end_datetime': record.end_datetime,
                #'timeline': timeline
            }
            act_pref = ActPref.query.filter_by(userid=userid).first()
            #return json.dumps(act_pref)
            try:
                leave_result = get_leave_timeline(act, act_pref)
                leave_timeline = leave_result[0]
                leave_traffics = leave_result[1]
                hotels = leave_result[2]
                restaurants = leave_result[3]

                return_result = get_return_timeline(act, act_pref)
                return_timeline = return_result[0]
                return_traffics = leave_result[1]

                db.session.remove()
                leave_timeline_record = Timeline.query.filter_by(userid=userid, actid=act['id'], leave_return=True).first()
                return_timeline_record = Timeline.query.filter_by(userid=userid, actid=act['id'], leave_return=False).first()
                if leave_timeline_record:
                    leave_timeline_record.timeline = json.dumps(leave_timeline)
                    leave_timeline_record.main_traffics = json.dumps(leave_traffics)
                    leave_timeline_record.hotels = json.dumps(hotels)
                    leave_timeline_record.restaurants = json.dumps(restaurants)
                else:
                    leave_timeline_record = Timeline(userid, act['id'], True,
                        json.dumps(leave_timeline), json.dumps(leave_traffics),
                        json.dumps(hotels), json.dumps(restaurants))
                    db.session.add(leave_timeline_record)
                if return_timeline_record:
                    return_timeline_record.timeline = json.dumps(return_timeline)
                    return_timeline_record.main_traffics = json.dumps(return_traffics)
                else:
                    return_timeline_record = Timeline(userid, act['id'], False,
                        json.dumps(return_timeline), json.dumps(return_traffics), '', '')
                    db.session.add(return_timeline_record)

                db.session.commit()                
                return act_list()
            except:
                error = traceback.format_exc()
                return 'get timeline error: %s' % error
        except Exception as e:
            db.session.rollback()
            return str(e)
        
@app.route('/act/mine/', methods=['GET', 'POST'])
@login_required
def act_mine():
    if request.method == 'GET':
        return act_list()

@app.route('/help/act/', methods=['GET', 'POST'])
@login_required
def help_act():
    if request.method == 'GET':
        return 'help about act'

@app.route('/act/pref/', methods=['GET', 'POST'])
@login_required
def act_pref():
    if request.method == 'GET':
        user = session['user']
        record =  ActPref.query.filter_by(userid=user['userid']).first()
        if record:
            pref = {
                'userid': record.userid,
                # leave,
                'leave_main_traffic': record.leave_main_traffic,
                'leave_start_traffic': record.leave_start_traffic,
                'leave_dest_traffic': record.leave_dest_traffic,
                # return,
                'return_main_traffic': record.return_main_traffic,
                'return_start_traffic': record.return_start_traffic,
                'return_dest_traffic': record.return_dest_traffic,
                
                'wait_bus_buffer': record.wait_bus_buffer,
                'wait_taxi_buffer': record.wait_taxi_buffer,
                # for train,
                'train_qos': record.train_qos,
                'train_type': record.train_type,
                'wait_train_buffer': record.wait_train_buffer,
                # for flight,
                'flight_qos': record.flight_qos,
                'flight_company': record.flight_company,
                'wait_flight_buffer': record.wait_flight_buffer,
                # hotel,
                'hotel': record.hotel,
                'hotel_radius': record.hotel_radius,
                'check_in_buffer': record.check_in_buffer,
                'check_out_buffer': record.check_out_buffer,
                # restaurant,
                'restaurant': record.restaurant,
                'restaurant_radius': record.restaurant_radius,
                'meal_buffer': record.meal_buffer,
                'wait_act_buffer': record.wait_act_buffer,
            }
        else:
            pref = {
                'userid': user['userid'],
                # leave,
                'leave_main_traffic': 'train',
                'leave_start_traffic': 'taxi',
                'leave_dest_traffic': 'taxi',
                # return,
                'return_main_traffic': 'train',
                'return_start_traffic': 'taxi',
                'return_dest_traffic': 'taxi',
                
                'wait_bus_buffer': 30,
                'wait_taxi_buffer': 20,
                # for train,
                'train_qos': '111',
                'train_type': 'GCDZTK1234567890',
                'wait_train_buffer': 60,
                # for flight,
                'flight_qos': '111',
                'flight_company': 'CA,CZ,MU,BK,JD,GJ,9C,EU,CN,DZ,NS,HU,G5,HO,KY,QW,3U,SC,ZH,FM,GS,PN,TV,JR,MF,8L,YI,KN',
                'wait_flight_buffer': 120,
                # hotel,
                'hotel': u'快捷酒店$三星级酒店$旅馆',
                'hotel_radius': 2000,
                'check_in_buffer': 30,
                'check_out_buffer': 30,
                # restaurant,
                'restaurant': u'中餐馆$西餐厅',
                'restaurant_radius': 2000,
                'meal_buffer': 60,
                'wait_act_buffer': 30,
            }
        return render_template('act_pref.html', user=user, pref=pref)
        
    if request.method == 'POST':
        #从session获得userid
        user = session['user']
        userid = user['userid']

        # leave
        leave_main_traffic = request.form.get('leave_main_traffic')
        leave_start_traffic = request.form.get('leave_start_traffic')
        leave_dest_traffic = request.form.get('leave_dest_traffic')
        # return
        return_main_traffic = request.form.get('return_main_traffic')
        return_start_traffic = request.form.get('return_start_traffic')
        return_dest_traffic = request.form.get('return_dest_traffic')
        
        wait_bus_buffer = request.form.get('wait_bus_buffer')
        wait_taxi_buffer = request.form.get('wait_taxi_buffer')
        # for train
        train_qos = request.form.get('train_price')+request.form.get('train_depart_time')+request.form.get('train_duration')
        train_type = request.form.get('train_type_')
        wait_train_buffer = request.form.get('wait_train_buffer')
        # for flight
        flight_qos = request.form.get('flight_price')+request.form.get('flight_depart_time')+request.form.get('flight_ontime_rate')
        flight_company = request.form.get('flight_company_')
        wait_flight_buffer = request.form.get('wait_flight_buffer')
        # hotel
        hotel = request.form.get('hotel_')
        hotel_radius = request.form.get('hotel_radius')
        check_in_buffer = request.form.get('check_in_buffer')
        check_out_buffer = request.form.get('check_out_buffer')
        # restaurant
        restaurant = request.form.get('restaurant_')
        restaurant_radius = request.form.get('restaurant_radius')
        meal_buffer = request.form.get('meal_buffer')
        wait_act_buffer = request.form.get('wait_act_buffer')

        record =  ActPref.query.filter_by(userid=user['userid']).first()
        if record:
            record.userid = userid
            # leave
            record.leave_main_traffic = leave_main_traffic
            record.leave_start_traffic = leave_start_traffic
            record.leave_dest_traffic = leave_dest_traffic
            # return
            record.return_main_traffic = return_main_traffic
            record.return_start_traffic = return_start_traffic
            record.return_dest_traffic = return_dest_traffic
            
            record.wait_bus_buffer = wait_bus_buffer
            record.wait_taxi_buffer = wait_taxi_buffer
            # for train
            record.train_qos = train_qos
            record.train_type = train_type
            record.wait_train_buffer = wait_train_buffer
            # for flight
            record.flight_qos = flight_qos
            record.flight_company = flight_company
            record.wait_flight_buffer = wait_flight_buffer
            # hotel
            record.hotel = hotel
            record.hotel_radius = hotel_radius
            record.check_in_buffer = check_in_buffer
            record.check_out_buffer = check_out_buffer
            # restaurant
            record.restaurant = restaurant
            record.restaurant_radius = restaurant_radius
            record.meal_buffer = meal_buffer
            record.wait_act_buffer = wait_act_buffer
        else:
            act_pref = ActPref(userid, leave_main_traffic, leave_start_traffic, leave_dest_traffic, 
                 return_main_traffic, return_start_traffic, return_dest_traffic,
                 wait_bus_buffer, wait_taxi_buffer, train_qos, train_type, wait_train_buffer,
                 flight_qos, flight_company, wait_flight_buffer, hotel, hotel_radius,
                 check_in_buffer, check_out_buffer, restaurant, restaurant_radius,
                 meal_buffer, wait_act_buffer)
            db.session.add(act_pref)
        try:
            db.session.commit()
            flash(u'偏好设置成功', 'message')
            return redirect(url_for('.act_pref'))
        except Exception as e:
            db.session.rollback()
            return str(e)


@app.route('/act/service/', methods=['GET', 'POST'])
@login_required
def service():
    if request.method == 'GET':
        #actid = 1
        actid = request.args.get('actid')
        user = session['user']
        act =  ActTour.query.filter_by(id=actid, userid=user['userid']).first()
        leave_timeline_record = Timeline.query.filter_by(userid=user['userid'], actid=actid, leave_return=True).first()
        return_timeline_record = Timeline.query.filter_by(userid=user['userid'], actid=actid, leave_return=False).first()
        if leave_timeline_record:
            leave_timelineid = leave_timeline_record.id
            leave_timeline = json.loads(leave_timeline_record.timeline)
            if leave_timeline_record.main_traffics:
                leave_traffics = json.loads(leave_timeline_record.main_traffics)
                hotels = json.loads(leave_timeline_record.hotels)
                restaurants = json.loads(leave_timeline_record.restaurants)
            else:
                leave_traffics = []
                hotels = []
                restaurants = []
        else:
            leave_timelineid = None
            leave_timeline = []
        if return_timeline_record:
            return_timelineid = return_timeline_record.id
            return_timeline =  json.loads(return_timeline_record.timeline)
            if return_timeline_record.main_traffics:
                return_traffics = json.loads(return_timeline_record.main_traffics)
            else:
                return_traffics = []
        else:
            return_timelineid = None
            return_timeline = []
        if leave_timeline or return_timeline:
            return render_template('act_composition.html', user=user, act=act,
                leave_timelineid=leave_timelineid, return_timelineid=return_timelineid,
                leave_timeline=leave_timeline, return_timeline=return_timeline,
                leave_traffics=leave_traffics, hotels=hotels,
                restaurants=restaurants, return_traffics=return_traffics)
        else:
            # flash(u'请从活动列表访问该页面', 'message')
            return '<h3 style="text-align:center">请从活动列表访问该页面</h3>'

    if request.method == 'POST':
        user = session['user']
        hotelid = request.form.get('nowhotelid')
        actid = request.form.get('actid')
        leave_timeline_record = Timeline.query.filter_by(userid=user['userid'], actid=actid, leave_return=True).first()
        if leave_timeline_record:
            leave_timeline = json.loads(leave_timeline_record.timeline)
            hotels = json.loads(leave_timeline_record.hotels)
            for i in range(len(leave_timeline)):
                if leave_timeline[i]['type'] == 'hotel':
                    leave_timeline[i]["detail"] = hotels[int(hotelid)]
                    leave_timeline[i]["hotelid"] = hotelid
                    break
            leave_timeline_record.timeline = json.dumps(leave_timeline)
            db.session.commit()
            return 'success'

@app.route('/direction/', methods=['GET', 'POST'])
@login_required
def direction():
    if request.method == 'GET':
        user = session['user']
        leave_timelineid = request.args.get('leave_timelineid')
        if leave_timelineid:
            timelineid = leave_timelineid
        return_timelineid = request.args.get('return_timelineid')
        if return_timelineid:
            timelineid = return_timelineid
        traffic_type = request.args.get('traffic_type')
        timeline_record = Timeline.query.filter_by(userid=user['userid'], id=timelineid).first()
        #print(timelineid)
        item_json = json.loads(timeline_record.timeline)
        item = item_json[-1]
        #print(item)
        start_from_address = 'name:%s|latlng:%s' % (item['start_from_address'], item['start_from'])
        start_to_address = 'name:%s|latlng:%s' % (item['start_to_address'], item['start_to'])
        dest_from_address = 'name:%s|latlng:%s' % (item['dest_from_address'], item['dest_from'])
        dest_to_address = 'name:%s|latlng:%s' % (item['dest_to_address'], item['dest_to'])

        region = ''
        origin_region = ''
        destination_region = ''

        if 'start_bus' in traffic_type:
            region = item['start_region']
            origin = start_from_address
            destination = start_to_address
            mode = 'transit'
        elif 'start_taxi' in traffic_type:
            region = item['start_region']
            origin = start_from_address
            destination = start_to_address
            mode = 'driving'
        elif 'start_driving' in traffic_type:
            region = item['start_region']
            origin = start_from_address
            destination = start_to_address
            mode = 'driving'
        elif 'dest_bus' in traffic_type:
            region = item['dest_region']
            origin = dest_from_address
            destination = dest_to_address
            mode = 'transit'
        elif 'dest_taxi' in traffic_type:
            region = item['dest_region']
            origin = dest_from_address
            destination = dest_to_address
            mode = 'driving'
        elif 'dest_driving' in traffic_type:
            region = item['dest_region']
            origin = dest_from_address
            destination = dest_to_address
            mode = 'driving'
        elif traffic_type == driving:
            origin_region = item['start_region']
            destination_region = item['dest_region']
            origin = dest_from_address
            destination = dest_to_address
            mode = 'driving'
        #生成url
        url = ('http://api.map.baidu.com/direction?origin=%s&destination=%s&mode=%s&region=%s&origin_region=%s&destination_region=%s&output=%s&src=%s&' % 
            (origin,destination,mode,region,origin_region,destination_region,'html','xiaomishu'))
        '''
        params={
            'origin': origin,
            'destination': destination,
            'mode': mode,
            'region': region,
            'origin_region': origin_region,
            'destination_region': destination_region,
            'output': 'html',
            'src': 'xiaomishu',
            }
        '''
        #返回response对象
        return redirect(url)

@app.route('/order/', methods=['GET', 'POST'])
@login_required
def order():
    if request.method == 'GET':
        user = session['user']
        user_record = User.query.filter_by(id=user['userid']).first()
        if not user_record.account:
            flash(u'请登录/注册小秘书账号', 'message')
            return redirect(url_for('.login', request_url=request.url))
        leave_timelineid = request.args.get('leave_timelineid')
        actid = request.args.get('actid')
        order_type = request.args.get('order_type')
        act = ActTour.query.filter_by(userid=user['userid'], id=actid).first()

        details = ['','','','','']
        if leave_timelineid:
            timelineid = leave_timelineid
            timeline_record = Timeline.query.filter_by(userid=user['userid'], id=timelineid).first()
            timeline_list = json.loads(timeline_record.timeline)
            check_in_date_str = timeline_list[-1]['check_in_datetime'][:7]
            train = {}
            flight = {}
            hotel = {}
            for item in timeline_list:
                if item['type'] == 'train':
                    train = item['detail']
                if item['type'] == 'plane':
                    flight = item['detail']
                if item['type'] == 'hotel':
                    hotel = item['detail']
            if train and order_type == 'leave_train':
                train_depart_datetime = get_train_depart_datetime(train).strftime('%Y-%m-%d %H:%M')
                train_arrive_datetime = get_train_arrive_datetime(train).strftime('%Y-%m-%d %H:%M')
                leave_train = {
                    "station_train_code": train['station_train_code'],
                    "from_station_name": train['from_station_name'],
                    "to_station_name": train['to_station_name'],
                    "depart_datetime": train_depart_datetime,
                    "arrive_datetime": train_arrive_datetime,
                    "tickets_info": train_tickets_info(train),
                }
                details[0] = leave_train
            if flight and order_type == 'leave_flight':
                leave_flight = {
                    "flightcomname": flight['flightcomname'],
                    "flightNum": flight['flightNum'],
                    "dep_arp": flight['dep_arp'],
                    "arr_arp": flight['arr_arp'],
                    "dep_time": flight['dep_time'],
                    "arr_time": flight['arr_time'],
                    "tickets_info": flight['ticketinfo'],
                }
                details[1] = leave_flight
            if hotel  and order_type == 'hotel':
                price = hotel['detail_info']['price']
                hotel_info = {
                    "name": hotel['name'],
                    "address": hotel['address'],
                    "telephone": hotel['telephone'],
                    "overall_rating": hotel['detail_info']['overall_rating'],
                    "check_in_date": check_in_date_str,
                    "check_out_date": act.end_datetime.strftime('%Y-%m-%d'),
                    "bed_types": ['drj','bj','dcf','swf'],
                    "prices": [price,price,price,price],
                }
                details[2] = hotel_info
        else:
            leave_timelineid = None

        return_timelineid = request.args.get('return_timelineid')
        if return_timelineid:
            timelineid = return_timelineid
            timeline_record = Timeline.query.filter_by(userid=user['userid'], id=timelineid).first()
            timeline_list = json.loads(timeline_record.timeline)
            train = {}
            flight = {}
            hotel = {}
            for item in timeline_list:
                if item['type'] == 'train':
                    train = item['detail']
                if item['type'] == 'plane':
                    flight = item['detail']
            if train and order_type == 'return_train':
                train_depart_datetime = get_train_depart_datetime(train).strftime('%Y-%m-%d %H:%M')
                train_arrive_datetime = get_train_arrive_datetime(train).strftime('%Y-%m-%d %H:%M')
                leave_train = {
                    "station_train_code": train['station_train_code'],
                    "from_station_name": train['from_station_name'],
                    "to_station_name": train['to_station_name'],
                    "depart_datetime": train_depart_datetime,
                    "arrive_datetime": train_arrive_datetime,
                    "tickets_info": train_tickets_info(train),
                }
                details[3] = leave_train
            if flight and order_type == 'return_flight':
                leave_flight = {
                    "flightcomname": flight['flightcomname'],
                    "flightNum": flight['flightNum'],
                    "dep_arp": flight['dep_arp'],
                    "arr_arp": flight['arr_arp'],
                    "dep_time": flight['dep_time'],
                    "arr_time": flight['arr_time'],
                    "tickets_info": flight['ticketinfo'],
                }
                details[4] = leave_flight
        else:
            return_timelineid = None

        flight_ticket_names = {
            
        }
        return render_template('order_confirm.html', user=user, orders=details,
            actid=actid, leave_timelineid=leave_timelineid, return_timelineid=return_timelineid)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


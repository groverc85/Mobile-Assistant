#-*- coding:utf-8 -*-
import json, requests
from datetime import datetime, time, timedelta


# qos of tran departing or arriving time 
def get_time_qos(time):
    time_list = time.split(':')
    minutes = int(time_list[0])*24 + int(time_list[1])
    return abs(12*60 - minutes)


# format date from yearmonthday to year-month-day
def format_date_str(date_str):
    format_str = date_str[:4]+'-'+date_str[4:6]+'-'+date_str[6:]
    return format_str


################################################################################
# train
# 获得火车出发时间
def get_train_depart_datetime(train):
    train_depart_datetime = datetime.strptime(
        train['start_train_date']+
            train['start_time'],
        '%Y%m%d%H:%M')
    return train_depart_datetime


# 获得火车到达时间
def get_train_arrive_datetime(train):
    train_arrive_datetime = get_train_depart_datetime(train) + timedelta(minutes=int(train['lishiValue']))
    return train_arrive_datetime


# query train list by using train API
def get_trains(start_city, dest_city, date):
    #生成url
    url = 'http://api.rocliu.net/api/StationToStation'
    #自定义请求头，referer用来保证获取当前时间内容
    headers={'referer': 'http://api.rocliu.net/'}
    params={
        'from_station': start_city,
        'to_station': dest_city,
        'date': date,
        }
    #返回response对象
    train_resp = requests.get(url, headers=headers, params=params)
    train_json = train_resp.json()
    trains_ = train_json['data']
    trains = []
    for train_ in trains_:
        train = train_['queryLeftNewDTO']
        trains.append(train)
    return trains


def train_tickets_info(train):
    if train['station_train_code'][0] in ['G', 'D', 'C']:
        swz = {
            "name": u'商务座',
            "type": 'swz',
            "price": get_price(train, 'A9'),
            "amount": train['swz_num'],
        }
        tdz = {
            "name": u'特等座',
            "type": 'tdz',
            "price": get_price(train, 'P'),
            "amount": train['tz_num'],
        }
        ydz = {
            "name": u'一等座',
            "type": 'ydz',
            "price": get_price(train, 'M'),
            "amount": train['zy_num'],
        }
        edz = {
            "name": u'二等座',
            "type": 'edz',
            "price": get_price(train, 'O'),
            "amount": train['ze_num'],
        }
        tickets = [swz, tdz, ydz, edz]
    else:
        gjrw = {
            "name": u'高级软卧',
            "type": 'gjrw',
            "price": get_price(train, 'A6'),
            "amount": train['gr_num'],
        }
        rw = {
            "name": u'软卧',
            "type": 'rw',
            "price": get_price(train, 'A4'),
            "amount": train['rw_num'],
        }
        yw = {
            "name": u'硬卧',
            "type": 'yw',
            "price": get_price(train, 'A3'),
            "amount": train['yw_num'],
        }
        rz = {
            "name": u'软座',
            "type": 'rz',
            "price": get_price(train, 'A2'),
            "amount": train['rz_num'],
        }
        yz = {
            "name": u'硬座',
            "type": 'yz',
            "price": get_price(train, 'A1'),
            "amount": train['yz_num'],
        }
        wz = {
            "name": u'无座',
            "type": 'wz',
            "price": get_price(train, 'WZ'),
            "amount": train['wz_num'],
        }
        tickets = [gjrw, rw, yw, rz, yz, wz]
    return tickets

#是否有余票
def remain_tickets(train):
    # ￥元    角   席别
    # A9      9    商务座
    # P            特等座
    # M            一等座
    # O            二等座
    # A6      6    高级软卧
    # A4      4    软卧
    # A3      3    硬卧
    # A2      2    软座
    # A1      1    硬座
    # WZ           无座
    # MIN     5    包厢硬卧
    # OT           同上
    # 查G/D/C用'seat_types'='OMP9', 查普通车用'seat_types'='12346'
    tickets = []
    if train['station_train_code'][0] in ['G', 'D', 'C']:
        #二等座
        if train['ze_num'] !="--" and train['ze_num'] !=u"无" and train['ze_num'] !="*":
            tickets.append('O')
        #一等座
        if train['zy_num'] !="--" and train['zy_num'] !=u"无" and train['zy_num'] !="*":
            tickets.append('M')
        #特等座
        if train['tz_num'] !="--" and train['tz_num'] !=u"无" and train['tz_num'] !="*":
            tickets.append('P')
        #商务座
        if train['swz_num'] !="--" and train['swz_num'] !=u"无" and train['swz_num'] !="*":
            tickets.append('A9')
    else:
        #硬座
        if train['yz_num'] !="--" and train['yz_num'] !=u"无" and train['yz_num'] !="*":
            tickets.append('A1')
        #软座
        if train['rz_num'] !="--" and train['rz_num'] !=u"无" and train['rz_num'] !="*":
            tickets.append('A2')
        #硬卧
        if train['yw_num'] !="--" and train['yw_num'] !=u"无" and train['yw_num'] !="*":
            tickets.append('A3')
        #软卧
        if train['rw_num'] !="--" and train['rw_num'] !=u"无" and train['rw_num'] !="*":
            tickets.append('A4')
        #高级软卧
        if train['gr_num'] !="--" and train['gr_num'] !=u"无" and train['gr_num'] !="*":
            tickets.append('A6')
    return tickets


# will the train arrive intime for leaving trip
def is_train_intime(begin_datetime, duration, train, act_pref):
    # 应该到达时间
    train_arrive_deadline = begin_datetime - timedelta(minutes=act_pref.check_in_buffer+act_pref.wait_act_buffer+duration)
    train_arrive_datetime = get_train_arrive_datetime(train)
    return train_arrive_deadline>train_arrive_datetime


def is_train_valid(end_datetime, duration, train, act_pref):
    # train earliest depart datetime
    train_depart_earliest = end_datetime + timedelta(minutes=act_pref.check_out_buffer+duration)
    train_depart_datetime = get_train_arrive_datetime(train)
    return train_depart_datetime>train_depart_earliest


# query the price of the train for leaving trip
def get_price(train, seat):
    depart_date_str = format_date_str(train['start_train_date'])
    seat_types='OMP912346'
    #调用TrainPriceInfoAPI
    #生成url
    price_url = ('https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?train_no=%s&from_station_no=%s&to_station_no=%s&seat_types=%s&train_date=%s' %
                 (train['train_no'],train['from_station_no'],train['to_station_no'],seat_types,depart_date_str))
    # 自定义请求头，referer用来保证获取当前时间内容
    price_headers = {'referer': 'http://api.rocliu.net/'}
    #返回response对象
    price_resp = requests.get(price_url, headers=price_headers, verify=False)
    price_json = price_resp.json()
    price = price_json['data']
    if seat in price:
        return price[seat]
    else:
        return '$10000'
        app.logger.error('An error occurred for seat_types: %s', seat)


# calculate the cost of the train, return trains with cost
def calc_trains_cost(trains, train_pref, the_same_day, leave_return):
    one_day_before = the_same_day - timedelta(days=1)
    two_days_before = the_same_day - timedelta(days=2)
    one_day_after = the_same_day + timedelta(days=1)
    # pref[0] for price_qos, pref[1] for depart_time_qos, pref[2] for duration_qos
    pref = train_pref
    # for check if the price is calcuted... in cost()
    station_tuple_list = []
    price_list = []
    optimal_train = trains[0]
    station_tuple_list.append((
        optimal_train['from_station_name'],
        optimal_train['to_station_name'],
        optimal_train['station_train_code'][0]
    ))
    price_list.append(get_price(optimal_train, remain_tickets(optimal_train)[0]))
    for train in trains:
        duration_qos = int(train['lishiValue'])
        # 出发时间离12:00的长短
        depart_time_qos = get_time_qos(train['start_time'])
        # 座位席别
        seat = remain_tickets(train)
        # pref[0]==1 means considering price
        if pref[0] == 1:
            # check if the price for (station,station,train_type) is calcuted before
            # can be migrated into get_price()
            station_tuple = (
                optimal_train['from_station_name'],
                optimal_train['to_station_name'],
                optimal_train['station_train_code'][0]
            )
            for i in range(len(station_tuple_list)):
                # if price is calcuted before
                if station_tuple == station_tuple_list[i]:
                    price = price_list[i]
                # if price is not calcuted before, calcuted it and append it
                else: 
                    price = float(get_price(train, seat[0])[1:])
                    station_tuple_list.append(station_tuple)
                    price_list.append(price)
            # calcute price qos from train price and additional hotel price
            # if leave_return=='leave', means leaving trip
            if leave_return == 'leave':
                train_arrive_datetime = get_train_arrive_datetime(train)
                # arrive on the same day, no additional lodging
                if train_arrive_datetime > datetime.combine(the_same_day, time.min):
                    price_qos = price
                # arrive on one day before, one day lodging, average privce 150
                elif train_arrive_datetime > datetime.combine(one_day_before, time.min):
                    price_qos = price + 150
                # arrive on one day before, two days lodging, average privce 300
                else:
                    price_qos = price + 300
            # else leave_return=='return', means returning trip
            else:
                train_depart_datetime = get_train_depart_datetime(train)
                if train_depart_datetime > datetime.combine(one_day_after,time.min):
                    price_qos = price + 150
                else:
                    price_qos = price
        else:
            price_qos = 0
        train['cost'] = int(pref[0])*int(price_qos) + int(pref[1])*depart_time_qos/2 + int(pref[2])*duration_qos
    return trains


# query the train with optimal cost for leaving trip
def get_leave_train(act, act_pref):
    #火车到达时间要在活动开始时间begin_datetime之前，火车的出发时间可能是当天，前一天，前两天
    #the same day
    the_same_day = act['begin_datetime'].date()
    #the day before
    one_day_before = the_same_day - timedelta(days=1)
    #two days ago
    two_days_before = the_same_day - timedelta(days=2)

    the_same_day_trains = get_trains(act['start_city'], act['dest_city'], the_same_day)
    one_day_before_trains = get_trains(act['start_city'], act['dest_city'], one_day_before)
    # two_days_before_trains = get_trains(act['start_city'], act['dest_city'], two_days_before)
    trains = the_same_day_trains + one_day_before_trains
    # 从3天的3个optimal_train中选择最好的那个train
    # 判断火车能否及时到达
    in_time_trains = []
    '''
    Each city has only several stations. When get bus duration from station to
    destination, check if it has been done before. If it has, use the
    duration, otherwise, get it.
    '''
    # for checking if the duration is calcuted before
    station_list = []
    duration_list = []
    station_list.append(trains[0]['to_station_name'] + u'站')
    duration_list.append(get_duration(act_pref.leave_dest_traffic, act['dest_city'], station_list[0], act['dest_address'], act_pref))
    for train in trains:
        if train['station_train_code'][0] in act_pref.train_type:
            # check if the duration is calcuted before
            station = train['to_station_name'] + u'站'
            # if the duration is calcuted before
            if station in station_list:
                duration = duration_list[station_list.index(station)]
            # if the duration is not calcuted before, caltuted it and append it
            else:
                duration = get_duration(act_pref.leave_dest_traffic, act['dest_city'], station, act['dest_address'], act_pref)
                station_list.append(station)
                duration_list.append(duration)
            # if no tickets for train, remain_tickets(train) return []
            if is_train_intime(act['begin_datetime'], duration, train, act_pref) and remain_tickets(train):
                in_time_trains.append(train)
    if not in_time_trains:
        for train in trains:
            # check if the duration is calcuted before
            station = train['to_station_name'] + u'站'
            # if the duration is calcuted before
            if station in station_list:
                duration = duration_list[station_list.index(station)]
            # if the duration is not calcuted before, caltuted it and append it
            else:
                duration = get_duration(act_pref.leave_dest_traffic, act['dest_city'], station, act['dest_address'], act_pref)
                station_list.append(station)
                duration_list.append(duration)
            # if no tickets for train, remain_tickets(train) return []
            if is_train_intime(act['begin_datetime'], duration, train, act_pref) and remain_tickets(train):
                in_time_trains.append(train)
    # trains with cost
    trains_cost = calc_trains_cost(in_time_trains, act_pref.train_qos, the_same_day, 'leave')
    sorted_trains = sorted(trains_cost, key=lambda train: train['cost'])
    return sorted_trains


# query the train with optimal cost for leaving trip
def get_return_train(act, act_pref):
    #火车出发时间要在活动结束时间end_datetime之后，火车的出发时间可能是当天，后一天
    # the same day as the activity end date
    the_same_day = act['end_datetime'].date()
    # one day after  the activity end date
    one_day_after = the_same_day + timedelta(days=1)
    the_same_day_trains = get_trains(act['dest_city'], act['start_city'], the_same_day)
    one_day_after_trains = get_trains(act['dest_city'], act['start_city'], one_day_after)
    # two_days_before_trains = get_trains(act['start_city'], act['dest_city'], two_days_before)
    trains = the_same_day_trains + one_day_after_trains
    # trains that can be catch up after the activity end
    valid_trains = []
    # for checking if the duration is calcuted before
    station_list = []
    duration_list = []
    station_list.append(trains[0]['from_station_name'] + u'站')
    duration_list.append(get_duration(act_pref.return_dest_traffic, act['dest_city'], act['dest_address'], station_list[0], act_pref))
    for train in trains:
        if train['station_train_code'][0] in act_pref.train_type:
            # check if the duration is calcuted before
            station = train['from_station_name'] + u'站'
            # if the duration is calcuted before
            if station in station_list:
                duration = duration_list[station_list.index(station)]
            # if the duration is not calcuted before, caltuted it and append it
            else:
                duration = get_duration(act_pref.return_dest_traffic, act['dest_city'], act['dest_address'], station, act_pref)
                station_list.append(station)
                duration_list.append(duration)
            if is_train_valid(act['end_datetime'], duration, train, act_pref) and remain_tickets(train):
                valid_trains.append(train)
    if not valid_trains:
        for train in trains:
            # check if the duration is calcuted before
            station = train['to_station_name'] + u'站'
            # if the duration is calcuted before
            if station in station_list:
                duration = duration_list[station_list.index(station)]
            # if the duration is not calcuted before, caltuted it and append it
            else:
                duration = get_duration(act_pref.return_dest_traffic, act['dest_city'], act['dest_address'], station, act_pref)
                station_list.append(station)
                duration_list.append(duration)
            if is_train_valid(act['end_datetime'], duration, train, act_pref) and remain_tickets(train):
                valid_trains.append(train)
    # trains with cost
    trains_with_cost = calc_trains_cost(valid_trains, act_pref.train_qos, the_same_day, 'leave')
    sorted_trains = sorted(trains_with_cost, key=lambda train: train['cost'])
    return sorted_trains


################################################################################
# flight API
# get flight list by using flight_query API developed by zhao
def get_flights(depart_city, arrive_city, act_pref, depart_date):
    # type    仓位
    # T       优选套餐3.5折
    # Y       经济舱全价
    # Z       头等舱6.7折
    # F       头等舱全价
    # A6      6    高级软卧
    # A4      4    软卧
    # A3      3    硬卧
    # A2      2    软座
    # A1      1    硬座
    # WZ           无座
    # MIN     5    包厢硬卧
    # OT           同上
    #生成URL
    flight_url = 'http://api.ok-api.cn:11380/Zhaolang/flightzl/2/flightzl'
    #传递的参数
    flight_params = {
        'dc': depart_city,    
        'ac': arrive_city,
        't': depart_date,
    }
    #返回response对象
    flight_resp = requests.get(flight_url, params=flight_params)
    flight_json = flight_resp.json()
    return flight_json['flights']


# calculate cost of flights according to act_pref.flight_qos, return flight with cost
def flight_cost(flight, flight_pref, the_same_day, leave_return):
    # pref[] is like [price, dep_time, ontimerate]
    pref = flight_pref
    one_day_before = the_same_day - timedelta(days=1)
    one_day_after = the_same_day + timedelta(days=1)
    flight_arrive_datetime = datetime.strptime(flight['arr_time'],'%Y-%m-%d %H:%M:%S')
    flight_depart_datetime = datetime.strptime(flight['dep_time'],'%Y-%m-%d %H:%M:%S')
    if leave_return == 'leave':
        if flight_arrive_datetime < datetime.combine(the_same_day, time.min):
            price_qos = float(flight['lowprice']) + 150
        else:
            price_qos = float(flight['lowprice'])
    else:
        if flight_depart_datetime > datetime.combine(one_day_after, time.min):
            price_qos = float(flight['lowprice']) + 150
        else:
            price_qos = float(flight['lowprice'])
    depart_time_qos = abs((flight_depart_datetime.hour)*60 +
                flight_depart_datetime.minute - 720)*2
    ontimerate_qos = float(flight['ontimerate'])
    cost = int(pref[0])*price_qos + int(pref[1])*depart_time_qos + int(pref[2])*ontimerate_qos
    return cost


def is_flight_intime(begin_datetime, duration, flight, act_pref):
    # print(begin_datetime, duration)
    flight_arrive_deadline = begin_datetime - timedelta(minutes=act_pref.check_in_buffer+act_pref.wait_act_buffer+duration)
    # print(flight_arrive_deadline, datetime.strptime(flight['arr_time'],'%Y-%m-%d %H:%M:%S'))
    return flight_arrive_deadline > datetime.strptime(flight['arr_time'],'%Y-%m-%d %H:%M:%S')


def is_flight_valid(end_datetime, duration, flight, act_pref):
    # flight earliest depart datetime
    flight_depart_earliest = end_datetime + timedelta(minutes=act_pref.check_out_buffer+duration)
    flight_depart_datetime = datetime.strptime(flight['dep_time'],'%Y-%m-%d %H:%M:%S')
    return flight_depart_datetime>flight_depart_earliest


# query the fight with optimal qos for leaving trip
def get_leave_flight(act, act_pref):
    # 飞机出发日期可能是当天，前一天
    # the same day as the activity begin
    the_same_day = act['begin_datetime'].date()
    # the day before the activity begin
    one_day_before = the_same_day - timedelta(days=1)
    the_same_day_flights = get_flights(act['start_city'], act['dest_city'], act_pref, the_same_day)
    one_day_before_flights = get_flights(act['start_city'], act['dest_city'], act_pref, one_day_before)
    flights = the_same_day_flights + one_day_before_flights
    # flights that can be catch up after the activity end
    intime_flights = []
    # for checking if the duration is calcuted before
    airport_list = []
    duration_list = []
    airport_list.append(flights[0]['arr_arp'] + u'机场')
    duration_list.append(get_duration(act_pref.leave_dest_traffic, act['dest_city'], airport_list[0], act['dest_address'], act_pref))
    for flight in flights:
        if flight['flightNum'][:1] in act_pref.flight_company:
            # check if the duration is calcuted before
            airport = flight['arr_arp'] + u'机场'
            # if the duration is calcuted before
            if airport in airport_list:
                duration = duration_list[airport_list.index(airport)]
            # if the duration is not calcuted before, caltuted it and append it
            else:
                duration = get_duration(act_pref.leave_dest_traffic, act['dest_city'], airport, act['dest_address'], act_pref)
                airport_list.append(airport)
                duration_list.append(duration)
            if is_flight_intime(act['begin_datetime'], duration, flight, act_pref):
                intime_flights.append(flight)
    if not intime_flights:
        for flight in flights:
            # check if the duration is calcuted before
            airport = flight['arr_arp'] + u'机场'
            # if the duration is calcuted before
            if airport in airport_list:
                duration = duration_list[airport_list.index(airport)]
            # if the duration is not calcuted before, caltuted it and append it
            else:
                duration = get_duration(act_pref.leave_dest_traffic, act['dest_city'], airport, act['dest_address'], act_pref)
                airport_list.append(airport)
                duration_list.append(duration)
            if is_flight_intime(act['begin_datetime'], duration, flight, act_pref):
                intime_flights.append(flight)
    sorted_flights = sorted(intime_flights, key=lambda flight: flight_cost(flight, act_pref.flight_qos, the_same_day, 'leave'))
    return sorted_flights


def get_return_flight(act, act_pref):
    # 飞机出发日期可能是当天，后一天
    # the same day as the activity end
    the_same_day = act['end_datetime'].date()
    # the day after the activity end
    one_day_after = the_same_day - timedelta(days=1)
    the_same_day_flights = get_flights(act['dest_city'], act['start_city'], act_pref, the_same_day)
    one_day_after_flights = get_flights(act['dest_city'], act['start_city'], act_pref, one_day_after)
    flights = the_same_day_flights + one_day_after_flights
    valid_flights = []
    # for checking if the duration is calcuted before
    airport_list = []
    duration_list = []
    airport_list.append(flights[0]['dep_arp'] + u'机场')
    duration_list.append(get_duration(act_pref.return_dest_traffic, act['dest_city'], act['dest_address'], airport_list[0], act_pref))
    for flight in flights:
        if flight['flightNum'][:1] in act_pref.flight_company:
            # check if the duration is calcuted before
            airport = flight['dep_arp'] + u'机场'
            # if the duration is calcuted before
            if airport in airport_list:
                duration = duration_list[airport_list.index(airport)]
            # if the duration is not calcuted before, caltuted it and append it
            else:
                duration = get_duration(act_pref.return_dest_traffic, act['dest_city'], act['dest_address'], airport, act_pref)
                airport_list.append(airport)
                duration_list.append(duration)
            if is_flight_valid(act['begin_datetime'], duration, flight, act_pref):
                valid_flights.append(flight)
    if not valid_flights:
        for flight in flights:
            # check if the duration is calcuted before
            airport = flight['dep_arp'] + u'机场'
            # if the duration is calcuted before
            if airport in airport_list:
                duration = duration_list[airport_list.index(airport)]
            # if the duration is not calcuted before, caltuted it and append it
            else:
                duration = get_duration(act_pref.return_dest_traffic, act['dest_address'], act['dest_city'], airport, act_pref)
                airport_list.append(airport)
                duration_list.append(duration)
            if is_flight_valid(act['begin_datetime'], duration, flight, act_pref):
                valid_flights.append(flight)
    sorted_flights =  sorted(valid_flights, key=lambda flight: flight_cost(flight, act_pref.flight_qos, the_same_day, 'return'))
    return sorted_flights


################################################################################
# address_to_coordinates API by fu
def addr_to_coor(location):
    #生成url address
    addr_to_coor_url = 'http://api.rocliu.net/api/address_to_coordinates'
    #自定义请求头，referer用来保证获取当前时间内容
    addr_to_coor_headers = {'referer': 'http://api.rocliu.net/'}
    addr_to_coor_params = {
        'city': location['city'],
        'address': location['address']
    }
    #返回response对象
    addr_to_coor_resp = requests.get(addr_to_coor_url, headers=addr_to_coor_headers, params=addr_to_coor_params)
    addr_to_coor_json = addr_to_coor_resp.json()
    #{'lat':,'lng':,} 获得经纬度
    coordinate_json = addr_to_coor_json['result']['location']
    coordinate = '%s,%s' % (coordinate_json['lat'], coordinate_json['lng'])
    return coordinate


# coordinate_to_address API by fu
def coor_to_addr(lat_lng, ctype):
    #生成url address
    coor_to_addr_url = 'http://api.rocliu.net/api/coordinates_to_address'
    #自定义请求头，referer用来保证获取当前时间内容
    coor_to_addr_headers = {'referer': 'http://api.rocliu.net/'}
    coor_to_addr_params = {
        'coordtype': ctype,
        'location': lat_lng,
    }
    #返回response对象
    coor_to_addr_resp = requests.get(coor_to_addr_url, headers=coor_to_addr_headers, params=coor_to_addr_params)
    coor_to_addr_json = coor_to_addr_resp.json()
    #或者sematic_description
    address = coor_to_addr_json['result']
    return address


# 通过地理位置转坐标，坐标转地理位置来获得城市
def get_city(address):
    '''
    # address to coordinate
    location = {
        'city':'',
        'address':address,
    }
    coordinate = addr_to_coor(location)
    # coordinate to address
    resp = coor_to_addr(coordinate, 'bd09ll')
    city = resp['addressComponent']['city']
    city_name = city[:-1]
    return city_name
    '''
    addr_list = address.split(' ')
    for addr in addr_list:
        if addr[-1:] == u'市':
            return addr[:-1]


# 测试输入地址的有效性
def test_addr(city, addr):
    #生成url
    addr_to_coor_url = 'http://api.rocliu.net/api/address_to_coordinates'
    #自定义请求头，referer用来保证获取当前时间内容
    addr_to_coor_headers = {'referer': 'http://api.rocliu.net/'}
    addr_to_coor_params = {
    'city': city,
    'address': addr
    }
    #返回response对象
    addr_to_coor_resp = requests.get(addr_to_coor_url, headers=addr_to_coor_headers, params=addr_to_coor_params)
    addr_to_coor_json = addr_to_coor_resp.json()
    if addr_to_coor_json['status'] != 0:
        return False


################################################################################
# city traffic
# routing_by_bus API
def get_bus(region, bus_from, bus_to):
    #生成URL
    bus_url = 'http://api.rocliu.net/api/routing_by_bus'
    #传递的参数
    coord_to = bus_to
    coord_from = bus_from
    bus_params = {
        'coord_to': coord_to,
        'region': region,
        'tactics': 11,
        'coord_from': coord_from,
    }
    #返回response对象
    bus_resp = requests.get(bus_url, params=bus_params)
    bus_json = bus_resp.json()
    buses = bus_json['result']['routes']
    #分阶段路线 不行-公交-步行
    optimal_bus = buses[0]['scheme'][0]
    return optimal_bus


# get taxi through "routing by bus" API 
def get_taxi(region, bus_from, bus_to):
    #生成URL
    bus_url = 'http://api.rocliu.net/api/routing_by_bus'
    #传递的参数
    coord_to = bus_to
    coord_from = bus_from
    bus_params = {
        'coord_to': coord_to,
        'region': region,
        'tactics': 11,
        'coord_from': coord_from,
    }
    #返回response对象
    bus_resp = requests.get(bus_url, params=bus_params)
    bus_json = bus_resp.json()
    taxi = bus_json['result']['taxi']
    return taxi


# routing_by_walking API
def get_walking(region, walk_from, walk_to):
    #生成URL
    walking_url = 'http://api.rocliu.net/api/routing_by_walking'
    #传递的参数
    coord_to = walk_to
    coord_from = walk_from
    walking_params = {
        'coord_to': coord_to,
        'region': region,
        'tactics': 11,
        'coord_from': coord_from,
    }
    #返回response对象
    walking_resp = requests.get(walking_url, params=walking_params)
    walking_json = walking_resp.json()
    return walking_json


################################################################################
# routing_by_driving API
def get_driving(region_from, region_to, drive_from, drive_to):
    #生成URL
    urldriving = 'http://api.rocliu.net/api/routing_by_driving'
    #传递的参数
    coord_to = drive_to
    coord_from = drive_from
    paramsdriving = {
        'region_from': region_from,
        'coord_from': coord_from,
        'region_to': region_to,
        'coord_to': coord_to,
        'tactics': 11
    }
    #返回response对象
    rdriving = requests.get(urldriving, params=paramsdriving)
    driving_json = rdriving.json()
    return driving_json['result']['taxi']


# get city traffic duration according to city traffic pref
def get_duration(city_traffic, city, from_, to_, act_pref):
    from_location = {'city': city, 'address': from_}
    to_location = {'city': city, 'address': to_}
    from_latlng = addr_to_coor(from_location)
    to_latlng = addr_to_coor(to_location)
    if city_traffic == 'bus':
        optimal_traffic = get_bus(city, from_latlng, to_latlng)
        return int(optimal_traffic['duration'])/60 + act_pref.wait_bus_buffer
    elif city_traffic == 'taxi':
        optimal_traffic = get_taxi(city, from_latlng, to_latlng)
        return int(optimal_traffic['duration'])/60 + act_pref.wait_taxi_buffer
    elif city_traffic == 'driving':
        optimal_traffic = get_driving(city, city, from_latlng, to_latlng)
        return int(optimal_traffic['duration'])/60


################################################################################
# restaurant
# get restaurant use catering API by fu
def get_restaurant(coordinate, restaurant_radius, restaurant_pref):
    #生成URL,resta is short for restaurant
    restaurant_url = 'http://api.rocliu.net/api/caters_nearby_within_a_circle'
    #传递的参数
    restaurant_params = {
        'radius': restaurant_radius,
        'sortby': 'default',
        'location': coordinate,
        'query': restaurant_pref,
    }
    #返回response对象
    restaurant_resp = requests.get(restaurant_url, params=restaurant_params)
    restaurant_json = restaurant_resp.json()
    restaurants = restaurant_json['results']
    # optimal_restaurant = restaurants[0]
    return restaurants


#获取进行餐饮的时间
def get_meal_datetime(date_time):
    breakfast_datetime = date_time.replace(hour=7,minute=0,second=0)
    lunch_datetime = date_time.replace(hour=12,minute=0,second=0)
    supper_datetime = date_time.replace(hour=17,minute=0,second=0)
    tomorrow_breakfast_datetime = breakfast_datetime + timedelta(days=1)
    if breakfast_datetime > date_time:
        return breakfast_datetime
    if lunch_datetime > date_time:
        return lunch_datetime
    if supper_datetime > date_time:
        return supper_datetime
    return tomorrow_breakfast_datetime


################################################################################
#hotel API
def get_hotel(coordinate, hotel_radius, hotel_pref):
    #生成URL
    hotel_url = 'http://api.rocliu.net/api/hotels_nearby_within_a_circle'
    #传递的参数
    hotel_params = {
        'radius': hotel_radius,
        'sortby': 'default',
        'location': coordinate,
        'query': hotel_pref,
    }
    #返回response对象
    hotel_resp = requests.get(hotel_url, params=hotel_params)
    hotel_json = hotel_resp.json()
    hotels = hotel_json['results']
    # optimal_hotel = hotels[0]
    return hotels


################################################################################
# timeline
#generate timeline for leaving trip
def get_leave_timeline(act, act_pref):
    # 出发地start_from,start_to,和目的地dest_from,dest_to
    start_from_json = {'city': act['start_city'], 'address': act['start_address']}
    dest_to_json = {'city': act['dest_city'], 'address': act['dest_address']}
    start_from = addr_to_coor(start_from_json)
    dest_to = addr_to_coor(dest_to_json)
    start_region = act['start_city']
    dest_region = act['dest_city']
    timeline = []
    # main traffic is driving
    if act_pref.leave_main_traffic == 'driving':
        # leaving trip
        optimal_driving = get_driving(start_region, dest_region, start_from, dest_to)
        arrive_datetime = act['begin_datetime'] - timedelta(minutes=act_pref.check_in_buffer+act_pref.wait_act_buffer+30)
        depart_datetime = arrive_datetime - timedelta(seconds=int(optimal_driving['duration']))
        check_in_datetime = arrive_datetime
        timeline.append({'type': 'driving', 'time':depart_datetime.strftime('%Y-%m-%d %H:%M'), 'title':u'自驾', 'detail':optimal_driving})
    # main traffic is train or plane
    else:
        # main traffic is train
        if act_pref.leave_main_traffic == 'train':
            # train
            main_traffics = get_leave_train(act, act_pref)
            optimal_train = main_traffics[0]
            start_to_json = {
                'city': act['start_city'],
                'address': optimal_train['from_station_name'] +u'站',
            }
            dest_from_json = {
                'city': act['dest_city'],
                'address': optimal_train['to_station_name'] +u'站',
            }
            depart_datetime = get_train_depart_datetime(optimal_train)
            arrive_datetime = get_train_arrive_datetime(optimal_train)
            wait_datetime = depart_datetime - timedelta(minutes=act_pref.wait_train_buffer)
            timeline.append({
                'type':'train',
                'time':depart_datetime.strftime('%Y-%m-%d %H:%M'),
                'title':u'乘坐火车',
                'detail':optimal_train,
                'trainid':0,
            })
        # main traffic is plane
        elif act_pref.leave_main_traffic == 'plane':
            # plane
            main_traffics = get_leave_flight(act, act_pref)
            optimal_flight = main_traffics[0]
            start_to_json = {'city': act['start_city'],'address': optimal_flight['dep_arp'] +u'机场'}
            dest_from_json = {'city': act['dest_city'],'address': optimal_flight['arr_arp'] +u'机场'}
            depart_datetime = datetime.strptime(optimal_flight['dep_time'],'%Y-%m-%d %H:%M:%S')
            arrive_datetime = datetime.strptime(optimal_flight['arr_time'],'%Y-%m-%d %H:%M:%S')
            wait_datetime = depart_datetime - timedelta(minutes=act_pref.wait_flight_buffer)
            timeline.append({'type': 'plane', 'time':depart_datetime.strftime('%Y-%m-%d %H:%M'), 'title':u'乘坐飞机', 'detail':optimal_flight, 'flightid':0,})
            # timeline.append({'type':'plane', 'flightid':0})

        start_to = addr_to_coor(start_to_json)
        dest_from = addr_to_coor(dest_from_json)

        # city traffic in start
        if act_pref.leave_start_traffic == 'bus':
            #bus
            start_optimal_bus = get_bus(start_region, start_from, start_to)
            start_bus_depart_datetime = wait_datetime - timedelta(minutes=int(start_optimal_bus['duration'])/60)
            timeline.insert(0, {
                'type': 'start_bus',
                'time': start_bus_depart_datetime.strftime('%Y-%m-%d %H:%M'),
                'title': u'乘坐公交',
                'detail': start_optimal_bus,
            })
        elif act_pref.leave_start_traffic == 'taxi':
            #taxi
            start_optimal_taxi = get_taxi(start_region, start_from, start_to)
            start_taxi_depart_datetime = wait_datetime - timedelta(minutes=int(start_optimal_taxi['duration'])/60)
            timeline.insert(0,{
                'type': 'start_taxi',
                'time': start_taxi_depart_datetime.strftime('%Y-%m-%d %H:%M'),
                'title': u'乘坐的士',
                'detail': start_optimal_taxi,
            })
        elif act_pref.leave_start_traffic == 'driving':
            # driving
            start_optimal_taxi = get_taxi(start_region, start_from, start_to)
            start_taxi_depart_datetime = wait_datetime - timedelta(minutes=int(start_optimal_taxi['duration'])/60)
            timeline.insert(0,{
                'type': 'start_driving',
                'time': start_taxi_depart_datetime.strftime('%Y-%m-%d %H:%M'),
                'title': u'自驾',
                'detail': start_optimal_taxi
            })
        # city traffic in destination
        if act_pref.leave_dest_traffic == 'bus':
            # bus
            dest_optimal_bus = get_bus(dest_region, dest_from, dest_to)
            dest_bus_depart_datetime = arrive_datetime + timedelta(minutes=act_pref.wait_bus_buffer)
            check_in_datetime = dest_bus_depart_datetime + timedelta(seconds=int(dest_optimal_bus['duration']))
            timeline.append({
                'type': 'dest_bus',
                'time': dest_bus_depart_datetime.strftime('%Y-%m-%d %H:%M'),
                'title': u'乘坐公交',
                'detail' :dest_optimal_bus
            })
        elif act_pref.leave_dest_traffic == 'taxi':
            # taxi
            dest_optimal_taxi = get_taxi(dest_region, dest_from, dest_to)
            dest_taxi_depart_datetime = arrive_datetime + timedelta(minutes=act_pref.wait_taxi_buffer)
            check_in_datetime = dest_taxi_depart_datetime + timedelta(seconds=int(dest_optimal_taxi['duration']))
            timeline.append({
                'type': 'dest_taxi',
                'time': dest_taxi_depart_datetime.strftime('%Y-%m-%d %H:%M'),
                'title': u'乘坐的士',
                'detail': dest_optimal_taxi,
            })
        elif act_pref.leave_dest_traffic == 'driving':
            # driving
            dest_optimal_taxi = get_taxi(dest_region, dest_from, dest_to)
            dest_taxi_depart_datetime = arrive_datetime + timedelta(minutes=act_pref.wait_taxi_buffer)
            check_in_datetime = dest_taxi_depart_datetime + timedelta(seconds=int(dest_optimal_taxi['duration']))
            timeline.append({
                'type': 'dest_driving',
                'time': dest_taxi_depart_datetime.strftime('%Y-%m-%d %H:%M'),
                'title': u'自驾',
                'detail': dest_optimal_taxi,
            })
    #hotel
    hotels = get_hotel(dest_to,act_pref.hotel_radius,act_pref.hotel)
    optimal_hotel = hotels[0]
    check_in_datetime_str = check_in_datetime.strftime('%Y-%m-%d %H:%M')
    timeline.append({
        'type': 'hotel',
        'time': check_in_datetime_str,
        'title': u'入住酒店',
        'detail': optimal_hotel,
        'hotelid': 0,
    })
    # timeline.append({'type': 'hotel', 'hotelid': 0})
    # restaurant
    checked_in_datetime = check_in_datetime - timedelta(minutes=act_pref.check_in_buffer)
    meal_datetime = get_meal_datetime(checked_in_datetime)
    restaurants = get_restaurant(dest_to, act_pref.restaurant_radius, act_pref.restaurant)
    optimal_restaurant = restaurants[0]
    timeline.append({'type':'restaurant', 'time':meal_datetime.strftime('%Y-%m-%d %H:%M'), 'title':u'餐饮', 'detail':optimal_restaurant, 'restaurantid': 0,})
    # timeline.append({'type': 'restaurant', 'restaurantid': 0})
    timeline.append({'type':'activity', 'time':act['begin_datetime'].strftime('%Y-%m-%d %H:%M'), 'title':u'活动开始', 'detail':None})

    timeline.append({'type': 'direction', 'start_region': start_region, 
        'dest_region': dest_region, 'start_from': start_from,
        'start_to': start_to, 'dest_from': dest_from, 'dest_to': dest_to,
        'start_from_address': act['start_address'], 'dest_to_address': act['dest_address'],
        'start_to_address': start_to_json['address'], 'dest_from_address': dest_from_json['address'],
        'check_in_datetime': check_in_datetime_str})

    result = [timeline, main_traffics, hotels, restaurants]
    return result


################################################################################
#generate timeline for returning trip
def get_return_timeline(act, act_pref):
    # attention: the start and destinaton are inverted
    # 出发地start_from,start_to,和目的地dest_from,dest_to
    start_from_json = {'city': act['dest_city'], 'address': act['dest_address']}
    dest_to_json = {'city': act['start_city'], 'address': act['start_address']}
    start_from = addr_to_coor(start_from_json)
    dest_to = addr_to_coor(dest_to_json)
    start_region = act['dest_city']
    dest_region = act['start_city']
    timeline = []
    timeline.append({'type':'activity', 'time':act['end_datetime'].strftime('%Y-%m-%d %H:%M'), 'title':u'活动结束', 'detail':None})
    # main traffic is driving
    if act_pref.return_main_traffic == 'driving':
        # driving
        optimal_driving = get_driving(start_region, dest_region, start_from, dest_to)
        depart_datetime = act['end_datetime'] + timedelta(minutes=act_pref.check_out_buffer+30)
        arrive_datetime = depart_datetime + timedelta(seconds=int(driving['duration']))
        timeline.append({'type': 'driving', 'time':depart_datetime.strftime('%Y-%m-%d %H:%M'), 'title':u'自驾', 'detail':optimal_driving})
    # main traffic is train or plane
    else:
        # main traffic is train
        if act_pref.return_main_traffic == 'train':
            # train
            main_traffics = get_return_train(act, act_pref)
            optimal_train = main_traffics[0]
            start_to_json = {
                'city': act['dest_city'],
                'address': optimal_train['from_station_name'] +u'站',
            }
            dest_from_json = {
                'city': act['start_city'],
                'address': optimal_train['to_station_name'] +u'站',
            }
            depart_datetime = get_train_depart_datetime(optimal_train)
            arrive_datetime = get_train_arrive_datetime(optimal_train)
            wait_datetime = depart_datetime - timedelta(minutes=act_pref.wait_train_buffer)
            timeline.append({'type':'train', 'time':depart_datetime.strftime('%Y-%m-%d %H:%M'), 'title':u'乘坐火车', 'detail':optimal_train, 'trainid': 0,})
            # timeline.append({'type':'train', 'trainid': 0})
        # main traffic is plane
        elif act_pref.return_main_traffic == 'plane':
            # plane
            main_traffics = get_return_flight(act, act_pref)
            optimal_flight = main_traffics[0]
            start_to_json = {'city': act['dest_city'],'address': optimal_flight['dep_arp'] +u'机场'}
            dest_from_json = {'city': act['start_city'],'address': optimal_flight['arr_arp'] +u'机场'}
            depart_datetime = datetime.strptime(optimal_flight['dep_time'],'%Y-%m-%d %H:%M:%S')
            arrive_datetime = datetime.strptime(optimal_flight['arr_time'],'%Y-%m-%d %H:%M:%S')
            wait_datetime = depart_datetime - timedelta(minutes=act_pref.wait_flight_buffer)
            timeline.append({'type': 'plane', 'time':depart_datetime.strftime('%Y-%m-%d %H:%M'), 'title':u'乘坐飞机', 'detail':optimal_flight, 'flightid': 0,})
            # timeline.append({'type':'plane', 'flightid': 0})

        start_to = addr_to_coor(start_to_json)
        dest_from = addr_to_coor(dest_from_json)

        # city traffic in start
        if act_pref.return_start_traffic == 'bus':
            #bus
            start_optimal_bus = get_bus(start_region, start_from, start_to)
            start_bus_depart_datetime = wait_datetime - timedelta(minutes=int(start_optimal_bus['duration'])/60)
            timeline.insert(1, {
                'type': 'start_bus',
                'time': start_bus_depart_datetime.strftime('%Y-%m-%d %H:%M'),
                'title': u'乘坐公交',
                'detail': start_optimal_bus,
            })
        elif act_pref.return_start_traffic == 'taxi':
            #taxi
            start_optimal_taxi = get_taxi(start_region, start_from, start_to)
            start_taxi_depart_datetime = wait_datetime - timedelta(minutes=int(start_optimal_taxi['duration'])/60)
            timeline.insert(1,{
                'type': 'start_taxi',
                'time': start_taxi_depart_datetime.strftime('%Y-%m-%d %H:%M'),
                'title': u'乘坐的士',
                'detail': start_optimal_taxi,
            })
        elif act_pref.return_start_traffic == 'driving':
            # driving
            start_optimal_taxi = get_taxi(start_region, start_from, start_to)
            start_taxi_depart_datetime = wait_datetime - timedelta(minutes=int(start_optimal_taxi['duration'])/60)
            timeline.insert(1,{
                'type': 'start_driving',
                'time': start_taxi_depart_datetime.strftime('%Y-%m-%d %H:%M'),
                'title': u'自驾',
                'detail': start_optimal_taxi
            })        
        # city traffic in destination
        if act_pref.return_dest_traffic == 'bus':
            # bus
            dest_optimal_bus = get_bus(dest_region, dest_from, dest_to)
            dest_bus_depart_datetime = arrive_datetime + timedelta(minutes=act_pref.wait_bus_buffer)
            check_in_datetime = dest_bus_depart_datetime + timedelta(seconds=int(dest_optimal_bus['duration']))
            timeline.append({
                'type': 'dest_bus',
                'time': dest_bus_depart_datetime.strftime('%Y-%m-%d %H:%M'),
                'title': u'乘坐公交',
                'detail' :dest_optimal_bus
            })
        elif act_pref.return_dest_traffic == 'taxi':
            # taxi
            dest_optimal_taxi = get_taxi(dest_region, dest_from, dest_to)
            dest_taxi_depart_datetime = arrive_datetime + timedelta(minutes=act_pref.wait_taxi_buffer)
            check_in_datetime = dest_taxi_depart_datetime + timedelta(seconds=int(dest_optimal_taxi['duration']))
            timeline.append({
                'type': 'dest_taxi',
                'time': dest_taxi_depart_datetime.strftime('%Y-%m-%d %H:%M'),
                'title': u'乘坐的士',
                'detail': dest_optimal_taxi,
            })
        elif act_pref.return_dest_traffic == 'driving':
            # driving
            dest_optimal_taxi = get_taxi(dest_region, dest_from, dest_to)
            dest_taxi_depart_datetime = arrive_datetime + timedelta(minutes=act_pref.wait_taxi_buffer)
            check_in_datetime = dest_taxi_depart_datetime + timedelta(seconds=int(dest_optimal_taxi['duration']))
            timeline.append({
                'type': 'dest_driving',
                'time': dest_taxi_depart_datetime.strftime('%Y-%m-%d %H:%M'),
                'title': u'自驾',
                'detail': dest_optimal_taxi,
            })
        timeline.append({'type': 'direction', 'start_region': start_region, 
            'dest_region': dest_region, 'start_from': start_from,
            'start_to': start_to, 'dest_from': dest_from, 'dest_to': dest_to,
            'start_from_address': act['dest_address'], 'dest_to_address': act['start_address'],
            'start_to_address': start_to_json['address'], 'dest_from_address': dest_from_json['address'],
            'check_out_datetime': wait_datetime.strftime('%Y-%m-%d %H:%M')})
        result = [timeline, main_traffics]
    return result

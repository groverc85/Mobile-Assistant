#-*- coding:utf-8 -*-

from moblife import app
from moblife.apis import flight, train
from moblife.models_wechat import WechatUserInfo
from flask import render_template, url_for, redirect, request

@app.route('/basic/train')
def basic_train():
    openId = request.args.get('openId')
    user = WechatUserInfo.query_by_openid(openId)
    return render_template('train_query.html', user = user)

@app.route('/basic/plane')
def basic_plane():
    openId = request.args.get('openId')
    user = WechatUserInfo.query_by_openid(openId)
    return render_template('plane_query.html', user = user)
    
@app.route('/basic/plane/list', methods=['POST', 'GET'])
def plane_list():
    if request.method == 'POST':
        origin = request.form['origin']
        destination = request.form['destination']
        #time暂时无用
        time = request.form['time']
        #查出结果
    elif request.method == 'GET':
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        time = request.args.get('time')
    #resp = flight.GetRoutingByPlane(origin,destination,time)
    resp = flight.GetNewPlane(origin,destination,time)
    planes = []
    noResult = False
    openId = request.args.get('openId')
    user = WechatUserInfo.query_by_openid(openId)
    if resp['flights'] == None:
        noResult = True
        return render_template('plane_list.html', planes = planes, noResult = noResult, user = user)
    else:

        for info in resp['flights']:
            planes.append({'flightnum':info['flightNum'],
                           'flightcom':info['flightcomname'],
                          'start_time':info['dep_time'][11:],
                          'end_time':info['arr_time'][11:],
                          'start_airp':info['dep_arp'],
                          'end_airp':info['arr_arp'],
                          'tickets':info['ticketinfo'],}
                          )
        return render_template('plane_list.html', planes = planes, noResult = noResult, user = user)

        '''
        for info in resp['data']:
            begin_time = info['planDptTime'][11:]
            arr_time = info['planArrTime'][11:]
            planes.append({'flightnum':info['flightNO'],
                           'start_time':begin_time,
                           'end_time':arr_time,
                           'start_airp':info['dptAirport'],
                           'end_airp':info['arrAirport']
                          })
        return render_template('plane_list.html', planes = planes, noResult = noResult, user = user)    '''

@app.route('/basic/train/list', methods=['POST', 'GET'])
def train_list():
    if request.method == 'POST':
        origin = request.form['origin']
        destination = request.form['destination']
        #time暂时无用
        time = request.form['time']
        #查出结果
    elif request.method == 'GET':
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        time = request.args.get('time')
    #resp = train.GetRoutingByTrain(origin,destination)
    resp = train.GetNewTrain(origin, destination , time)
    trains = []
    noResult = False
    openId = request.args.get('openId')
    user = WechatUserInfo.query_by_openid(openId)
    if resp['data'] == None:
        noResult = True
        return render_template('train_list.html', trains = trains, noResult = noResult, user = user)
    else:
        for info in resp['data']:
            trains.append({'trainnum':info['trainNumber'],
                           'start_time':info['fromTime'],
                           'end_time':info['toTime'],
                           'start_sta':info['fromStation'],
                           'end_sta':info['toStation'],
                           'dur_time':info['durationTime'],
                           'tickets':info['seats'],
                          })

        return render_template('train_list.html', trains = trains, noResult = noResult, user = user)



        '''
        for info in resp['result']['data']:
            trains.append({'trainnum':info['trainOpp'],
                           'start_time':info['leave_time'],
                           'end_time':info['arrived_time'],
                           #start_staion中少了个t 坑死人不偿命
                           'start_sta':info['start_staion'],
                           'end_sta':info['end_station']
                          })
        return render_template('train_list.html', trains = trains, noResult = noResult, user = user)'''

@app.route('/basic/plane/detail', methods=['POST', 'GET'])
def plane_detail():
    if request.method == 'GET':
        flightNum = request.args.get('flightNum')
    resp = flight.GetFlightNum(flightNum)
    details = {}
    openId = request.args.get('openId')
    user = WechatUserInfo.query_by_openid(openId)
    if resp['status'] != '0':
        details['noInfo'] = True
    else:
        details['noInfo'] = False
        details['type'] = resp['data']['planeType']
        details['timeRate'] = resp['data']['onTimeRate']
        details['company'] = resp['data']['company']
        details['flightNum'] = resp['data']['flightNO']
        details['dptTerminal'] = resp['data']['cities'][0]['dptTerminal']
        details['dptTime'] = resp['data']['cities'][0]['planDptTime'][11:]
        details['dptCityName'] = resp['data']['cities'][0]['name']
        details['dptAirport'] = resp['data']['cities'][0]['airport']
        details['arrTerminal'] = resp['data']['cities'][1]['arrTerminal']
        details['arrTime'] = resp['data']['cities'][1]['planArrTime'][11:]
        details['arrCityName'] = resp['data']['cities'][1]['name']
        details['arrAirport'] = resp['data']['cities'][1]['airport']
        dptmin = ( ( ord(details['dptTime'][0]) - 48 ) * 10 + ord(details['dptTime'][1]) - 48 ) * 60 + (ord(details['dptTime'][3]) - 48) * 10 + ord(details['dptTime'][4]) - 48 
        arrmin = ( ( ord(details['arrTime'][0]) - 48 ) * 10 + ord(details['arrTime'][1]) - 48 ) * 60 + (ord(details['arrTime'][3]) - 48) * 10 + ord(details['arrTime'][4]) - 48
        durmin = arrmin - dptmin
        details['durhours'] = durmin // 60
        details['durmins'] = durmin % 60

    return render_template('plane_detail.html', details = details, user = user)

@app.route('/basic/train/detail', methods=['POST', 'GET'])
def train_detail():
    if request.method == 'GET':
        trainNum = request.args.get('trainNum')
    resp = train.GetTrainNum(trainNum)
    details = {}
    openId = request.args.get('openId')
    user = WechatUserInfo.query_by_openid(openId)
    if not resp['status'] == False:
        details['noInfo'] = True
    else:
        details['noInfo'] = False
        details['trainNum'] = resp['data']['data'][0]['station_train_code']
        details['dptStation'] = resp['data']['data'][0]['start_station_name']
        details['dptTime'] = resp['data']['data'][0]['start_time']
        details['arrStation'] = resp['data']['data'][0]['end_station_name']
        details['arrTime'] = resp['data']['data'][len(resp['data']['data']-1)]['arrive_time']




    return render_template('plane_detail.html', details = details, user = user)
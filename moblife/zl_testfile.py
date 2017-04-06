#-*- coding:utf-8 -*-
from moblife import app, wechat_api
from flask import render_template, url_for, redirect, request
from moblife.models_activity import ActTour, ActPref, Timeline, db
from sqlalchemy import asc
from moblife.models_wechat import WechatUserInfo, WechatUserLoc
import datetime,time
from moblife.apis import catering

import requests
import sys, json
#模拟微信数据
testuser = {'nickname':'Amasim'}


#act_list.html
@app.route('/test2')
def test223():
	acts = [{
              
           				 'id' : 123,
           				 'openId' : 456,
           				 'title' : u'北京出差',
          				 'note' : u'真的我也不知道如果备注真的很多很长会发生什么事不过事到如今也只好见机行事了希望不会对排版造成太大的影响',
          				 'startCity': u'杭州',
           				 'startAddr' : u'浙江大学西溪校区',
          				 'destCity' : u'北京',
          				 'destAddr' : u'北京大学',
          				 'startTime' : '2015-05-03 14:00:00',
           				 'endTime' : '2015-05-04 15:00:00',
           
        
	},
	{
              
           				 'id' : 123,
           				 'openId' : 456,
           				 'title' : u'北京出差',
          				 'note' : u'真的我也不知道如果备注真的很多很长会发生什么事不过事到如今也只好见机行事了希望不会对排版造成太大的影响',
          				 'startCity': u'杭州',
           				 'startAddr' : u'浙江大学西溪校区',
          				 'destCity' : u'北京',
          				 'destAddr' : u'北京大学',
          				 'startTime' : '2015-05-03',
           				 'endTime' : '2015-05-04',
           
        
	}]
	user = {
	                     'nickname':'Amasim',
	}
	return render_template('act_list.html', acts = acts, user = user)


@app.route('/test3')
def service1233323():
    if request.method == 'GET':
        actId = request.args.get('actId')
        openId = request.args.get('openId')
        user = WechatUserInfo.query_by_openid(openId)
        actTour =  ActTour.query.filter_by( id = actId, openId = user.openid).first()
        if actTour:
            act = {
            'title' : actTour.title,
            'note' : actTour.note, 
            'startCity':  actTour.startCity,
            'startAddr' : actTour.startAddr,
            'destCity' : actTour.destCity,
            'destAddr' : actTour.destAddr,
            'startTime' : actTour.startTime,
            'endTime' : actTour.endTime,
            #'timeline' : timeline
            }
        actPref =  ActPref.query.filter_by(openId = user.openid).first()

        #将datetime类型转换为字符串
        timeArray = act['startTime']
        actStartTime= timeArray.strftime('%Y-%m-%d %H:%M')
        #出发地和目的地
        startFrom = {'city' : act['startCity'],'address' :act['startAddr']}
        destTo = {'city' : act['destCity'],'address' :act['destAddr']}
        if actPref.interCity == 'train':
            if actPref.innerCity == 'bus':
            #####################################################################
                timeline = {}
                #train
                optimalTrain = train(act, actStartTime)
                startTo = {'city' : act['startCity'],'address' : optimalTrain['queryLeftNewDTO']['from_station_name'] +u'站'}
                destFrom = {'city' : act['destCity'],'address' : optimalTrain['queryLeftNewDTO']['to_station_name'] +u'站'}
                startTrainDT = formatDate(optimalTrain['queryLeftNewDTO']['start_train_date'])+' '+optimalTrain['queryLeftNewDTO']['start_time']
                destTrainDT = dTOperate(startTrainDT, '+', int(optimalTrain['queryLeftNewDTO']['lishiValue']))
                timeline['train'] = {'time':startTrainDT, 'title':u'乘坐火车', 'detail':optimalTrain}
                #bus
                startOptimalBus = bus(act['startCity'], startFrom, startTo)
                timeline['busStart'] = {'time':dTOperate(startTrainDT, '-', int(startOptimalBus['duration'])/60+60), 'title':u'乘坐公交', 'detail':startOptimalBus}
                destOptimalBus = bus(act['destCity'], destFrom, destTo)
                timeline['busDest'] = {'time':dTOperate(destTrainDT, '+', 30), 'title':u'乘坐公交', 'detail':destOptimalBus}
                #hotel
                optimalHotel = hotel(destTo)
                timeline['hotel'] = {'time':dTOperate(destTrainDT, '+', 30+int(destOptimalBus['duration'])/60), 'title':u'入住酒店', 'detail':optimalHotel}
                #restaurant
                afterHotelDT = dTOperate(destTrainDT, '+', 30+int(destOptimalBus['duration'])/60 + 20)
                restDT = dTRest(afterHotelDT)
                optimalRest = rest(destTo)
                timeline['rest'] = {'time':restDT, 'title':u'餐饮', 'detail':optimalRest}
                timeline['activity'] = {'time':actStartTime, 'title':u'活动开始', 'detail':None}
                #timelineRecord =  Timeline(actId, 'timeline1')
                #db.session.add(timelineRecord)
                timeline = trainBus(act, actPref)
                #timelineRecord =  Timeline(actId, 'timeline1')
                #db.session.add(timelineRecord)
                try:
                    #db.session.commit()
                    return render_template('justhavealook.html', act=act, train = timeline['train']['detail']['queryLeftNewDTO'], timeline =timeline)
                except Exception as e:
                    #db.session.rollback()
                    return str(e)


    
@app.route('/testcom')
def testcom():
    act = {
            'destCity':u'北京',
            'destAddr':u'清华大学',
            'note':u'一些没用的blabla',
            'startTime':'2015-05-13',
            'endTime':'2015-05-16',    
    }

    user = {

    }

    timeline = [
                 {
                   'type':'hotel',
                   'detail':{
                              'name':u'如家酒店',
                              'telephone':'010-46578942',
                              'address':u'五道口XXX号',
                              'detail_info':{
                                    'detail_url':'http://map.baidu.com/detail?qt=ninf&uid=1ec2dfa5ca3b46b0a8175a36&wd=%E5%A6%82%E5%AE%B6&b=(12907485.5,4807534.63;13005917.5,4862318.63)&&detail=hotel',
                              },
                   }
                 }
    ]
    return render_template('act_composition_test.html', act=act, user=user, timeline = timeline)





#测试路径##########################################
#base.html
@app.route('/test/base')              #working well
def test21314():
    return render_template('base.html',user = testuser)
###################################################
#火车
@app.route('/test/train/query')       #working well
def trainqtest():
    return render_template('train_query.html',user = testuser)

#@app.route('/test/train/list')       #noneed acess directly
#def trainltest():
#    return render_template('train_list.html',user = user)#trains = ?)

#@app.route('/test/train/detail')
#def traindtest():
#    return render_template('train_detail.html')
###################################################
#飞机
@app.route('/test/plane/query')       #working well
def planeqtest():
    return render_template('plane_query.html',user = testuser)

#@app.route('/test/plane/list')
#def planeltest():
#    return render_template('plane_list.html')

#@app.route('/test/plane/detail')
#def planedtest():
#    return render_template('plane_detail.html')
###################################################
#酒店
@app.route('/test/hotel/query')       #working well
def hotelqtest():
    return render_template('hotel_query.html',user = testuser)
###################################################
@app.route('/test/dinner/query')
def dinnerqtest():
    return render_template('dinner_query.html', user = testuser)
@app.route('/test/dinner/list')
def dinnerltest():
    if request.method == 'POST':
        location = request.form['location']
        keyWord = request.form['keyWord']
        price = request.form['price']
    elif request.method == 'GET':
        location = request.args.get['location']
        keyWord = request.args.get['keyWord']
        price = request.args.get['price']

    resp = catering.baiduGetCatering(location,price)
    dinners = []

    for info in resp['results']:
        d = {'name':info['name'],
             'address':info['address'],
             'tele':info['telephone'],
            }
        if info['detail_info']['price']:
            d['price'] = info['detail_info']['price']
        else:
            d['price'] = ''

        if info['detail_info']['detail_url']:
            d['url'] = info['detail_info']['detail_url']
        else:
            d['url'] = ''

        if info['detail_info']['overall_rating']:
            d['rating'] = info['detail_info']['overall_rating']
        else:
            d['rating'] = ''

        dinners.append(d)
    return render_template('dinner_list.html', dinners = dinners, user = testuser)
###################################################
#act系列
@app.route('/test/act/creat')         #working well
def actctest():
    return render_template('act_creat.html')

@app.route('/test/act/list')          #working well
def actltest():
    testacts = []
    for record in records:
        act = {
                  'id' : record['id'],
                  'openId' : record['openId'],
                  'title' : record['title'],
                  'note' : record['note'],
                  'startCity': record['startCity'],
                  'startAddr' : record['startAddr'],
                  'destCity' : record['destCity'],
                  'destAddr' : record['destAddr'],
                  'startTime' : record['startTime'][:16],
                  'endTime' : record['endTime'][:16],
                  #'timeline' : record.timeline
        }
        testacts.append(act)
    return render_template('act_list.html', user = testuser, acts = testacts)

@app.route('/test/act/pref')           #no working
def actptest():
    return render_template('act_pref.html')

@app.route('/test/act/composition')
def actcotest():
    return render_template('act_composition.html', user=testuser, act=testacts, timeline=json.loads(timeline_record.timeline))
    return render_template('act_composition.html')
####################################################
#order
@app.route('/test/order/confirm')
def orderctest():
    return render_template('order_confirm.html', user = testuser)

@app.route('/test/order/list')
def orderltest():
    return render_template('order_list.html', user = testuser)


















#####################test args###################
records = [
    {
        "id": 20,
        "openId": "o9KLls-iPWXrPb73rZV-X5Cqff8M",
        "title": u"北京出差",
        "note": u"None",
        "startCity": u"杭州",
        "startAddr": u"浙江大学玉泉校区",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-30 18:00:00",
        "endTime": "2015-04-30 14:00:00"
    },
    {
        "id": 28,
        "openId": "o9KLls_UjIPqrqGlVxYKitVXiqyk",
        "title": u"玩的开心",
        "note": u"你明明",
        "startCity": u"杭州",
        "startAddr": u"浙江大学玉泉校区",
        "destCity": u"西安",
        "destAddr": u"西安市政府 ",
        "startTime": "2015-04-28 14:00:00",
        "endTime": "2015-04-30 14:00:00"
    },
    {
        "id": 96,
        "openId": "o9KLls70ReakhjebmHUYxjbz9K8c",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江大学玉泉校区",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-29 01:34:00",
        "endTime": "2015-05-01 01:34:00"
    },
    {
        "id": 97,
        "openId": "o9KLls-iPWXrPb73rZV-X5Cqff8M",
        "title": u"呵呵出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学 ",
        "startTime": "2015-04-30 15:30:00",
        "endTime": "2015-05-01 01:34:00"
    },
    {
        "id": 98,
        "openId": "o9KLls-iPWXrPb73rZV-X5Cqff8M",
        "title": u"呵呵出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-30 15:30:00",
        "endTime": "2015-05-01 01:34:00"
    },
    {
        "id": 99,
        "openId": "o9KLls70ReakhjebmHUYxjbz9K8c",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江大学玉泉校区",
        "destCity": u"兰州",
        "destAddr": u"兰州大厦 ",
        "startTime": "2015-04-29 00:50:00",
        "endTime": "2015-05-01 01:44:00"
    },
    {
        "id": 100,
        "openId": "o9KLls-iPWXrPb73rZV-X5Cqff8M",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"北京大学",
        "startTime": "2015-04-29 19:45:00",
        "endTime": "2015-05-01 01:46:00"
    },
    {
        "id": 101,
        "openId": "o9KLls-iPWXrPb73rZV-X5Cqff8M",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"兰州",
        "destAddr": u"市政家园定西路小区 ",
        "startTime": "2015-04-30 01:55:00",
        "endTime": "2015-05-01 01:46:00"
    },
    {
        "id": 102,
        "openId": "oPX5rt_bFraV8rmOPzef4cPlyRDk",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江大学玉泉校区",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-29 10:00:00",
        "endTime": "2015-05-01 10:00:00"
    },
    {
        "id": 103,
        "openId": "oPX5rt8sUOXbr5prIqZAbuED70U0",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-29 10:08:00",
        "endTime": "2015-05-01 10:08:00"
    },
    {
        "id": 104,
        "openId": "oPX5rt_0kWFQm2H1ZGFnYb056xB0",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"西安",
        "destAddr": u"大雁塔北广场 ",
        "startTime": "2015-04-29 10:11:00",
        "endTime": "2015-05-01 10:11:00"
    },
    {
        "id": 105,
        "openId": "oPX5rt_0kWFQm2H1ZGFnYb056xB0",
        "title": u"出差",
        "note": u"阿啊啊",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"广州",
        "destAddr": u"科技园中英文学校 ",
        "startTime": "2015-04-29 10:11:00",
        "endTime": "2015-05-01 10:11:00"
    },
    {
        "id": 106,
        "openId": "oPX5rt_0kWFQm2H1ZGFnYb056xB0",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-29 10:13:00",
        "endTime": "2015-05-01 10:13:00"
    },
    {
        "id": 107,
        "openId": "oPX5rt_0kWFQm2H1ZGFnYb056xB0",
        "title": u"出差",
        "note": u"啊的",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-29 10:19:00",
        "endTime": "2015-05-01 10:19:00"
    },
    {
        "id": 108,
        "openId": "oPX5rtzVGx3pq_fc962kRjdGAeKU",
        "title": u"西安出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江大学玉泉校区",
        "destCity": u"西安",
        "destAddr": u"西安交通大学-南门 ",
        "startTime": "2015-04-29 11:00:00",
        "endTime": "2015-05-01 10:19:00"
    },
    {
        "id": 109,
        "openId": "oPX5rt_0kWFQm2H1ZGFnYb056xB0",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"广州",
        "destAddr": u"清华大学",
        "startTime": "2015-05-05 06:30:00",
        "endTime": "2015-05-06 10:30:00"
    },
    {
        "id": 110,
        "openId": "oPX5rtzVGx3pq_fc962kRjdGAeKU",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江大学玉泉校区",
        "destCity": u"青岛",
        "destAddr": u"青岛大学(宁夏路校区) ",
        "startTime": "2015-04-29 10:25:00",
        "endTime": "2015-05-01 10:25:00"
    },
    {
        "id": 111,
        "openId": "oPX5rtzVGx3pq_fc962kRjdGAeKU",
        "title": u"宝宝出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江大学玉泉校区",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-29 10:32:00",
        "endTime": "2015-05-01 10:32:00"
    },
    {
        "id": 112,
        "openId": "oPX5rt4pLMUfJbe-DD7HCDGmAniU",
        "title": u"出差",
        "note": u"",
        "startCity": u"北京",
        "startAddr": u"渭城区委党校 ",
        "destCity": u"杭州",
        "destAddr": u"浙江大学(玉泉校区)-北门 ",
        "startTime": "2015-04-29 10:56:00",
        "endTime": "2015-05-01 10:56:00"
    },
    {
        "id": 113,
        "openId": "oPX5rt4pLMUfJbe-DD7HCDGmAniU",
        "title": u"出差",
        "note": u"",
        "startCity": u"北京",
        "startAddr": u"北京银行 ",
        "destCity": u"杭州",
        "destAddr": u"浙江大学(玉泉校区)-北门 ",
        "startTime": "2015-04-29 10:56:00",
        "endTime": "2015-05-01 10:56:00"
    },
    {
        "id": 114,
        "openId": "oPX5rt4pLMUfJbe-DD7HCDGmAniU",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江大学玉泉校区",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-29 10:59:00",
        "endTime": "2015-05-01 10:59:00"
    },
    {
        "id": 115,
        "openId": "oPX5rt4pLMUfJbe-DD7HCDGmAniU",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-29 11:06:00",
        "endTime": "2015-05-01 11:06:00"
    },
    {
        "id": 116,
        "openId": "oPX5rt4pLMUfJbe-DD7HCDGmAniU",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-29 11:07:00",
        "endTime": "2015-05-01 11:07:00"
    },
    {
        "id": 117,
        "openId": "oPX5rtzZId2HRonWI0knqSmLBrVo",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-29 11:08:00",
        "endTime": "2015-05-01 11:08:00"
    },
    {
        "id": 118,
        "openId": "oPX5rt4pLMUfJbe-DD7HCDGmAniU",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-29 11:08:00",
        "endTime": "2015-05-01 11:08:00"
    },
    {
        "id": 119,
        "openId": "oPX5rt4pLMUfJbe-DD7HCDGmAniU",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-29 11:09:00",
        "endTime": "2015-05-01 11:09:00"
    },
    {
        "id": 120,
        "openId": "oPX5rt_LpVYDootmKLHcjs0Q81tA",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区文三路",
        "destCity": u"北京",
        "destAddr": u"长白山国际酒店 ",
        "startTime": "2015-04-28 09:10:00",
        "endTime": "2015-04-28 13:15:00"
    },
    {
        "id": 121,
        "openId": "oPX5rt2-lX3TBpN7dyFxiDlXV7r8",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-29 11:16:00",
        "endTime": "2015-05-01 11:16:00"
    },
    {
        "id": 122,
        "openId": "oPX5rt_0kWFQm2H1ZGFnYb056xB0",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"长白山国际酒店 ",
        "startTime": "2015-04-28 09:00:00",
        "endTime": "2015-05-01 11:16:00"
    },
    {
        "id": 123,
        "openId": "oPX5rt_0kWFQm2H1ZGFnYb056xB0",
        "title": u"北京出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"长白山国际酒店 ",
        "startTime": "2015-04-28 10:00:00",
        "endTime": "2015-04-29 15:00:00"
    },
    {
        "id": 124,
        "openId": "oPX5rt0lHMemAnl_Yz_c8zi0Opbg",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江大学玉泉校区",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-04-29 18:16:00",
        "endTime": "2015-05-01 18:16:00"
    },
    {
        "id": 125,
        "openId": "oPX5rt_LpVYDootmKLHcjs0Q81tA",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市萧山区迎宾大道",
        "destCity": u"北京",
        "destAddr": u"长白山国际酒店 ",
        "startTime": "2015-05-01 14:44:00",
        "endTime": "2015-05-03 14:44:00"
    },
    {
        "id": 126,
        "openId": "oPX5rt_0kWFQm2H1ZGFnYb056xB0",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-05-02 13:33:00",
        "endTime": "2015-05-04 13:33:00"
    },
    {
        "id": 127,
        "openId": "oPX5rt0J2vrdJB6I1VqLsLOgQsvU",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区宜山路",
        "destCity": u"厦门",
        "destAddr": u"厦门鼓浪屿码头 ",
        "startTime": "2015-05-28 10:55:00",
        "endTime": "2015-05-31 22:45:00"
    },
    {
        "id": 128,
        "openId": "oPX5rt0J2vrdJB6I1VqLsLOgQsvU",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区宜山路",
        "destCity": u"桂林",
        "destAddr": u"象鼻山 ",
        "startTime": "2015-05-06 14:30:00",
        "endTime": "2015-05-07 21:55:00"
    },
    {
        "id": 129,
        "openId": "oPX5rtzVGx3pq_fc962kRjdGAeKU",
        "title": u"厦门出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区迪臣中路",
        "destCity": u"厦门",
        "destAddr": u"厦门大学(思明校区) ",
        "startTime": "2015-05-28 18:05:00",
        "endTime": "2015-05-30 21:05:00"
    },
    {
        "id": 130,
        "openId": "",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-05-16 16:29:00",
        "endTime": "2015-05-18 16:29:00"
    },
    {
        "id": 131,
        "openId": "",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-05-16 16:36:00",
        "endTime": "2015-05-18 16:36:00"
    },
    {
        "id": 132,
        "openId": "",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-05-16 16:42:00",
        "endTime": "2015-05-18 16:42:00"
    },
    {
        "id": 133,
        "openId": "",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-05-16 16:43:00",
        "endTime": "2015-05-18 16:43:00"
    },
    {
        "id": 134,
        "openId": "",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-05-16 17:35:00",
        "endTime": "2015-05-18 17:35:00"
    },
    {
        "id": 135,
        "openId": "",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-05-16 18:46:00",
        "endTime": "2015-05-18 18:46:00"
    },
    {
        "id": 136,
        "openId": "",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"青岛",
        "destAddr": u"青岛大学医学院 ",
        "startTime": "2015-05-16 18:49:00",
        "endTime": "2015-05-18 18:49:00"
    },
    {
        "id": 137,
        "openId": "",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-05-16 18:56:00",
        "endTime": "2015-05-18 18:56:00"
    },
    {
        "id": 138,
        "openId": "",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-05-16 18:57:00",
        "endTime": "2015-05-18 18:57:00"
    },
    {
        "id": 139,
        "openId": "o9KLls-iPWXrPb73rZV-X5Cqff8M",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-05-16 19:05:00",
        "endTime": "2015-05-18 19:05:00"
    },
    {
        "id": 140,
        "openId": "oPX5rt_LpVYDootmKLHcjs0Q81tA",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"上宁桥-公交车站 ",
        "destCity": u"北京",
        "destAddr": u"联想集团 ",
        "startTime": "2015-05-19 14:00:00",
        "endTime": "2015-05-19 17:00:00"
    },
    {
        "id": 141,
        "openId": "o9KLls-iPWXrPb73rZV-X5Cqff8M",
        "title": u"青岛出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"青岛",
        "destAddr": u"青岛大学",
        "startTime": "2015-05-17 11:25:00",
        "endTime": "2015-05-19 11:25:00"
    },
    {
        "id": 142,
        "openId": "o9KLlsyPAexerHSAoL6M9skgfM8w",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-05-23 19:31:00",
        "endTime": "2015-05-25 19:31:00"
    },
    {
        "id": 143,
        "openId": "o9KLls-iPWXrPb73rZV-X5Cqff8M",
        "title": u"厦门出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区教工路138号",
        "destCity": u"厦门",
        "destAddr": u"厦门大学",
        "startTime": "2015-06-30 15:00:00",
        "endTime": "2015-06-30 23:55:00"
    },
    {
        "id": 144,
        "openId": "oPX5rt187NBQd4yIyh4pf3CeRvC8",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江大学玉泉校区",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-06-02 02:43:00",
        "endTime": "2015-06-04 02:43:00"
    },
    {
        "id": 145,
        "openId": "oPX5rt-XOAKhWYlFSwVQV_w2PcNo",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江大学玉泉校区",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-06-11 18:57:00",
        "endTime": "2015-06-13 18:57:00"
    },
    {
        "id": 146,
        "openId": "oPX5rt_pK2j7NRERYvMIPL9cD9oI",
        "title": u"旅游",
        "note": u"",
        "startCity": u"上海",
        "startAddr": u"浙江大学玉泉校区",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-06-13 14:12:00",
        "endTime": "2015-06-15 14:12:00"
    },
    {
        "id": 147,
        "openId": "oPX5rt_pK2j7NRERYvMIPL9cD9oI",
        "title": u"旅游",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江大学(玉泉校区)-北门 ",
        "destCity": u"上海",
        "destAddr": u"美罗城 ",
        "startTime": "2015-06-13 14:12:00",
        "endTime": "2015-06-15 14:12:00"
    },
    {
        "id": 148,
        "openId": "oPX5rt_pK2j7NRERYvMIPL9cD9oI",
        "title": u"出差",
        "note": u"",
        "startCity": u"杭州",
        "startAddr": u"浙江省杭州市西湖区保俶北路46号",
        "destCity": u"北京",
        "destAddr": u"清华大学",
        "startTime": "2015-06-13 14:22:00",
        "endTime": "2015-06-15 14:22:00"
    }
]


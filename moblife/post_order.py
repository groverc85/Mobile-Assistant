#-*- coding:utf-8 -*-
'''

处理提交过来的订单
1.    从活动提交过来的定单，可能有火车票、酒店订单、机票订单
2.    从单个服务过来的订单
'''

'''
导入需要用到的函数,插入数据库函数
'''
import json

from flask import request, session,flash,render_template,session

from moblife import app
from moblife.activity import login_required
from moblife.order import addUser,addTrainOrder,addFlightOrder,addHotelOrder,db,deleteTrainOrder
from moblife.models import User,TrainOrder,FlightOrder,HotelOrder
from moblife.models_activity import ActTour

'''
orders数组中有五个元素
[0]表示leave_TrainOrder
[1]表示leave_flight_order
[2]表示hotel_order
[3]表示return_TrainOrder
[4]表示return_flight_order
如果 该项为空,那么表示表示该订单无效
'''

@app.route('/makeorder/', methods = ['GET', 'POST'])
@login_required
def make_order():
    if request.method == 'POST':
        user=session['user']
        user_record = User.query.filter_by(id=user['userid']).first()
        actid=request.args.get('actid')
        ordersstr=request.form.get('orders')
        leave_train = request.form.get('leave_train')
        leave_flight = request.form.get('leave_flight')
        hotel = request.form.get('hotel')
        return_train = request.form.get('return_train')
        return_flight = request.form.get('return_flight')

        orders = json.loads(ordersstr)

        #act_record=ActTour.query.filter_by(id=actid,userid=user_record.id)
        '''
        activity_order=ActivityOrder.query.filter_by(actid=actid).first()
        if not activity_order:
            activity_order=ActivityOrder(actid,user['userid'])

        activity_order.actname=activity_record.title
        activity_order.actdatetime=activity_record.begin_datetime
        '''
        if orders[0]:
            leave_TrainOrder = orders[0]
            '''
            先判断数据库中是否已经同样的订单,判断的依据，actid,leaveTicket两个字段如果一样，则认为是同一个订单
            '''
            #离开的火车票订单
            '''
            leave_TrainOrder_obj2 = TrainOrder(actid,leave_TrainOrder['station_train_code'],leave_TrainOrder['depart_datetime'],leave_TrainOrder['from_station_name'],
                    leave_TrainOrder['arrive_datetime'],leave_TrainOrder['to_station_name'],user_record.name,user_record.IDNo,True,False)
            flag=deleteTrainOrder(leave_TrainOrder_obj2)
            if flag:
                return "deleteTrainOrder success"
            '''
            record = TrainOrder.query.filter_by(actid=actid,leaveTicket=True,returnTicket=False).first()
            if not record:
                print(orders[0])
                index = leave_TrainOrder['ticket_types'].index(leave_train)
                price = leave_TrainOrder['prices'][index]
                leave_TrainOrder_obj = TrainOrder(user_record.id, actid,
                    leave_TrainOrder['station_train_code'], leave_TrainOrder['depart_datetime'],
                    leave_TrainOrder['from_station_name'], leave_TrainOrder['arrive_datetime'],
                    leave_TrainOrder['to_station_name'], leave_train, price, user_record.name,
                    user_record.IDNo,True,False)
                
                leave_TrainOrder_obj.display()
                addTrainOrder(leave_TrainOrder_obj)
                # activity_order.leave_TrainOrderid=leave_TrainOrder_obj.id
                # activity_order.leave_train_info=leave_TrainOrder['station_train_code']+leave_TrainOrder['from_station_name']+'--'+leave_TrainOrder['to_station_name']
                
                flash(u'出发火车票下单成功。小秘书正在帮您订火车票...', 'message')
            else :
                flash(u'出发火车票已经成功下单，不能重复下单，亲！', 'message')
                
        if orders[1]:
            leave_flight_order = orders[1]
            # activity_order.leave_flight_info="深航Mu4007"
            '''
            离开机票订单数据
            '''
            record = FlightOrder.query.filter_by(actid=actid,leaveTicket=True,returnTicket=False).first()
            if not record:
                index = leave_flight_order['ticket_types'].index(leave_flight)
                price = leave_flight_order['prices'][index]
                leave_flight_order_obj =FlightOrder(user_record.id, actid,
                    leave_flight_order['flightNum'], leave_flight_order['dep_time'],
                    leave_flight_order['dep_arp'], leave_flight_order['arr_time'],
                    leave_flight_order['arr_arp'], leave_flight, price,
                    user_record.name,user_record.IDNo,True,False)
                addFlightOrder(leave_flight_order_obj)
                
                # activity_order.leave_flight_orderid=leave_flight_order_obj.id
                # activity_order.leave_flight_info=leave_flight_order['flightcomname']+leave_flight_order['flightNum']+leave_flight_order['dep_arp']+'--'+leave_flight_order['arr_arp']+leave_flight_order['dep_time']
                
                flash(u'出发飞机票下单成功.小秘书正在帮您订机票...', 'message')
                # print '航班信息-------------》',leave_flight_order
            else :
                flash(u'出发飞机票已经成功下单，不能重复下单，亲！', 'message')
        if orders[2]:
            hotel_order = orders[2]
            # activity_order.hotel_info='如家如家'
            '''
            酒店订单数据插入数据库
            '''
            record = HotelOrder.query.filter_by(actid=actid).first()
            if not record:
                index = hotel_order['bed_types'].index(hotel)
                price = hotel_order['prices'][index]
                hotel_order_obj =HotelOrder(user_record.id, actid, user_record.name,
                    user_record.IDNo, hotel_order['check_in_date'],
                    hotel_order['check_out_date'], user_record.phone, hotel_order['name'], 
                    hotel, price, hotel_order['address'])
                addHotelOrder(hotel_order_obj)
                
                # activity_order.hotel_orderid=hotel_order_obj.id
                # activity_order.hotel_info=hotel_order['name']+hotel_order['checkin_date']+u'入住 '+hotel_order['checkout_date']+u'离开'
                
                flash(u'酒店下单成功，小秘书的正在帮您订酒店...', 'message')
            else :
                flash(u'酒店已经下单成功，不能重复下单！', 'message')
        if orders[3]:
            return_TrainOrder = orders[3]
            #返程火车票订单
            record = TrainOrder.query.filter_by(actid=actid,leaveTicket=False,returnTicket=True).first()
            if not record:
                index = return_TrainOrder['ticket_types'].index(return_train)
                price = return_TrainOrder['prices'][index]
                return_TrainOrder_obj=TrainOrder(user_record.id, actid,
                    return_TrainOrder['station_train_code'], return_TrainOrder['depart_datetime'],
                    return_TrainOrder['from_station_name'], return_TrainOrder['arrive_datetime'],
                    return_TrainOrder['to_station_name'], return_train, price,
                    user_record.name, user_record.IDNo, False, True)
                addTrainOrder(return_TrainOrder_obj)
                
                # activity_order.return_TrainOrderid=return_TrainOrder_obj.id
                # activity_order.return_train_info=return_TrainOrder['station_train_code']+return_TrainOrder['from_station_name']+'--'+return_TrainOrder['to_station_name']
                
                flash(u'返程火车票下单成功，小秘书的正在帮您预订...', 'message')
            else :
                flash(u'返程火车票已经下单成功，不能重复下单！', 'message')
        if orders[4]:
            return_flight_order = orders[4]
            record = FlightOrder.query.filter_by(actid=actid,leaveTicket=False,returnTicket=True)
            if not record:
                #返程机票
                index = return_TrainOrder['ticket_types'].index(return_flight)
                price = return_TrainOrder['prices'][index]
                return_flight_order_obj =FlightOrder(user_record.id, actid,
                    return_flight_order['flightNum'], return_flight_order['dep_time'], 
                    return_flight_order['dep_arp'], return_flight_order['arr_time'],
                    return_flight_order['arr_arp'], return_flight, price,
                    user_record.name, user_record.IDNo, False, True)
                addFlightOrder(leave_flight_order_obj)
                
                # activity_order.return_flight_orderid=return_flight_order_obj.id
                # activity_order.return_flight_info=return_flight_order['flightcomname']+return_flight_order['flightNum']+return_flight_order['dep_arp']+'--'+return_flight_order['arr_arp']+return_flight_order['dep_time']
                
                flash(u'返程飞机票下单成功，小秘书的正在帮您预订...', 'message')
            else :
                flash(u'返程飞机票已经下单成功，不能重复下单！', 'message')
        
        '''
        if not activity_record:
            db.session.add(activity_order)
        db.session.commit()
        activity_order.display()
        # 活动的订单数据
        activities_orders=ActivityOrder.query.filter_by(userid=user_record.id).all()
        '''
        # 服务的订单
        TrainOrders=TrainOrder.query.filter_by(userid=user_record.id).all()
        flight_orders=FlightOrder.query.filter_by(userid=user_record.id).all()
        hotel_orders=HotelOrder.query.filter_by(userid=user_record.id).all()
        
        return render_template('order_list.html', user=user, TrainOrders=TrainOrders,
            flight_orders=flight_orders, hotel_orders=hotel_orders)
    else :
        return "不能使用get方法提交数据！"
@app.route('/deleteorder/', methods = ['GET', 'POST'])
@login_required
def delete_order():
    return 
#-*- coding:utf-8 -*-
'''
数据类对应数据库表
'''

from moblife import db,app


class User(db.Model):
    '''用户表'''
    __bind_key__ = 'xms'
    __tablehotel_name__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(30))
    openid = db.Column(db.String(30))
    password = db.Column(db.String(30))
    nickname = db.Column(db.String(30))
    name = db.Column(db.String(30))
    sex = db.Column(db.String(10))
    IDNo = db.Column(db.String(20))
    email = db.Column(db.String(120))
    email_verified = db.Column(db.Boolean)
    phone = db.Column(db.String(14))
    phone_verified = db.Column(db.Boolean)
    country = db.Column(db.String(20))
    province = db.Column(db.String(20))
    city = db.Column(db.String(20))

    #构造函数
    def __init__(self, account, openid, password, nickname, name, sex, IDNo, email, 
        email_verified, phone, phone_verified, country, province, city):
        self.account = account
        self.openid = openid
        self.password = password
        self.nickname = nickname
        self.name = name
        self.sex = sex
        self.IDNo=IDNo
        self.email = email
        self.email_verified = email_verified
        self.phone = phone
        self.phone_verified = phone_verified
        self.country = country
        self.province = province
        self.city = city

    def __repr__(self):
        return '<User %r>' % (self.hotel_name)


class TrainOrder(db.Model):       
    '''火车订单表'''
    __bind_key__ = 'xms'
    __tablehotel_name__ = "TrainOrder"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    actid = db.Column(db.Integer)
    # True mean leave trip, False mean return trip
    leave_return = db.Column(db.Boolean)
    train_num = db.Column(db.String(6))
    depart_datetime = db.Column(db.String(20))
    depart_station = db.Column(db.String(15))
    arrive_datetime = db.Column(db.String(20))
    arrive_station = db.Column(db.String(15))
    ticket_type = db.Column(db.String(10))
    price = db.Column(db.Float)
    # string of contacts' id
    passengers = db.Column(db.String(20))
    total = db.Column(db.Float)
    # True for payed, False for unpayed
    payment = db.Column(db.Boolean)
    
    def __init__(self, userid, actid, leave_return, train_num, depart_datetime,
        depart_station, arrive_datetime, arrive_station, ticket_type, price,
        passengers, total, payment):
        
        self.userid = userid
        self.actid = actid
        self.leave_return = leave_return
        self.train_num = train_num
        self.depart_datetime = depart_datetime
        self.depart_station = depart_station
        self.arrive_datetime = arrive_datetime
        self.arrive_station = arrive_station
        self.ticket_type = ticket_type
        self.price = price
        self.passengers = passengers
        self.total = total
        self.payment = payment
    
    def display(self):
        print "活动Id：",self.actid ,"火车车次: ",self.train_num,"乘客姓名：",self.passengers


class FlightOrder(db.Model):
    '''机票订单表,class: economy,business class,fist class,premium class'''
    __bind_key__ = 'xms'
    __tablehotel_name__ = "FlightOrder"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    actid = db.Column(db.Integer)
    leave_return = db.Column(db.Boolean)
    flight_num = db.Column(db.String(7))
    depart_datetime = db.Column(db.String(20))
    depart_airport = db.Column(db.String(15))
    arrive_datetime = db.Column(db.String(20))
    arrive_airport = db.Column(db.String(15))
    ticket_type = db.Column(db.String(10))
    price = db.Column(db.Float)
    passengers = db.Column(db.String(20))
    total = db.Column(db.Float)
    # True for payed, False for unpayed
    payment = db.Column(db.Boolean)
   
    def __init__(self, userid, actid, leave_return, flight_num, depart_datetime,
        depart_airport, arrive_datetime, arrive_airport, ticket_type, price,
        passengers, total, payment):
        self.userid=userid
        self.actid=actid
        self.leave_return=leave_return
        self.flight_num=flight_num
        self.depart_datetime=depart_datetime
        self.depart_airport=depart_airport
        self.arrive_datetime=arrive_datetime
        self.arrive_airport=arrive_airport
        self.ticket_type = ticket_type
        self.price = price
        self.passengers=passengers
        self.total=total
        self.payment=payment
    
    def display(self):
        print "活动Id：",self.actid,"航班号：",self.flight_num,"乘客姓名：",self.passengers


class HotelOrder(db.Model):
    '''酒店订单表'''
    __bind_key__ = 'xms'
    __tablehotel_name__ = "HotelOrder"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    actid = db.Column(db.Integer)
    hotel_name = db.Column(db.String(30))
    address = db.Column(db.String(80))
    hotel_phone = db.Column(db.String(14))
    check_in_date = db.Column(db.String(12))
    check_out_date = db.Column(db.String(12))
    bed_type = db.Column(db.String(10))
    price = db.Column(db.Float)
    room_num = db.Column(db.Integer)
    total = db.Column(db.Float)
    # id of contacts
    guest = db.Column(db.Integer)
    # True for payed, False for unpayed
    payment = db.Column(db.Boolean)
    
    def __init__(self, userid, actid, hotel_name, address, hotel_phone, check_in_date,
        check_out_date, bed_type, price, room_num, total, guest, payment):        
        self.userid = userid
        self.actid = actid
        self.hotel_name = hotel_name
        self.address = address
        self.hotel_phone = hotel_phone
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.bed_type = bed_type
        self.price = price
        self.room_num = room_num
        self.total = total
        self.guest = guest
        self.payment=payment
        
    def dispaly(self):
        print "活动Id：",self.actid,"酒店名：",self.guest,"客人姓名：",self.hotel_name


class Contact(object):
    """contacts for TrainOrder, FlightOrder and HotelOrder"""
    __bind_key__ = 'xms'
    __tablehotel_name__ = "Contact"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    name = db.Column(db.String(15))
    IDNo = db.Column(db.String(20))
    phone = db.Column(db.String(14))

    def __init__(self, userid, name, IDNo, phone):
        self.userid = userid
        self.name = name
        self.IDNo = IDNo
        self.phone = phone

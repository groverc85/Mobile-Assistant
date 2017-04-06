#-*- coding:utf-8 -*-
'''
对应数据库表的基本操作
create
update
delete
'''

from moblife.models import User,TrainOrder,FlightOrder,HotelOrder,db

'''
将传入的user对象直接当做记录插入数据库
如果成功插入：则返回插入的对象数据（以备前端再处理）
插入失败的话，返回“error”
'''
def addUser(user):
    try:
        db.session.add(user)
        db.session.commit()
        return 'add user success:%s' % name
    except Exception as e:
        db.session.rollback()
        return 'error'

		
'''
将传入的TrainOrder对象直接当做记录插入数据库
'''
def addTrainOrder(TrainOrder):
    try:
        db.session.add(TrainOrder)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return 'error'

#query.filter(User.id == 1).update({User.name: 'c'}) 更新语法
#session.delete(user) 删除元素语法
#query4 = session.query(User.id)
#query4.count()
        
def deleteTrainOrder(TrainOrder):
    try:
        db.session.delete(TrainOrder)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return 'error'
'''
将传入的filghtOrder对象直接当做记录插入数据库
'''
def addFlightOrder(flightOrder):
    try:
        db.session.add(flightOrder)
        db.session.commit()
        return flightOrder
    except Exception as e:
        db.session.rollback()
        return 'error'
        
def deleteFlightOrder(flight_order):
    try:
        db.session.delete(flight_order)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return 'error'
'''
将传入的hotelOrder对象直接当做记录插入数据库
'''
def addHotelOrder(hotelOrder):
    try:
        db.session.add(hotelOrder)
        db.session.commit()
        return hotelOrder
    except Exception as e:
        db.session.rollback()
        return 'error'

def deleteHotelOrder(hotel_order):
    try:
        db.session.delete(hotel_order)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return 'error'
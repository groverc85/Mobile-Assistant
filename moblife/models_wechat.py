from moblife import db
import time

class WechatUserInfo(db.Model):
    __bind_key__ = 'xms'
    id = db.Column(db.Integer, primary_key = True)
    subscribe = db.Column(db.Integer)
    openid = db.Column(db.String(100), unique = True)
    nickname = db.Column(db.String(50))
    sex = db.Column(db.Integer)
    city = db.Column(db.String(40))
    country = db.Column(db.String(40))
    province = db.Column(db.String(40))
    language = db.Column(db.String(40))
    headimgurl = db.Column(db.String(512))
    subscribe_time = db.Column(db.Integer)
    #unionid

    def __init__(self, obj):
        self.subscribe = obj['subscribe']
        self.openid = obj['openid']
        self.nickname = obj['nickname']
        self.sex = obj['sex']
        self.city = obj['city']
        self.country = obj['country']
        self.province = obj['province']
        self.language = obj['language']
        self.headimgurl = obj['headimgurl']
        self.subscribe_time = obj['subscribe_time']
    
    @staticmethod
    def insert(obj):
        item = WechatUserInfo(obj)        
        try:
            db.session.add(item)
            db.session.commit()
        except:
            db.session.rollback()
        return item

    @staticmethod
    def update(openid, obj):
        r = WechatUserInfo.query.filter_by(openid = openid).first()
        if r is None:
            return False
        r.subscribe = obj['subscribe']
        r.openid = obj['openid']
        r.nickname = obj['nickname']
        r.sex = obj['sex']
        r.city = obj['city']
        r.country = obj['country']
        r.province = obj['province']
        r.language = obj['language']
        r.headimgurl = obj['headimgurl']
        r.subscribe_time = obj['subscribe_time']
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return False
        return True

    @staticmethod
    def query_by_openid(openid):
        try:
            return WechatUserInfo.query.filter_by(openid = openid).first()
        except Exception as e:
            db.session.rollback()

    @staticmethod
    def delete(openid):
        pass
        
    def __str__(self):
        return '<WechatUserInfo:openid=%s,nickname=%s>' % (self.openid, self.nickname)

class WechatUserLoc(db.Model):
    __bind_key__ = 'xms'
    id = db.Column(db.Integer, primary_key = True)
    openid = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timestamp = db.Column(db.Integer)

    def __init__(self, openid, latitude, longitude):
        self.openid = openid
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = int(time.time())
        
    @staticmethod
    def insert(uid, lat, lon):
        item = WechatUserLoc(uid, lat, lon)        
        try:
            db.session.add(item)
            db.session.commit()
        except:
            db.session.rollback()
    
    @staticmethod
    def query_by_openid(openid):
        try:
            return WechatUserLoc.query.filter_by(openid = openid).order_by( db.desc(WechatUserLoc.timestamp) ).first()
        except Exception as e:
            db.session.rollback()
            
    def __str__(self):
        return '<WechatUserLoc:openid=%s,lat=%s,lon=%s>' % (self.openid, self.latitude, self.longitude)
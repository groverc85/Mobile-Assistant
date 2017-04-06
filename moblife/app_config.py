class Config(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://:memory:'

class LocalDevConfig(Config):
    from datetime import timedelta
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@192.168.0.101/xms'
    SQLALCHEMY_BINDS = {
        'xms': 'mysql://root:root@192.168.0.101/xms',
    }
    SQLALCHEMY_POOL_RECYCLE = 5

    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    SECRET_KEY = '\x82\xe2/\x1fq\xc4\xa1\xfcw\x11\xdf\xbe\x12'
    # for Flask-WTF
    CSRF_ENABLED = True
    
class RemoteDevConfig(Config):
    from datetime import timedelta
    DEBUG = True
    SERVER_NAME = 'xms.ok-api.cn'
    SQLALCHEMY_DATABASE_URI = 'mysql://xms:xmsdbroot@101.71.0.22/xms'
    SQLALCHEMY_BINDS = {

        'xms': 'mysql://xms:xmsdbroot@101.71.0.22/xms',
    }
    SQLALCHEMY_POOL_RECYCLE = 5

    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    SECRET_KEY = '\x82\xe2/\x1fq\xc4\xa1\xfcw\x11\xdf\xbe\x12'
    # for Flask-WTF
    CSRF_ENABLED = True
    
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://stMWFmP5H8P8j23LhDzzvSQV:ScOHl8ATsrDw00iXzT5u2qCyEhyMSpf7@sqld.duapp.com:4050/pRtvtvsLEvRpREHGnHOA'
    SQLALCHEMY_POOL_RECYCLE = 5
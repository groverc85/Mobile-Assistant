# -*- coding:utf-8 -*-

from moblife import app, db
from flask import request

@app.route('/test/requests')
def req():
    try:
        import requests
        r = requests.get('http://www.qq.com')
        return r.text
    except Exception as e:
        return str(e)
        
@app.route('/test/cache')
def cache():
    body = []
    id = request.args.get('id', None)
    try:        
        from cache import gecache, setcache
        from moblife.models_wechat import WechatUserInfo
        users = WechatUserInfo.query.all()
        body.append('user%s: %s' % (len(users), users))
        if setcache(id, users):
            body.append('success')
        else:
            body.append(str(getlasterror()))
        val = getcache(id)
        body.append('key : %s' % id)
        for user in val:
            body.append('value : %s' % val)
        body.append('last except: %s' % getlasterror())
    except Exception as e:
        body.append(str(e))
    
    return '<br>'.join(body)
    
@app.route('/test/thread')
def thread():
    body = []
    import time
    def run():
        with open('/home/bae/log/tt.txt') as f:
            f.write('ss')

    try:
        body.append('import threading')
        from threading import Thread
        t = Thread(target = run)
        t.start()
        db.session.add(u)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            
        body.append('returned')
        body.append('thread is alive: %s' % t.is_alive())
        body.append('thread is a daemon: %s' % t.daemon)
        
    except Exception as e:
        body.append(str(e))
        
    return '<br>'.join(body)
    
@app.route('/test/log')
def log():
    body = []
    try:
        from log import logger
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.fatal("fatal message")
        logger.log(12, "trace message")
        body.append('returned')
    except Exception as e:
        body.append(str(e))
        
    return '<br>'.join(body)
        
@app.route('/test/log_local')
def log_local():
    body = []
    try:
        import logging
        logger = logging.getLogger('abcd')
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.fatal("fatal message")
        logger.log(12, "trace message")
        body.append('returned')
    except Exception as e:
        body.append(str(e))
        
    return '<br>'.join(body)
    
@app.route('/itinerary/route')
def traval():
    import time,datetime,json
    origin = (request.args.get('startLat'), request.args.get('startLng'))
    dest = (request.args.get('endLat'), request.args.get('endLng'))
    pref = request.args.get('pref', '').split(',')
    time = tuple(map(float, request.args.get('time', '').split(',')))
    #origin = (30.277648,120.146503)
    #dest = (39.9352,116.406534)
    import routing
    service = routing.GetRouting(origin, dest, time, pref)
    return "var routing = " + json.dumps(service, ensure_ascii = False, indent = 4)
    
@app.route('/itinerary/activity')
def activity():
    import time,datetime,json
    acts = {
        'status': 0, 
        'message': 'ok', 
        'activities': [
            {
                'act_id': 1, 
                'name': u'CBMP出差', 
                'origin':
                {
                    'address': u'西溪校区', 
                    'lat':30.277869, 
                    'lng':120.147477
                },
                'destination':
                {
                    'address': u'东华大学',
                    'lat':31.210809,
                    'lng':121.421229
                },
                'start_time': time.mktime(datetime.datetime(2014,12,5,9).timetuple()),
                'end_time': time.mktime(datetime.datetime(2014,12,5,18).timetuple())
            },
            {
                'act_id': 2, 
                'name': u'PETS5考试', 
                'origin':
                {
                    'address': u'玉泉校区', 
                    'lat':1, 
                    'lng':1
                },
                'destination':
                {
                    'address': u'浙江工商大学教工路校区',
                    'lat':1,
                    'lng':1
                },
                'start_time': time.time(),
                'end_time': time.time()
            }
        ]}
    return 'var result = ' + json.dumps(acts, ensure_ascii = False, indent = 4) 
        
@app.route('/test/subprocess')
def sub():
    import subprocess
    cmd = request.args.get('cmd', 'pwd')
    err = file('/home/bae/log/subprocess.err.log', 'a')
    out = file('/home/bae/log/subprocess.out.log', 'a')
    try:
        output = subprocess.check_output(cmd, shell = True, stderr = err)
        out.writelines(output)
        return output
    except subprocess.CalledProcessError as cpe:
        return '%s\n%s' % (cpe.returncode, cpe.output)
    finally:
        out.close()
        err.close()
#-*- coding:utf-8 -*-
from moblife import app, wechat_api
from moblife.service import *
from moblife.models_wechat import WechatUserInfo, WechatUserLoc

from flask import render_template, url_for, redirect, request

import datetime, json

@app.route('/act/localService')
def localService():
    '''
    location = {
        'city': '',
        'address':u'浙江大学玉泉校区',
    }
    '''
    address = u'青岛大学'
    city = get_city(address)
    return city
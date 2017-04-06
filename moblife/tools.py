# -*- coding: utf-8 -*-

from moblife import app
from flask import render_template
from moblife.wechat_api import configs, get_access_token
import urllib

@app.template_filter('urlencode')
def urlencode_filter(url):
    return urllib.quote(url, '')

@app.route('/wechat/tool/menu')
def wechat_menu():
    return render_template('wechat_menu.js', appid = configs['appid'])
    
@app.route('/wechat/tool/access_token')
def access_token():
    return get_access_token()
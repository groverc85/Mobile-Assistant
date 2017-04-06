# -*- coding: utf-8 -*-

from moblife import app
from flask import request
import requests
from wechat_api import configs, get_web_token

@app.route('/help/basic')
def help_basic():
    return 'help about basic service'
    return u"<a href='https://open.weixin.qq.com/connect/oauth2/authorize?appid=" + configs['appid'] + u"&redirect_uri=http%3A%2F%2Fsonics.duapp.com%2Fusers%2Fauth&response_type=code&scope=snsapi_base&state=123#wechat_redirect'>点击授权snsapi_base</a><a href='https://open.weixin.qq.com/connect/oauth2/authorize?appid=" + configs['appid'] + u"&redirect_uri=http%3A%2F%2Fsonics.duapp.com%2Fusers%2Fauth&response_type=code&scope=snsapi_userinfo&state=123#wechat_redirect'>点击授权snsapi_userinfo</a>"

@app.route('/help/conversation')
def help_conv():
    return 'help about basic wechat message'
    
@app.route('/users/auth')
def user_auth():
    code = request.args.get('code')
    state = request.args.get('state')
    resp = get_web_token(code)
    return 'code: %s<br>state: %s<br> %s' % (code, state, resp['openid'])
    
pass
#-*- coding:utf-8 -*-

from flask import Flask, Blueprint, url_for, render_template, request, session, g, redirect, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.session import Session
from functools import wraps

import os, json

app = Flask(__name__)
config = os.environ.get('moblife_config', 'moblife.app_config.RemoteDevConfig')
app.config.from_object(config)
db = SQLAlchemy(app)
Session(app)

import moblife.wechat 
import moblife.activity, moblife.dyh_test
import moblife.post_order
import moblife.trainandplane
import moblife.test
import moblife.users
import moblife.hotel
import moblife.tools
import moblife.wechat_api
from moblife.models_wechat import WechatUserInfo
from moblife.models_activity import *
from moblife.activity import login_required
from moblife.models import User
#the module below is the testing file for Zhaolang
import moblife.zl_testfile


def modify_userid(model_, oldid, newid):
    # 将外键为user_openid.userid的相关记录的外键改为user_record.userid
    records = model_.query.filter_by(userid=oldid).all()
    for record in records:
        record.userid = newid
    db.session.commit()

@app.route('/')
def index():
    if 'user' in session:
        user = session['user']
        return render_template('index.html',user=user)
    return render_template('index.html')


@app.route('/login', methods = ['GET', 'POST'])
def login():
    request_url = request.args.get('request_url')
    if not request_url:
        request_url = url_for('.index')
    if request.method == 'GET':
        if 'user' in session:
            user_record = User.query.filter_by(id=session['user']['userid']).first()
            # 如果没有account，说明是微信openid账号
            if user_record.account:
                flash(u'您已登录，无需重复登录', 'message')
                return redirect(request_url)
        return render_template("login.html", request_url=request_url)
    if request.method == 'POST':
        account = request.form.get('account')
        password = request.form.get('password')
        user_record = User.query.filter_by(account=account, password=password).first()
        if user_record:
            # 只可能是微信端的session，无account
            if 'user' in session:
                try:
                    user_openid = User.query.filter_by(userid=session['user']['userid']).first()
                    user_record.openid = user_openid.openid
                    db.session.commit()
                    # 将外键为user_openid.userid的相关记录的外键改为user_record.userid
                    modify_userid(ActTour, user_openid.id, user_record.id)
                    modify_userid(ActPref, user_openid.id, user_record.id)
                    modify_userid(Timeline, user_openid.id, user_record.id)
                except Exception, e:
                    return str(e)

            session['user'] = {
                #'subscribe': user_record.subscribe,
                'userid': user_record.id,
                'nickname': user_record.nickname,
                'sex': user_record.sex,
                'country': user_record.country,
                'province': user_record.province,
                'city': user_record.city,
                #'language': user_record.language,
                #'headimgurl': user_record.headimgurl,
                #'subscribe_time': user_record.subscribe_time
            }
        else:
            flash(u'用户名或密码错误', 'message')
            return redirect(url_for(".login", request_url=request_url))
        return redirect(request_url)


@app.route('/logout')
def logout():
    # 如果会话中有用户就删除它。
    session.pop('user', None)
    flash(u'您已退出', 'message')
    return redirect(url_for('index'))


@app.route('/register', methods = ['GET', 'POST'])
def register():
    ua = request.headers.get('User_Agent', '').lower()
    # 如果不是微信浏览器访问register，清除session中的user
    if 'micromessenger' not in ua:
        # 如果会话中有用户就删除它。
        session.pop('user', None)
    if request.method == 'GET':
        return render_template("register.html")
    if request.method == 'POST':
        account = request.form.get('account')
        password = request.form.get('password')
        nickname = request.form.get('nickname')
        name = request.form.get('name')
        sex = request.form.get('sex')
        phone = request.form.get('phone')
        IDNo = request.form.get('IDNo')
        country = request.form.get('country')
        province = request.form.get('province')
        city = request.form.get('city')
        if 'user' not in session:
            user_record = User.query.filter_by(account=account).first()
            if user_record:
                flash(u'该账号已经存在', 'message')
                return render_template("register.html")
            #randint_suffix = randint(0,100000)
            #account = 'xms%d' % randint_suffix
            user = User(account, '', password, nickname, name, sex, IDNo, '', False, phone, False, country, province, city)
            db.session.add(user)
            db.session.commit()
            flash(u'注册成功，请登录', 'message')
        elif 'user' in session:
            user = session['user']
            user_record = User.query.filter_by(id=user['userid']).first()
            # 不判断也可以，因为微信跳转过来的肯定没有account，浏览器跳转过来的session会被清除
            if not user_record.account:
                user_record.account = account
                user_record.password = password
                user_record.nickname = nickname
                user_record.name = name
                user_record.sex = sex
                user_record.phone = phone
                user_record.IDNo = IDNo
                user_record.country = country
                user_record.province = province
                user_record.city = city
                db.session.commit()
                flash(u'注册成功，请登录', 'message')
    return redirect(url_for('.login'))


@app.route('/db_init')
def dbinit():
    try:
        db.create_all()
    except Exception as e:
        return 'init db  fails, reason: %s' % e
    return 'init db  sucess' 


def main():
    app.config.from_object('moblife.app_config.LocalDevConfig')
    app.run(host='0.0.0.0')
#-*- coding:utf-8 -*-
#酒店，吃饭

from moblife import app
from moblife.apis import lodging
from moblife.apis import catering
from moblife.apis import maps
from moblife.models_wechat import WechatUserInfo
from flask import render_template,url_for,redirect,request

#酒店住宿，搜索主页
@app.route('/basic/lodging',methods=['POST','GET'])
def basic_lodging():
	openId = request.args.get('openId')
	user = WechatUserInfo.query_by_openid(openId)
	return render_template('hotel_query.html', user = user)

#搜索酒店结果页面
'''
需要的参数有，城市，入住时间，退房时间，关键字，酒店星级，价格
city,startTime,endTime,keyWord,star,price
'''
@app.route('/basic/lodging/list',methods=['POST','GET'])
def basic_hotel_list():
	if request.method=='POST':
		city=request.form['city']
		#startTime=request.form['startTime']
		#endTime=request.form['endTime']
		keyWord=request.form['keyWord']
		#star=request.form['star']
		price=request.form['price']
		#先将地点转化为地图坐标
		loc=maps.GetLocationParam(keyWord,city)
	elif request.method == 'GET':
		city = request.args.get('city')
		keyWord = request.args.get('keyWord')
		#lat = request.args.get('lat')
		#lon = request.args.get('lon')
		#loc = (lat, lon)
		price = request.args.get('price')
		loc=maps.GetLocationParam(keyWord,city)
	else:
		city = keyWord = price = None
	
	#通过loc去调用百度酒店api
	response=lodging.baiduGetLodging(loc,price)
	#print response
	hotels=[]
	noResult=False
	openId = request.args.get('openId')
	user = WechatUserInfo.query_by_openid(openId)
	if response['status']!=0:
		noResult=True
		return render_template('hotel_list.html',hotels=hotels,noResult=noResult, user = user)
	else:
		for hotel in response['results']:
			try:
				hotelName=hotel['name']
				address=hotel['address']
				tel=hotel['telephone']
				#酒店详情数据
				detail=hotel['detail_info']
				price=detail['price']
				#顾客评分
				rating=detail['overall_rating']
				url=detail['detail_url']
				hotels.append({'hotelName':hotelName,
								'address':address,
								'tel':tel,
								'detail':detail,
								'price':price,
								'rating':rating,
								'url':url
				})
			except Exception as e:
				pass
		return render_template('hotel_list.html',hotels=hotels,noResult=noResult, user = user)
	
	
#餐饮美食搜索
@app.route('/basic/catering',methods=['POST','GET'])
def basic_catering():
	openId = request.args.get('openId')
	user = WechatUserInfo.query_by_openid(openId)
	return render_template('dinner_query.html', user = user)
#餐饮美食搜索结果

@app.route('/basic/catering/list',methods=['POST','GET'])
def basic_catering_list():
	if request.method=='POST':
		city=request.form['city']
		#startTime=request.form['startTime']
		#endTime=request.form['endTime']
		keyWord=request.form['keyWord']
		#star=request.form['star']
		price=request.form['price']
		#先将地点转化为地图坐标
		loc=maps.GetLocationParam(keyWord,city)
	elif request.method == 'GET':
		lat = request.args.get('lat')
		lon = request.args.get('lon')
		loc = (lat, lon)
		price = request.args.get('price')
	else:
		city = keyWord = price = None
	#通过loc去调用百度酒店api
	response=catering.baiduGetCatering(loc,price)
	print response
	
	dinners=[]
	noResult=False
	openId = request.args.get('openId')
	user = WechatUserInfo.query_by_openid(openId)
	if(response['status']!=0):
		noResult=True
		return render_template('dinner_list.html',dinners=dinners,noResult=noResult, user = user)
	else :
		for dinner in response['results']:
			try:
				name=dinner['name']
				address=dinner['address']
				tel=dinner['telephone']
				#酒店详情数据
				detail=dinner['detail_info']
				price=detail['price']
				#顾客评分
				rating=detail['overall_rating']
				url=detail['detail_url']
				dinners.append({'name':name,
								'address':address,
								'tel':tel,
								'detail':detail,
								'price':price,
								'rating':rating,
								'url':url
				})
			except:
				pass
		return render_template('dinner_list.html',dinners=dinners,noResult=noResult, user = user)






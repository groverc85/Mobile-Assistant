# -*- coding:utf-8 -*-

configs = {
    'appid': 'wx205afe2dc89bf1bb',
    'appsecret': '1f7e4d5b4c418bb66713cf0a2e39f738',
    'token': 'xiaomishu'
}

urls = {
    'token': 'https://api.weixin.qq.com/cgi-bin/token',
    'semantic': 'https://api.weixin.qq.com/semantic/semproxy/search'
}

import time, hashlib
import requests
import xml.etree.ElementTree as ET

_access_token = None
_access_token_expire = None

def get_access_token():
    global _access_token, _access_token_expire
    t = time.time()
    if not _access_token or _access_token_expire < t:
        p = {'grant_type': 'client_credential', 'appid': configs['appid'], 'secret': configs[
        'appsecret']}
        r = requests.get(urls['token'], params = p)
        resp = r.json()
        _access_token = resp['access_token']
        _access_token_expire = t + resp['expires_in']
    return _access_token

def get_semantic(query, uid = None, category = ['map','restaurant','hotel','train','flight'], lat = None, lon = None, city = None, region = None):
    data = {
        'query': query,
        'category': ','.join(category),
        'appid': configs['appid']
    }
    if uid != None:
        data['uid'] = uid
    if lat != None and lon != None:
        data['latitude'] = lat
        data['longitude'] = lon
    elif city != None:
        data['city'] = city
    elif region != None:
        data['region'] = region

    p = { 'access_token': get_access_token() }
    return requests.post(urls['semantic'], params = p, json = data).json()

def get_user_list():
    next_openid = ''    
    p = {'access_token': get_access_token(), 'next_openid': next_openid}
    r = requests.get('https://api.weixin.qq.com/cgi-bin/user/get', params = p)
    result = r.json()
    for id in result['data']['openid']:
        yield id
        
def get_user_info(openid):
    p = {'access_token': get_access_token(), 'openid': openid}
    r = requests.get('https://api.weixin.qq.com/cgi-bin/user/info', params = p)
    return r.json()

def send_message(openid, text):
    p = {'access_token': get_access_token()}
    data = { "touser" : openid, "text":{   "content" : text }, "msgtype":"text" }
    r = requests.post("https://api.weixin.qq.com/cgi-bin/message/mass/preview", params = p, json = data)
    print(r.text)

def check_signature(signature, timestamp, nonce):
    tmpArr = sorted([configs['token'], timestamp, nonce])
    tmpStr = ''.join(tmpArr)
    tmpStr = hashlib.sha1(tmpStr).hexdigest()
    return tmpStr == signature

def get_web_token(code):
    params = {'appid': configs['appid'], 'secret': configs['appsecret'], 'code': code, 'grant_type':'authorization_code'}
    return requests.get("https://api.weixin.qq.com/sns/oauth2/access_token", params = params).json()

class MessageBase(object):
    
    def __init__(self, content):
        self.content = content
        self._reply = ''
        try:
            self.xml = ET.fromstring(content)
            self.to_id = self.xml.find('ToUserName').text
            self.from_id = self.xml.find('FromUserName').text
            self.type = self.xml.find('MsgType').text
            self.time = self.xml.find('CreateTime').text

            self.on_message()
            
            if self.type == 'event':
                self.event = self.xml.find('Event').text
                self.on_event()
                if self.event == 'subscribe':
                    self.event_subscribe()
                elif self.event == 'unsubscribe':
                    self.event_unsubscribe()
                elif self.event == 'LOCATION':
                    self.loc_lat = self.xml.find('Latitude').text
                    self.loc_lon = self.xml.find('Longitude').text
                    self.loc_precision = self.xml.find('Precision').text
                    self.event_location()
                elif self.event == 'CLICK':
                    self.click_key = self.xml.find('EventKey').text
                    self.event_click()
                elif self.event == 'VIEW':
                    self.view_key = self.xml.find('EventKey').text
                    self.event_view()
            else:
                self.id = self.xml.find('MsgId').text
                self.on_basic()
                if self.type == 'text':
                    self._text()
                elif self.type == 'image':
                    self._image()
                elif self.type == 'voice':
                    self._voice()
                elif self.type == 'video':
                    self._video()
                elif self.type == 'location':
                    self._location()
                elif self.type == 'link':
                    self._link()
                else:
                    raise Exception('unkonw message')
                
        except Exception as e:
            self.error = e
            self.reply_text("error occurs:\n%s" % self.error)
    
    def _text(self):
        self.text = self.xml.find('Content').text
        self.on_text()
    
    def _image(self):
        self.pic_url = self.xml.find('PicUrl').text
        self.media_id = self.xml.find('MediaId').text
        self.on_image()

    def _voice(self):
        self.media_id = self.xml.find('MediaId').text
        self.voice_format = self.xml.find('Format').text
        self.recognition = self.xml.find('Recognition').text
        self.on_voice()
        
    def _video(self):
        self.media_id = self.xml.find('MediaId').text
        self.video_thumb = self.xml.find('ThumbMediaId').text
        self.on_video()
    
    def _location(self):
        self.loc_x = self.xml.find('Location_X').text
        self.loc_y = self.xml.find('Location_Y').text
        self.loc_scale = self.xml.find('Scale').text
        self.loc_label = self.xml.find('Label').text
        self.on_location()
        
    def _link(self):
        self.link_url = self.xml.find('Url').text
        self.link_title = self.xml.find('Title').text
        self.link_desc = self.xml.find('Description').text
        self.on_link()
    
    def event_click(self):
        #click_key
        self.reply_text(u'您点击了一个拉取消息命令:%s' % self.click_key)
    
    def event_location(self):
        #loc_lat, loc_lon, loc_precision
        self.reply_text(u'您当前的位置是:(%s, %s, %s)' % (self.loc_lat, self.loc_lon, self.loc_precision))
        
    def event_subscribe(self):
        self.reply_text(u'欢迎您订阅我们的微信公众号，我们将竭诚为您服务')
        
    def event_unsubscribe(self):
        self.reply_text(u'取消关注')
        
    def event_view(self):
        self.reply_text(u'您点击了一个查看页面:%s' % self.view_key)

    
    def on_message(self):
        #to_id, from_id, type
        pass
        
    def on_event(self):
        #event 
        pass
    
    def on_basic(self):
        #id, time
        pass
        
    def on_text(self):
        #text
        self.reply_text(u'您发送了一条消息:%s' % self.text)
    
    def on_image(self):
        #pic_url, media_id
        self.reply_image(self.media_id)
        
    def on_voice(self):
        #media_id
        self.reply_voice(self.media_id)
        
    def on_video(self):
        pass
        
    def on_location(self):
        pass
        
    def on_link(self):
        pass
    
    def reply_text(self, text):
        self._reply_type = 'text'
        self._reply = '<Content><![CDATA[%s]]></Content>' % text
        
    def reply_image(self, image_id):
        self._reply_type = 'image'
        self._reply = '<Image><MediaId><![CDATA[%s]]></MediaId></Image>' % image_id
    
    def reply_voice(self, voice_id):
        self._reply_type = 'voice'
        self._reply = '<Voice><MediaId><![CDATA[%s]]></MediaId></Voice>' % voice_id
        
    def reply_video(self, video_id, title = None, desc = None):
        self._reply_type = 'voice'
        self._reply = '''<Video>
            <MediaId><![CDATA[%s]]></MediaId>
            <Title><![CDATA[%s]]></Title>
            <Description><![CDATA[%s]]></Description>
            </Video> ''' % (video_id, title, desc)
        
    def reply_music(self, music_id, ):
        pass
        
    def reply_news(self, articles):
        items = []
        for atc in articles:
            items.append(self.get_article_text(atc))
        body = '<Articles>%s</Articles>' % ''.join(items)
        tpl = ['<ArticleCount>%d</ArticleCount>' % len(articles)]
        tpl.append(body)
        self._reply_type = 'news'
        self._reply = ''.join(tpl)
        
    def get_article_text(self, article):
        text = ['<item>']
        if 'title' in article:
            text.append('<Title><![CDATA[%s]]></Title>' % article['title'])
        if 'description' in article:
            text.append('<Description><![CDATA[%s]]></Description>' % article['description'])
        if 'picurl' in article:
            text.append('<PicUrl><![CDATA[%s]]></PicUrl>' % article['picurl'])
        if 'url' in article:
            text.append('<Url><![CDATA[%s]]></Url>' % article['url'])
        text.append('</item>')
        return '\n'.join(text)
        
    def reply(self):
        if self._reply is None or self._reply == '':
            self.reply_text(self.type + self.content.replace(']', '|').replace('>','|'))
            
        return '''<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[%s]]></MsgType>
%s
</xml>''' % (self.from_id, self.to_id, int(time.time()), self._reply_type, self._reply)
        
if __name__ == '__main__':
    #s = get_semantic(u'查一下三天内上海的天气', city = u'杭州', category = ['weather'])
    #print(s)
    for id in get_user_list():
        print(get_user_info(id))
    #for i in range(10):
        #send_message('oTZA7t6ehLaWUt9ctE3f0owYnSgA', 'fdas, %s' % i)

{
	"button": [{
		"name": "主页",
        "type": "view",
        "url": "{{ url_for('.index', _external = True) }}"
		
	}, {
		"name": "我的活动",
		"sub_button": [{
			"type": "view",
			"name": "活动列表",
			"url": "{{ url_for('.act_mine', _external = True)}}"
		}, {
			"type": "view",
			"name": "新建活动",
			"url": "{{ url_for('.act_new', _external = True)}}"
		}, {
            "type": "view",
            "name": "偏好设置",
            "url": "{{ url_for('.act_pref', _external = True)}}"
        }]
	}, {
		"name": "快捷服务",
		"sub_button": [{
            "type": "click",
            "name": "查天气",
            "key": "basic_weather"
        }]
	}]
}
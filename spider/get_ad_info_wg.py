#!/usr/bin/env python
#encoding=utf-8
import MySQLdb
import requests
import json
import urllib
import traceback
import re
from bs4 import BeautifulSoup
import time
import xmltodict
from config import *
import datetime
import cPickle
import uuid

reload(sys)
sys.setdefaultencoding('utf8')

db_conn = new_session()
mylogger = get_logger('adv_record')

import imghdr
import os

def download_img(url, file_path):
	new_file_path = '' 
	try:
		#url, name = args
		if not os.path.isfile(file_path):
			#mylogger.info("downloading pic ... %s" % (file_path))
			urllib.urlretrieve(url, "%s" % (file_path))
			if os.path.exists(file_path) :
				imgType = imghdr.what(file_path)
				if imgType is not None :
					new_file_path = "%s.%s" %(file_path, imgType)
					os.rename(file_path, new_file_path)
	except Exception,e:
		mylogger.error(traceback.format_exc())
		return ''
	return new_file_path

#channel_name, channel_id
#u"首页大图/大屏轮播图/banner 	1"
#u"热门图标推荐				2"
#u"精品速递/专题推荐 			3"
#u"榜单推荐 					4"
url_map = {
		#channelId, position_type_id, position_name, url, headers, get/post
		'xiaomi_android_game_pos1' : [5, 1, '首页大图', u'http://app.migc.xiaomi.com/cms/interface/v5/featured1.php', {}, 'get', 'json', 'Android'],
		'xiaomi_android_game_pos2' : [5, 1, '推荐游戏', u'http://app.migc.xiaomi.com/cms/interface/v5/recommend1.php', {},'get', 'json', 'Android'],
		'xiaomi_android_game_pos3' : [5, 2, '免费精品', u'http://app.migc.xiaomi.com/cms/interface/v5/subjectgamelist1.php?subId=478', {}, 'get', 'json', 'Android'],
		'xiaomi_android_game_pos4' : [5, 2, '米游', u'http://app.migc.xiaomi.com/cms/interface/v5/subjectgamelist1.php?subId=564', {}, 'get', 'json', 'Android'],
		
		'dangle_android_game_pos1' : [15, 1, '大屏轮播图', u'http://api2014.digua.d.cn/newdiguaserver/game/recommend/adv', {'HEAD':{"stamp":"1451986884466","verifyCode":"689f043e8a8dc193941585c1f14c2d79","it":2,"resolutionWidth":720,"imei":"868008021943653","clientChannelId":"100550","versionCode":751,"mac":"50:a7:2b:33:57:56","vender":"ARM","vp":"","version":"7.5.1","sign":"14b44ffc3f342739","dd":320,"sswdp":"360","hasRoot":0,"glEsVersion":131072,"device":"Che2-UL00","ss":2,"local":"zh_CN","language":"2","sdk":19,"resolutionHeight":1280,"osName":"4.4.2","gpu":"Mali-450 MP"}}, 'post', 'json', 'Android'],
		'dangle_android_game_pos2' : [15, 1, '首页大图', u'http://api2014.digua.d.cn/newdiguaserver/game/index720', {'HEAD':{"stamp":"1452049998709","verifyCode":"689f043e8a8dc193941585c1f14c2d79","it":2,"resolutionWidth":720,"imei":"868008021943653","clientChannelId":"100550","versionCode":751,"mac":"50:a7:2b:33:57:56","vender":"ARM","vp":"","version":"7.5.1","sign":"a301e62ed9bf6036","dd":320,"sswdp":"360","hasRoot":0,"glEsVersion":131072,"device":"Che2-UL00","ss":2,"local":"zh_CN","language":"2","sdk":19,"resolutionHeight":1280,"osName":"4.4.2","gpu":"Mali-450 MP"}}, 'post', 'json', 'Android'],
		'dangle_android_game_pos3' : [15, 1, '网游大屏轮播图', u'http://api2014.digua.d.cn/newdiguaserver/netgame/recommend/adv', {'HEAD': {"stamp":"1452049042162","verifyCode":"689f043e8a8dc193941585c1f14c2d79","it":2,"resolutionWidth":720,"imei":"868008021943653","clientChannelId":"100550","versionCode":751,"mac":"50:a7:2b:33:57:56","vender":"ARM","vp":"","version":"7.5.1","sign":"0ba0c5045450919c","dd":320,"sswdp":"360","hasRoot":0,"glEsVersion":131072,"device":"Che2-UL00","ss":2,"local":"zh_CN","language":"2","sdk":19,"resolutionHeight":1280,"osName":"4.4.2","gpu":"Mali-450 MP"}}, 'post', 'json', 'Android'],

		'sogou_android_zhushou_pos1' : [14, 1, '大屏轮播图', u'http://mobile.zhushou.sogou.com/m/focus.html?tid=4', {}, 'get', 'json', 'Android'],
		'sogou_android_zhushou_pos2' : [14, 1, '首页大图', u'http://mobile.zhushou.sogou.com/m/focus.html?tid=2', {}, 'get', 'json', 'Android'],
		'sogou_android_zhushou_pos3' : [14, 1, '首页大图', u'http://mobile.zhushou.sogou.com/android/onlinegame.html?iv=40', {}, 'get', 'json', 'Android'],
				
		'meizu_android_game_pos1' : [25, 1, '大屏轮播图', u'http://api-game.meizu.com/games/public/feed/layout?start=0&mzos=4.0&os=21&vc=75&max=20', {}, 'get', 'json', 'Android'],
		'meizu_android_game_pos2' : [25, 1, '首页大图', u'http://api-game.meizu.com/games/public/feed/layout?start=0&mzos=4.0&os=21&vc=75&max=20', {}, 'get', 'json', 'Android'],
		'meizu_android_game_pos3' : [25, 2, '图标推荐', u'http://api-game.meizu.com/games/public/feed/layout?start=0&mzos=4.0&os=21&vc=75&max=20', {}, 'get', 'json', 'Android'],
		'meizu_android_game_pos4' : [25, 3, '热门推荐', u'http://api-game.meizu.com/games/public/feed/layout?start=0&mzos=4.0&os=21&vc=75&max=20', {}, 'get', 'json', 'Android'],
		'meizu_android_game_pos5' : [25, 3, '人气首发', u'http://api-game.meizu.com/games/public/feed/layout?start=0&mzos=4.0&os=21&vc=75&max=20', {}, 'get', 'json', 'Android'],
		
		'youku_android_game_pos1' : [13, 1, '大屏轮播图', u'http://api.gamex.mobile.youku.com/app/box?product_id=1&pg=1&pz=10&pid=642a656c40601971', {}, 'get', 'json', 'Android'],
		'youku_android_game_pos2' : [13, 2, '编辑推荐', u'http://api.gamex.mobile.youku.com/app/box?product_id=1&pg=1&pz=10&pid=642a656c40601971', {}, 'get', 'json', 'Android'],
		'youku_android_game_pos3' : [13, 3, '热门网游', u'http://api.gamex.mobile.youku.com/app/box?product_id=1&pg=1&pz=10&pid=642a656c40601971', {}, 'get', 'json', 'Android'],
		'youku_android_game_pos4' : [13, 1, '首页大图', u'http://api.gamex.mobile.youku.com/app/box?product_id=1&pg=1&pz=10&pid=642a656c40601971', {}, 'get', 'json', 'Android'],
		'youku_android_game_pos5' : [13, 3, '精品单机', u'http://api.gamex.mobile.youku.com/app/box?product_id=1&pg=1&pz=10&pid=642a656c40601971', {}, 'get', 'json', 'Android'],
		'youku_android_game_pos6' : [13, 3, '新品专区', u'http://api.gamex.mobile.youku.com/app/box?product_id=1&pg=1&pz=10&pid=642a656c40601971', {}, 'get', 'json', 'Android'],
		'youku_android_game_pos7' : [13, 3, '经典端游改编', u'http://api.gamex.mobile.youku.com/app/box?product_id=1&pg=1&pz=10&pid=642a656c40601971', {}, 'get', 'json', 'Android'],
		'youku_android_game_pos8' : [13, 3, '经典影视改编网游', u'http://api.gamex.mobile.youku.com/app/box?product_id=1&pg=1&pz=10&pid=642a656c40601971', {}, 'get', 'json', 'Android'],
		'youku_android_game_pos9' : [13, 3, '经典动漫改编网游', u'http://api.gamex.mobile.youku.com/app/box?product_id=1&pg=2&pz=10&pid=6b5f94f4ab33c702', {}, 'get', 'json', 'Android'],
		'youku_android_game_pos10' : [13, 1, '大屏轮播图', u'http://api.gamex.mobile.youku.com/app/opertab?product_id=1&pg=1&pz=40&pid=6b5f94f4ab33c702', {}, 'get', 'json', 'Android'],
		
		'baidu_android_game_pos1' : [29, 1, '首页大图', u'http://m.baidu.com/appsrv?psize=3&usertype=1&is_support_webp=true&ver=16786881&from=1011080v&cen=cuid_cut_cua_uid&action=gamepage&native_api=1&pn=0', {}, 'get', 'json', 'Android'],
		'baidu_android_game_pos2' : [29, 1, '流行游戏风向标', u'http://m.baidu.com/appsrv?psize=3&usertype=1&is_support_webp=true&ver=16786881&from=1011080v&cen=cuid_cut_cua_uid&action=gamepage&native_api=1&pn=0', {}, 'get', 'json', 'Android'],
		'baidu_android_game_pos3' : [29, 2, '流行游戏风向标', u'http://m.baidu.com/appsrv?psize=3&usertype=1&is_support_webp=true&ver=16786881&from=1011080v&cen=cuid_cut_cua_uid&action=gamepage&native_api=1&pn=0', {}, 'get', 'json', 'Android'],
		'baidu_android_game_pos4' : [29, 2, '精品手游天天荐', u'http://m.baidu.com/appsrv?psize=3&usertype=1&is_support_webp=true&ver=16786881&from=1011080v&cen=cuid_cut_cua_uid&action=gamepage&native_api=1&pn=0', {}, 'get', 'json', 'Android'],
		'baidu_android_game_pos5' : [29, 1, '今日特选好游戏', u'http://m.baidu.com/appsrv?psize=3&usertype=1&is_support_webp=true&ver=16786881&from=1011080v&cen=cuid_cut_cua_uid&action=gamepage&native_api=1&pn=0', {}, 'get', 'json', 'Android'],
		'baidu_android_game_pos6' : [29, 2, '人气网游火力全开', u'http://m.baidu.com/appsrv?psize=3&usertype=1&is_support_webp=true&ver=16786881&from=1011080v&cen=cuid_cut_cua_uid&action=gamepage&native_api=1&pn=1', {}, 'get', 'json', 'Android'],
		'baidu_android_game_pos7' : [29, 2, '休闲时刻来一发', u'http://m.baidu.com/appsrv?psize=3&usertype=1&is_support_webp=true&ver=16786881&from=1011080v&cen=cuid_cut_cua_uid&action=gamepage&native_api=1&pn=2', {}, 'get', 'json', 'Android'],
		'baidu_android_game_pos8' : [29, 1, '火热新游', u'http://m.baidu.com/appsrv?psize=3&usertype=1&is_support_webp=true&ver=16786881&from=1011080v&cen=cuid_cut_cua_uid&action=gamepage&native_api=1&pn=2', {}, 'get', 'json', 'Android'],
		'baidu_android_game_pos9' : [29, 2, '速度与激情', u'http://m.baidu.com/appsrv?psize=3&usertype=1&is_support_webp=true&ver=16786881&from=1011080v&cen=cuid_cut_cua_uid&action=gamepage&native_api=1&pn=3', {}, 'get', 'json', 'Android'],
		'baidu_android_game_pos10' : [29, 2, '棋牌桌游欢乐斗', u'http://m.baidu.com/appsrv?psize=3&usertype=1&is_support_webp=true&ver=16786881&from=1011080v&cen=cuid_cut_cua_uid&action=gamepage&native_api=1&pn=4', {}, 'get', 'json', 'Android'],
		'baidu_android_game_pos11' : [29, 1, '火热新品', u'http://m.baidu.com/appsrv?psize=3&usertype=0&ver=16786356&from=1011454q&network=WF&gms=true&action=newgame&apn=&&native_api=1&pn=0&f=newgameentrance%40url', {}, 'get', 'json', 'Android'],
		'baidu_android_game_pos12' : [29, 2, '火热新品', u'http://m.baidu.com/appsrv?psize=3&usertype=0&ver=16786356&from=1011454q&network=WF&gms=true&action=newgame&apn=&&native_api=1&pn=0&f=newgameentrance%40url', {}, 'get', 'json', 'Android'],
		'baidu_android_game_pos13' : [29, 1, '今日必玩单机', u'http://m.baidu.com/appsrv?psize=3&usertype=1&is_support_webp=true&ver=16786881&from=1011080v&cen=cuid_cut_cua_uid&action=gamepage&native_api=1&pn=0', {}, 'get', 'json', 'Android'],		
		
		'aisi_ios_zhushou_pos1' : [36, 1, '大屏轮播图',  u'http://ios3.app.i4.cn/getAppList.xhtml?osversion=9.0.2&pageno=1', {}, 'get', 'xml', 'IOS'],

		'xy_ios_zhushou_pos1'   : [26, 1, '热门推荐大屏轮播图', u'http://interface.xyzs.com/v2/ios/c01/homepage?p=1&certId=0&ipatype=2', {}, 'get', 'json', 'IOS'],
		'xy_ios_zhushou_pos2'   : [26, 2, '首发网游推荐大图', u'http://interface.xyzs.com/v2/ios/c01/webgame/alreadytested?p=1&page=1&size=20&certId=10006&ipatype=4', {}, 'get', 'json', 'IOS'],
		'xy_ios_zhushou_pos3'   : [26, 1, '已开测网游推荐大图', u'http://interface.xyzs.com/v2/ios/c01/webgame/sf?page=1&p=1&size=20&ipatype=4', {}, 'get', 'json', 'IOS'],
		'xy_ios_zhushou_pos4'   : [26, 1, '即将开测网游推荐大图', u'http://interface.xyzs.com/v2/ios/c01/webgame/tobetested?p=1&page=1&size=20&ipatype=4', {}, 'get', 'json', 'IOS'],
		'xy_ios_zhushou_pos5'   : [26, 1, '精选游戏推荐大图', u'http://interface.xyzs.com/v2/ios/c01/game/chosen?p=1&ps=20&ipatype=4', {}, 'get', 'json', 'IOS'],
		'xy_ios_zhushou_pos6'   : [26, 1, '新锐游戏推荐大图', u'http://interface.xyzs.com/v2/ios/c01/game/latest?p=1&ps=20&ipatype=4', {}, 'get', 'json', 'IOS'],
		
		'itools_ios_zhushou_pos1' : [26, 1, '大屏轮播图', u'http://n1.app.itools.cn/?r=iphonexb/iosIndex/index', {}, 'get', 'json', 'IOS'],
		'itools_ios_zhushou_pos2' : [26, 3, '网游精选', u'http://n1.app.itools.cn/?r=iphonexb/iosIndex/index', {}, 'get', 'json', 'IOS'],
		'itools_ios_zhushou_pos3' : [26, 3, '优秀单机', u'http://n1.app.itools.cn/?r=iphonexb/iosIndex/index', {}, 'get', 'json', 'IOS'],
		
		'kuaiyong_ios_zhushou_pos1' : [19, 1, '大屏轮播图', u'http://iphonetwo.kuaiyong.com/i/q.php?d=D0YsJ%2FfM6b%2Fko3jOVi2ReTqC5wrNyzPSqExm35yO3vM3XQVwqK8%2FPdo14S%2FBaZ7LepUjKyMgsjl02qFg7yY41OD0sHealFRYsdg0PUlQoi6XJtTjzW92DjejYLfS3kTRek2vZhjzTL1ILblantpQ7lA9oiFO8c0gWn0pT7idqv60U8d9l757e8rvYNFbYlZBHND53keMiLBpGHLsAPUTZxG%2FuefyO74I', {}, 'get', 'json', 'IOS']
		}

json_struct_map = {
		'xiaomi_android_game_pos1' : {'json_tree' : ['if (0,1,6) template[', 'module['],
									 'json_rst'  : {'img_url': ['modPic'], 'game_name' : ['modName'], 'pkg_name':[], 'game_developer' : []}
									},
		'xiaomi_android_game_pos2' : {'json_tree' : ['objList[', 'obj[',],
									 'json_rst'  : {'img_url': ['icon'], 'game_name' : ['displayName'], 'pkg_name':['packageName'], 'game_developer' : ['publisherName']}
									},
		'xiaomi_android_game_pos3' : {'json_tree' : ['gameList['],
									 'json_rst'  : {'img_url': ['icon'], 'game_name' : ['displayName'], 'pkg_name':['packageName'], 'game_developer' : ['publisherName']}
									},
		'xiaomi_android_game_pos4' : {'json_tree' : ['gameList['],
									 'json_rst'  : {'img_url': ['icon'], 'game_name' : ['displayName'], 'pkg_name':['packageName'], 'game_developer' : ['publisherName']}
									},
   		'dangle_android_game_pos1' : {'json_tree' : ['list['],
  									 'json_rst'  : {'img_url': ['iconUrl'], 'game_name' : ['title'], 'pkg_name':[], 'game_developer' : []}
  									},
		'dangle_android_game_pos2' : {'json_tree' : ['if {"backgroundImage":"*"} ['],
									 'json_rst'  : {'img_url': ['backgroundImage'], 'game_name' : ['title'], 'pkg_name':[], 'game_developer' : []}
									},
   		'dangle_android_game_pos3' : {'json_tree' : ['list['],
  									 'json_rst'  : {'img_url': ['iconUrl'], 'game_name' : [], 'pkg_name':[], 'game_developer' : []}
  									},
		'sogou_android_zhushou_pos1'  : {'json_tree' : ['list['],
 									 'json_rst'  : {'img_url': ['iurl'], 'game_name' : ['tips'], 'pkg_name':[], 'game_developer' : []}
 									},
		'sogou_android_zhushou_pos2'  : {'json_tree' : ['list['],
 									 'json_rst'  : {'img_url': ['iurl'], 'game_name' : ['tips'], 'pkg_name':[], 'game_developer' : []}
 									},
		'sogou_android_zhushou_pos3' : {'json_tree' : ['banner['],
									 'json_rst'  : {'img_url': ['icon'], 'game_name' : ['name'], 'pkg_name':['packagename'], 'game_developer' : ['author']}
									},
   
		'meizu_android_game_pos1' : {'json_tree' : ['value{', 'if {"type":"banner"} blocks[', 'data['],
									 'json_rst'  : {'img_url': ['img_url'], 'game_name' : ['name'], 'pkg_name':['package_name'], 'game_developer' : []}
									},
		'meizu_android_game_pos2' : {'json_tree' : ['value{', 'if {"type":"advertise"} blocks[', 'data['],
							 'json_rst'  : {'img_url': ['img_url'], 'game_name' : ['name'], 'pkg_name':[], 'game_developer' : []}
							},
		'meizu_android_game_pos3' : {'json_tree' : ['value{', 'if {"type":"game_recommend"} blocks[', 'data[' ],
					 'json_rst'  : {'img_url': ['icon'], 'game_name' : ['name'], 'pkg_name':['package_name'], 'game_developer' : ['publisher']}
					},
		'meizu_android_game_pos4' : {'json_tree' : ['value{', 'if {"name":"热门推荐"} blocks[', 'data['],
					 'json_rst'  : {'img_url': ['icon'], 'game_name' : ['name'], 'pkg_name':['package_name'], 'game_developer' : ['publisher']}
					},
		'meizu_android_game_pos5' : {'json_tree' : ['value{', 'if {"name":"人气首发"} blocks[', 'data['],
					 'json_rst'  : {'img_url': ['icon'], 'game_name' : ['name'], 'pkg_name':['package_name'], 'game_developer' : ['publisher']}
					},
		'youku_android_game_pos1' : {'json_tree' : ['scollers['],
					 'json_rst'  : {'img_url': ['scoller'], 'game_name' : ['appname'], 'pkg_name':['package'], 'game_developer' : []}
					},
		'youku_android_game_pos2' : {'json_tree' : ['editor_recs[', 'apps['],
					 'json_rst'  : {'img_url': ['detail', 'scoller'], 'game_name' : ['detail', 'appname'], 'pkg_name':['detail', 'package'], 'game_developer' : []}
					},
		'youku_android_game_pos3' :  {'json_tree' : ['if {"name":"热门网游"} boxes[', 'games['],
					 'json_rst'  : {'img_url': ['scoller'], 'game_name' : ['appname'], 'pkg_name':['package'], 'game_developer' : []}
					}, 
		'youku_android_game_pos4' : {'json_tree' : ['if {"card_type":2} boxes[', 'games['],
					 'json_rst'  : {'img_url': ['scoller'], 'game_name' : ['appname'], 'pkg_name':['package'], 'game_developer' : []}
					}, 
		'youku_android_game_pos5' :  {'json_tree' : ['if {"name":"精品单机"} boxes[', 'games['],
					 'json_rst'  : {'img_url': ['scoller'], 'game_name' : ['appname'], 'pkg_name':['package'], 'game_developer' : []}
					}, 
		'youku_android_game_pos6' :  {'json_tree' : ['if {"name":"新品专区"} boxes[', 'games['],
					 'json_rst'  : {'img_url': ['scoller'], 'game_name' : ['appname'], 'pkg_name':['package'], 'game_developer' : []}
					},
		'youku_android_game_pos7' :  {'json_tree' : ['if {"name":"经典端游改编"} boxes[', 'games['],
					 'json_rst'  : {'img_url': ['scoller'], 'game_name' : ['appname'], 'pkg_name':['package'], 'game_developer' : []}
					}, 
		'youku_android_game_pos8' :  {'json_tree' : ['if {"name":"经典影视改编网游"} boxes[', 'games['],
					 'json_rst'  : {'img_url': ['scoller'], 'game_name' : ['appname'], 'pkg_name':['package'], 'game_developer' : []}
					}, 
		'youku_android_game_pos9' :  {'json_tree' : ['if {"name":"经典动漫改编网游"} boxes[', 'games['],
					 'json_rst'  : {'img_url': ['scoller'], 'game_name' : ['appname'], 'pkg_name':['package'], 'game_developer' : []}
					}, 
		'youku_android_game_pos10' : {'json_tree' : ['scollers['],
					 'json_rst'  : {'img_url': ['scoller'], 'game_name' : ['appname'], 'pkg_name':['package'], 'game_developer' : []}
					},
		'baidu_android_game_pos1' : {'json_tree' : ['result{', 'if {"datatype":58} data{', 'itemdata['],
									 'json_rst'  : {'img_url': ['banner'], 'game_name' : ['appinfo', 'sname'], 'pkg_name':['appinfo','package'], 'game_developer' : []}
									},
		'baidu_android_game_pos2' : {'json_tree' : ['result{', 'if {"datatype":61} data{', 'itemdata{', 'special{'],
									 'json_rst'  : {'img_url': ['special_icon'], 'game_name' : ['sname'], 'pkg_name':['package'], 'game_developer' : []}
									},
		'baidu_android_game_pos3' : {'json_tree' : ['result{', 'if {"datatype":61} data{', 'itemdata{', 'app_data['],
									 'json_rst'  : {'img_url': ['icon'], 'game_name' : ['sname'], 'pkg_name':['package'], 'game_developer' : []}
									},
		'baidu_android_game_pos4' : {'json_tree' : ['result{', 'if {"datatype":1} data['],
							 		 'json_rst'  : {'img_url': ['itemdata','icon'], 'game_name' : ['itemdata','sname'], 'pkg_name':['itemdata','package'], 'game_developer' : []}
									},
  		'baidu_android_game_pos5' : {'json_tree' : ['result{', 'if {"datatype":59} data{', 'itemdata{','apps['],
  							 		 'json_rst'  : {'img_url': ['icon'], 'game_name' : ['sname'], 'pkg_name':['package'], 'game_developer' : []}
 									},
		'baidu_android_game_pos6' : {'json_tree' : ['result{', 'if {"datatype":1} data['],
							 		 'json_rst'  : {'img_url': ['itemdata','icon'], 'game_name' : ['itemdata','sname'], 'pkg_name':['itemdata','package'], 'game_developer' : []}
									},
  	    'baidu_android_game_pos7' : {'json_tree' : ['result{', 'if {"datatype":1} data['],
 			 				 		 'json_rst'  : {'img_url': ['itemdata','icon'], 'game_name' : ['itemdata','sname'], 'pkg_name':['itemdata','package'], 'game_developer' : []}
  				 					},
		'baidu_android_game_pos8' : {'json_tree' : ['result{', 'if {"datatype":57} data{', 'itemdata{', 'appinfo{'],
				 		 			'json_rst'  : {'img_url': ['icon'], 'game_name' : ['sname'], 'pkg_name':['package'], 'game_developer' : []}
								 	},
   		'baidu_android_game_pos9' : {'json_tree' : ['result{', 'if {"datatype":1} data['],
  			 				 		 'json_rst'  : {'img_url': ['itemdata','icon'], 'game_name' : ['itemdata','sname'], 'pkg_name':['itemdata','package'], 'game_developer' : []}
   				 					},
   		'baidu_android_game_pos10' : {'json_tree' : ['result{', 'if {"datatype":1} data['],
  			 				 		 'json_rst'  : {'img_url': ['itemdata','icon'], 'game_name' : ['itemdata','sname'], 'pkg_name':['itemdata','package'], 'game_developer' : []}
  			 				 		},
		'baidu_android_game_pos11' : {'json_tree' : ['result{', 'if {"datatype":320} data{', 'itemdata{', 'special{'],
									 'json_rst'  : {'img_url': ['icon'], 'game_name' : ['sname'], 'pkg_name':['package'], 'game_developer' : []}
									},
		'baidu_android_game_pos12' : {'json_tree' : ['result{', 'if {"datatype":320} data{', 'itemdata{', 'app_data['],
									 'json_rst'  : {'img_url': ['icon'], 'game_name' : ['sname'], 'pkg_name':['package'], 'game_developer' : []}
									},
		'baidu_android_game_pos13' : {'json_tree' : ['result{', 'if {"datatype":304} data{', 'if {"title":"单机"} itemdata{', 'jump{', 'bundle{', 'header{', 'itemdata{', 'apps['],
									 'json_rst'  : {'img_url': ['imgurl'], 'game_name' : ['sname'], 'pkg_name':['package'], 'game_developer' : []}
									},
		'aisi_ios_zhushou_pos1' : {'json_tree' : ['i4{', 'adlist{', 'adinfo['],
 									 'json_rst'  : {'img_url': ['image'], 'game_name' : ['name'], 'pkg_name':[], 'game_developer' : []}
 								},
    				
		'xy_ios_zhushou_pos1'   : {'json_tree' : ['data{', 'banner['],
 									 'json_rst'  : {'img_url': ['img'], 'game_name' : ['title'], 'pkg_name':[], 'game_developer' : []}
 								},
		'xy_ios_zhushou_pos2'   : {'json_tree' : ['data{', 'ad{'],
 									 'json_rst'  : {'img_url': ['adimg'], 'game_name' : ['adname'], 'pkg_name':['bundleid'], 'game_developer' : []}
 								},
		'xy_ios_zhushou_pos3'   : {'json_tree' : ['data{', 'ad{'],
 									 'json_rst'  : {'img_url': ['adimg'], 'game_name' : ['adname'], 'pkg_name':['bundleid'], 'game_developer' : []}
 								},
		'xy_ios_zhushou_pos4'   : {'json_tree' : ['data{', 'ad{'],
 									 'json_rst'  : {'img_url': ['adimg'], 'game_name' : ['adname'], 'pkg_name':['bundleid'], 'game_developer' : []}
 								},
		'xy_ios_zhushou_pos5'   :{'json_tree' : ['data{', 'banner['],
 									 'json_rst'  : {'img_url': ['img'], 'game_name' : ['title'], 'pkg_name':[], 'game_developer' : []}
 								},
		'xy_ios_zhushou_pos6'   :{'json_tree' : ['data{', 'recommend{'],
 									 'json_rst'  : {'img_url': ['img'], 'game_name' : ['title'], 'pkg_name':['bundleid'], 'game_developer' : []}
								},
		'itools_ios_zhushou_pos1' :{'json_tree' : ['data{', 'if {"type":"app"} banner['],
 									 'json_rst'  : {'img_url': ['pic'], 'game_name' : ['appInfo', 'name'], 'pkg_name':['appInfo', 'bid'], 'game_developer' : []}
 								},
		'itools_ios_zhushou_pos2' :{'json_tree' : ['data{', 'if {"name":"网游精选"} content{', 'data['],
 									 'json_rst'  : {'img_url': ['icon'], 'game_name' : ['name'], 'pkg_name':['bid'], 'game_developer' : []}
 								},
		'itools_ios_zhushou_pos3' :{'json_tree' : ['data{', 'if {"name":"优秀单机"} content{', 'data['],
 									 'json_rst'  : {'img_url': ['icon'], 'game_name' : ['name'], 'pkg_name':['bid'], 'game_developer' : []}
 								},
		'kuaiyong_ios_zhushou_pos1' :{'json_tree' : ['data{', 'banner['],
									 'json_rst'  : {'img_url': ['banner_url'], 'game_name' : ['intro'], 'pkg_name':[], 'game_developer' : []}
								},
}

def parse_json_rst(json_data_list, json_rst_struct):
	#print json_data_list
	rst_list = []

	for item in json_data_list :
		rst_dict = {}
		for key in json_rst_struct :
			item_key_list = json_rst_struct[key]
			
			if item_key_list :
				item_value = item
				for item_key in item_key_list :
					if item_value == u'' :
						break
					if item_key.endswith('[') :
						item_key = item_key[0:(len(item_key)-1)]
						tmp_list = item_value.get(item_key, u'')
						item_value = tmp_list[0] if tmp_list else u''
					else :
						item_value = item_value.get(item_key, u'')
				rst_dict[key] = item_value
		rst_list.append(rst_dict)
	return rst_list


#{x:wugao}, (wu:(1,2,3))
def parse_json_if_stat(json_list_data, if_stat) :
	stat_list = if_stat.split()
	condition = stat_list[1]
	rst_list_data = []
	if json_list_data is None or not json_list_data :
		return rst_list_data
	
	if condition.startswith('{') :#{key1:value1}对应key, value的条件过滤
		data_dict = eval(condition)
		for data in json_list_data :
			for key in data_dict :
				value = data_dict.get(key)
				if data.has_key(key) :
					if value == '*' or str(data.get(key)).decode('utf8') == str(value).decode('utf8'):
						rst_list_data.append(data)
	elif condition.startswith('(') : #[0, 1, 2]对应数组的索引
		data_list = list(eval(condition))
		for i in range(len(json_list_data)) :
			if i in data_list :
				rst_list_data.append(json_list_data[i])
	rst_type = stat_list[2]
	
	# { 表示返回数组第一个元素
	if rst_type.endswith('{') :
		if len(rst_list_data) > 0 :
			return rst_list_data[0]
	
	return rst_list_data


def parse_json_tree(json_org_data, json_tree_struct) :
	rst_list = []
	json_hist_data = []
	
	if json_org_data is None or not json_org_data:
		return rst_list
	
	if json_tree_struct is None or not json_tree_struct :
		return rst_list

	json_hist_data.append(json_org_data)
	
	cur_index = 0
	for json_tree_node in json_tree_struct :
		json_cur_data = json_hist_data[-1]

		if json_tree_node.startswith('if') :
			stat_list = json_tree_node.split()
			tmp_str = stat_list[2]
			node_key = tmp_str[0:(len(tmp_str)-1)]
			if node_key :
				json_cur_data = json_cur_data.get(node_key, u'')
			json_cur_data = parse_json_if_stat(json_cur_data, json_tree_node)
		else:
			node_key = json_tree_node[0:(len(json_tree_node)-1)]
			json_cur_data = json_cur_data.get(node_key, u'')
		
 		cur_index = cur_index + 1
		if json_cur_data is not None and json_cur_data:
			to_scan_tree_struct = json_tree_struct[cur_index : len(json_tree_struct)]
			if json_tree_node.endswith('[') and to_scan_tree_struct:
				for json_item in json_cur_data:
					rst_item = parse_json_tree(json_item, to_scan_tree_struct)
					if rst_item is not None and rst_item:
						rst_list.extend(rst_item)
				return rst_list
			json_hist_data.append(json_cur_data)
		else :
			return rst_list

	if type(json_hist_data[-1]) is dict :
		rst_list.append(json_hist_data[-1])
	elif type(json_hist_data[-1]) is list :
		rst_list = json_hist_data[-1]
		
	return rst_list

def parse_url_response(json_data, json_struct) :
	rst_list = []

	json_tree_struct = json_struct.get('json_tree')
	json_tree_data_list = parse_json_tree(json_data, json_tree_struct)
	
	if json_tree_data_list :
		json_rst_info = json_struct.get('json_rst')
		rst_list = parse_json_rst(json_tree_data_list, json_rst_info)
	return rst_list

def get_market_ad_info ():
	for pos_key in json_struct_map.keys() :
		pos_info = url_map.get(pos_key)
	
		get_data_url = pos_info[3]
		url_header = pos_info[4]
		url_method = pos_info[5]
		url_responseType = pos_info[6]
		json_data = get_data_from_api(get_data_url, headers=url_header, method=url_method, responseType=url_responseType)
		
		json_struct = json_struct_map.get(pos_key)
		#dict_list = parse_url_json(json_data, json_struct)
		dict_list = parse_url_response(json_data, json_struct)
#		print pos_key, pos_info[2]
		for mydict in dict_list :
 			game_id = insert_ad_game(mydict, pos_info)
			mydict['game_id'] = game_id
			insert_ad_record(mydict, pos_info)
# 			store_adv_info_data(mydict, pos_info)
# 			print mydict.get('img_url', u'')
# 			print str(mydict.get('game_name', u'')).decode('utf8')
# 			print mydict.get('pkg_name', u'')
# 			print str(mydict.get('game_developer', u'')).decode('utf8')
		now = datetime.datetime.now()
		mylogger.info("%s  channel %s  postion %s insert number of data %d" % (now.strftime('%Y-%m-%d %H:%M:%S'), pos_key, pos_info[2], len(dict_list)))
	return 

def get_data_from_api(url, timeout=10, headers={}, proxies={}, method='get', responseType='json'):
	if isinstance(url, unicode):
		url = url.encode('utf-8')
	try:
		if method == 'get':
			r = requests.get(url, timeout=timeout, headers=headers, proxies=proxies)
		elif method == 'post' :
			r = requests.post(url, timeout=timeout, headers=headers, proxies=proxies)
		if r.status_code == 200:
			if responseType == 'json':
				return r.json()
			elif responseType == 'xml':
				return xmltodict.parse(r.text)			
	except Exception,e:
		now = datetime.datetime.now()
		mylogger.error("%s get data from ### %s ### \n%s" % (now.strftime('%Y-%m-%d %H:%M:%S'), url, traceback.format_exc()))
	return None

def insert_ad_game(infoData, pos_info):
	platform  = pos_info[7]
	
	img_url = infoData.get('img_url')
	game_name = infoData.get('game_name')
	
	pkg_name = infoData.get('pkg_name')
	game_developer = infoData.get('game_developer')

	ins = db_conn.query(ADVGameDetail).filter(ADVGameDetail.game_name==game_name).filter(ADVGameDetail.img_url==img_url).first()
	
	if ins is None:
		item = ADVGameDetail(**{
						"img_url"			: img_url if img_url else '',
						"game_name"			: game_name if game_name else '',
						"game_developer"    : game_developer if game_developer else '',
						"pkg_name"			: pkg_name if pkg_name else '',
						"platform"			: platform if platform else 'Android',
						})
		db_conn.add(item)
		db_conn.commit()
		return item.id
	else:
		return ins.id
	
def insert_ad_record(infoData, pos_info) :
	infoData['channel_id'] = pos_info[0]
	infoData['position_type_id'] = pos_info[1]
	infoData['position_name'] = pos_info[2]
	
	channel_id = infoData.get('channel_id')
	position_type_id = infoData.get('position_type_id')
	position_name = infoData.get('position_name')
	game_id = infoData.get('game_id')
		
	dt = date.today()
	ins = db_conn.query(ADVRecord2).filter(ADVRecord2.update_date==dt).filter(ADVRecord2.channel_id==channel_id).filter(ADVRecord2.position_type_id==position_type_id).filter(ADVRecord2.adv_game_detail_id==game_id).filter(ADVRecord2.position_name==position_name).first()
	
	if ins is None:
		item = ADVRecord2(**{
						"channel_id"		: channel_id,
						"position_type_id"	: position_type_id,
						"position_name"		: position_name,
						"adv_game_detail_id": game_id,
						"update_date"		: dt,
						})
		db_conn.merge(item)
	db_conn.commit()
	
def store_adv_info_data(infoData, pos_info) :
	infoData['channel_id'] = pos_info[0]
	infoData['position_type_id'] = pos_info[1]
	infoData['position_name'] = pos_info[2]
	
	channel_id = infoData.get('channel_id')
	position_type_id = infoData.get('position_type_id')
	position_name = infoData.get('position_name')
	img_url = infoData.get('img_url')
	game_name = infoData.get('game_name')
	
	pkg_name = infoData.get('pkg_name')
	game_developer = infoData.get('game_developer')
	
	img_parent_path = "/root/yanpengchen/data_eye/spider/imgs"
	if not os.path.exists(img_parent_path) :
		os.mkdir(img_parent_path)



	img_path = img_parent_path + "/" + str(uuid.uuid1())
	if img_url is not None :
		img_path = download_pic_v2(img_url, img_path)
		
	dt = date.today()
	ins = db_conn.query(ADVRecord).filter(ADVRecord.update_date==dt).filter(ADVRecord.channel_id==channel_id).filter(ADVRecord.position_type_id==position_type_id).filter(ADVRecord.img_path==img_path).filter(ADVRecord.position_name==position_name).first()
	if ins is None:
		item = ADVRecord(**{
						"channel_id"		: channel_id,
						"position_type_id"	: position_type_id,
						"position_name"		: position_name,
						"img_path"			: img_url if img_url else '',
						"img_local_path"	: img_path if img_path else '',
						"game_name"			: game_name if game_name else '',
						"pkg_name"		: pkg_name if pkg_name else '',
						"update_date"		: dt,
						"game_developer"    : game_developer if game_developer else ''
						})
		db_conn.merge(item)
	db_conn.commit()
	
def main():
	get_market_ad_info()
	
	pass

if __name__ == "__main__":
	main()
#	get_appicsh_raw_data()

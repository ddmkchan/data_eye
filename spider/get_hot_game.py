#!/usr/bin/env python
#encoding=utf-8

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

mylogger = get_logger('hot_game')

s = requests.session()
db_conn = new_session()

import random
proxies = [{rc.type: u"%s:%s" % (rc.ip, rc.port)} for rc in db_conn.query(ProxyList)]

source_map = {
			"baidu"	: 0,
			"xiaomi_active": 1,
			"360_webgame"	: 2,
			"9game"	: 3,
			"9game_hot_wanted"	: 4,
			"360_app_single"	: 5,
			"360_app_webgame"	: 6,
			"360_app_new_game"	: 7,
			"m5_qq_single"	: 8,#应用宝PC
			"m5_qq_webgame"	: 9,#应用宝PC
			"m5_qq_new_game"	: 10,#应用宝PC
			"m_baidu_single"	: 11,
			"m_baidu_webgame"	: 12,
			"m_baidu_new_game"	: 13,
			"dangle_new_game"	: 14,
			"xiaomi_new_game"	: 15,
			"vivo_single"	: 16,
			"vivo_webgame"	: 17,
			"vivo_new_game"	: 18,
			"gionee_active"	: 19,
			"gionee_hot"	: 20,
			"coolpad_hot"	: 21,
			"coolpad_webgame"	: 22,
			"coolpad_new_game"	: 23,
			"open_play_download"	: 24,#爱游戏榜单
			"open_play_free"	: 25,#爱游戏榜单
			"open_play_webgame"	: 26,#爱游戏榜单
			"wandoujia_single"	: 27,
			"wandoujia_webgame"	: 28,
			"iqiyi_download"	: 29,
			"iqiyi_hot"	: 30,
			"youku_single"	: 31,
			"youku_webgame"	: 32,
			"sogou_single"	: 33,
			"sogou_webgame"	: 34,
			"i4_hot"	: 35,
			"pp_hot"	: 36,
			"kuaiyong_hot"	: 37,
			"itools_hot"	: 38,
			"xyzs_hot"	: 39,
			"91play_hot"	: 40,
			"360_gamebox_single"	: 41,
			"360_gamebox_webgame"	: 42,
			"m5_qq_download"	: 43,
			"m_baidu_top"	: 44,
			"open_play_rise"	: 45,
			"18183_top"	: 46,
			"18183_hot"	: 47,
			"360_app_expect"	: 48,
			"xiaomi_downloads": 49,
			"xiaomi_new_webganme": 50,
			"sogou_download"	: 51,
			"360_child"		: "52", 
			"360_rpg"		: "53", 
			"360_act"		: "54", 
			"360_puz"		: "55", #休闲益智
			"360_sport"		: "56", 
			"360_stg"		: "57", #飞行射击
			"360_strategy"	: "58", 
			"360_chess"		: "59", 
			"xiaomi_app_download"		: "60", 
			"xiaomi_app_hot"		: "61", #畅销榜 
			"tbzs_single"		: "62", #淘宝助手单机榜
			"tbzs_webgame"		: "63", #淘宝助手网游榜
			"tbzs_rise"		: "64", #淘宝助手飙升榜
			"wogame_hot"		: "65", #沃游戏最热榜
			"wogame_new"		: "66", #沃游戏最新榜
			"dangle_webgame"	: 67,
			"lenovo_gc_mostuser"	: 68,#联想游戏中心
			"lenovo_gc_mosttime"	: 69,
			"lenovo_gc_newest"	: 70,
			"lenovo_shop_racing_car"	: 71,
			"lenovo_shop_android_free" : 72,
			"lenovo_shop_parkour" : 73,
			"lenovo_shop_hard_game" : 74,
			"meizu_webgame" : 75,
			"meizu_single" : 76,
			"wostore_new_game" : 77,
			"wostore_hot" : 78,
			"mmstore_hot" : 79,
			"vivo_store_single" : 80,
			"vivo_store_webgame" : 81,
			"myaora_download" : 82,#易用汇下载榜
			"myaora_rise" : 83,#易用汇
			"huawei_single_weekly" : 84,
			"huawei_webgame_weekly" : 85,
			"huawei_newgame" : 86,
			"huawei_hot" : 87,
			"app12345" : 88,
				}

def get_baidu_hot_games():
	url = "http://shouji.baidu.com/game"
	r = s.get(url)
	rank = 0
	if r.status_code == 200:
		soup = BeautifulSoup(r.text)
		hot = soup.find("div", class_="sec-hot tophot")
		if hot is not None:
			for k in hot.find_all("li")[:]:
				rank += 1
				popular 	= u""
				game_type 	= u""
				status 		= u""
				url 		= u""
				source 		= source_map.get('baidu')
				url_a = k.find("a",class_="app-box")
				if url_a is not None:
					url = "http://shouji.baidu.com%s" % url_a.get('href')
				detail = k.find("div",class_="app-detail")
				if detail is not None:
					game_name = detail.find("p").text
					img = detail.find("div", class_="icon").find("img").get("src")
					down_size = detail.find("p", class_="down-size")	
					downloads = down_size.find("span", class_="down").text
					size = down_size.find("span", class_="size").text
					store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))

def download_pic(url, name):
	try:
		if not os.path.isfile("/home/cyp/data_eye/spider/ttt/%s" % (name)):
			print '**'
			urllib.urlretrieve(url, "/home/cyp/data_eye/spider/ttt/%s" % name)
	except Exception,e:
		print traceback.format_exc()

def download_pic2(args):
	try:
		url, name = args
		if not os.path.isfile("/home/cyp/data_eye/spider/pics/%s" % (name)):
			mylogger.info("downloading pic ... %s" % name)
			urllib.urlretrieve(url, "/home/cyp/data_eye/spider/pics/%s" % name)
	except Exception,e:
		mylogger.error(traceback.format_exc())

def get_appannie_icons():
	import multiprocessing
	from multiprocessing.dummy import Pool as ThreadPool
	try:
		pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
		urls = [(ret.src, ret.name+"_"+str(ret.source)) for ret in db_conn.query(HotGames).filter(HotGames.create_date=="2015-09-02").filter(HotGames.source!=4)]	
		pool.map_async(download_pic2, urls)
		pool.close()
		pool.join()
	except Exception,e:
		print traceback.format_exc()
	

def get_icons(f):
	import multiprocessing
	from multiprocessing.dummy import Pool as ThreadPool
	try:
		pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
		urls = []
		for ret in f():
			app_name, src, download_count, size, source = ret
			url = src 
			name = app_name.encode("utf-8")+"_"+str(source)
			urls.append((url, name))
			#pool.apply_async(download_pic, (url, name))
		pool.map_async(download_pic2, urls)
		pool.close()
		pool.join()
	except Exception,e:
		mylogger.error(traceback.format_exc())

def get_xiaomi_game_rank(page, rank_id):
	url = "http://game.xiaomi.com/index.php?c=app&a=ajaxPage&type=rank"
	payload = {
				"page"			:page,
				"category_id"	:"",
				"total_page"	:60,
				"rank_id"		:rank_id,
				"type"			:"rank"
				}
	r = s.post(url, data=payload)
	if r.status_code == 200:
		return r.json()
	return None


def get_xiaomi_web_rank(gtype, rank_id):
	rank = 0
	for page in xrange(1):
		detail = get_xiaomi_game_rank(page, rank_id)
		if detail is not None:
			for d in detail:
				rank += 1
				popular 	= u""
				game_type 	= u""
				status 		= u""
				url 		= u"http://game.xiaomi.com/app-appdetail--app_id__%s.html" % d.get("ext_id")
				game_name = d.get("game_name")
				img = d.get("icon")
				downloads = d.get("download_count")
				size = d.get("apk_size")
				source = source_map.get(gtype)
				yield rank, game_name, img, downloads, size, source, popular, game_type, status, url

def store_xiaomi_web_rank():
	type_2_source = {
						"xiaomi_active": 12,
						"xiaomi_new_webganme": 13,
						"xiaomi_downloads": 2,
						"xiaomi_new_game": 3,
					}
	for gtype, rank_id in type_2_source.iteritems():
		for data in get_xiaomi_web_rank(gtype, rank_id):
			store_data(data)


def get_360zhushou_web_rank():
	_dict = {
				"360_webgame"	: "100451", 
				"360_child"		: "102238", 
				"360_rpg"		: "101587", 
				"360_act"		: "20", 
				"360_puz"		: "19", #休闲益智
				"360_sport"		: "51", 
				"360_stg"		: "52", #飞行射击
				"360_strategy"	: "53", 
				"360_chess"		: "54", 
			}
	for gtype, id in _dict.iteritems():
		try:
			r = s.get('http://zhushou.360.cn/list/index/cid/%s/order/download/?page=1' % id)
			if r.status_code == 200:
				soup = BeautifulSoup(r.text)
				icon_list = soup.find("ul", class_="iconList")
				if icon_list is not None:
					rank = 0
					for i in icon_list.find_all("li"):
						rank += 1
						game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
						if i.find('h3') is not None and i.find('h3').find('a') is not None:
							item = i.find('h3').find('a')
							url 		= u"http://zhushou.360.cn/detail/index/soft_id/%s" % item.get('sid')
							game_name = item.text
							img = i.find("a", sid="%s" % item.get("sid")).find("img").get("_src")
							downloads = i.find("span").text
							size 		= u""
							source 		= source_map.get(gtype)
							#print rank, game_name, img, downloads, size, source, popular, game_type, status, url
							store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
		except Exception,e:
			mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	mylogger.info("get 360zhushou web done!")
			

def store_9game_web_app_rank():
	_dict = {'9game': "http://www.9game.cn/xyrb/", '9game_hot_wanted':"http://www.9game.cn/xyqdb/"}
	for gtype, url in _dict.iteritems():
		get_9game_web_app_rank(gtype, url)

def get_9game_web_app_rank(gtype, url):
	try:	
		p = proxies[random.randrange(len(proxies))]
		r = requests.get(url, timeout=10)
		if r.status_code == 200:
			soup = BeautifulSoup(r.text)
			t = soup.find("div", class_="box-text").find("table").find_all("tr")
			for i in t[1:]:
				game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
				td_list = i.find_all("td")
				rank = td_list[0].find("span").text
				game_name = td_list[1].find("a").get("title")
				url = u"http://www.9game.cn%s" % td_list[1].find("a").get("href")
				game_type = td_list[2].text.rstrip()
				status = td_list[3].text.strip()
				popular = td_list[4].text.strip()
				source = source_map.get(gtype)
				downloads = popular
				store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))


def get_appannie_hot_list():
	headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'}
	r = s.get("https://www.appannie.com/apps/ios/top/china/games/?device=iphone", headers=headers, timeout=10)
	if r.status_code == 200:
		soup = BeautifulSoup(r.text)
		t = soup.find("div", class_="region-main-inner").find("table").find_all("tr")
		for i in t[1:]:
			hot = i.find_all("td")[2]
			d = hot.find("div", class_="main-info").find("a")
			yield d.text, d.get("href")

def get_appannie_detail():
	for i in get_appannie_hot_list():
		app_name, url = i
		r = s.get("https://www.appannie.com/cn%s" % url, headers=headers)
		if r.status_code == 200:
			soup = BeautifulSoup(r.text)
			img_div = soup.find("div", class_="col-lg-3 col-md-3 col-sm-4 text-center-mobile app-logo")
			yield app_name, img_div.find("img").get("src"), u"", u"", 4


def get_360_app_rank(gtype):
	rank = 0
	type_2_source = {'single': '360_app_single',
						'webgame': '360_app_webgame',
						'expect': '360_app_expect',
						'new': '360_app_new_game'}
	_url = 'http://openboxcdn.mobilem.360.cn//app/rank?from=game&type=%s&page=1' % gtype
	try:
		r = requests.get(_url, timeout=10)
		if r.status_code == 200:
			j = r.json()
			if j['errno'] == u'0':
				for app in j['data']:
					rank += 1
					game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
					game_name = app.get('name', u'')
					img = app.get('logo_url', u'')
					downloads = app.get('download_times', u'')
					size = app.get('size', u'')
					game_type = app.get('category_name', u'')
					url = app.get('apkid', u'') + "\t" + app.get('id', u'')
					source = source_map.get(type_2_source.get(gtype))
					yield rank, game_name, img, downloads, size, source, popular, game_type, status, url
	except Exception,e:
		mylogger.error("%s====>\t%s" % (_url, traceback.format_exc()))

def store_360_app_rank():
	for gtype in ['single', 'webgame', 'new', 'expect']:
		mylogger.info("360 %s rank start... " % gtype)
		for data in get_360_app_rank(gtype):
			store_data(data)


def get_m5qq_app_rank(gtype):
	#应用宝 PC
	rank = 0
	type_2_source = {
						'16': 'm5_qq_download',
						'19': 'm5_qq_single',
						'20': 'm5_qq_webgame',
						'18': 'm5_qq_new_game',
					}
	_url = 'http://m5.qq.com/app/applist.htm?listType=%s&pageSize=50&contextData=' % gtype
	try:
		r = requests.get(_url, timeout=10)
		if r.status_code == 200:
			j = r.json()
			if 'obj' in j and 'appList' in j['obj']:
				for app in j['obj']['appList']:
					rank += 1
					game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
					game_name = app.get('appName', u'')
					img = app.get('iconUrl', u'')
					downloads = app.get('appDownCount', u'')
					size = app.get('fileSize', u'')
					game_type = app.get('categoryName', u'')
					#url = u"%s\t%s" % (app.get('pkgName', u''),  app.get('appId', u''))
					url = "http://m5.qq.com/app/getappdetail.htm?pkgName=%s&sceneId=0" % app.get('pkgName', u'') if app.get('pkgName', u'') else u''
					source = source_map.get(type_2_source.get(gtype))
					yield rank, game_name, img, downloads, size, source, popular, game_type, status, url
	except Exception,e:
		mylogger.error("%s====>\t%s" % (_url, traceback.format_exc()))

def store_m5qq_app_rank():
	for gtype in ['16', '18', '19', '20']:
		mylogger.info("get_m5qq_app_rank %s rank start... " % gtype)
		for data in get_m5qq_app_rank(gtype):
			store_data(data)


BAIDU_SINGLE_RANK = 0
BAIDU_WEBGAME_RANK = 0 
BAIDU_NEW_GAME_RANK = 0 
BAIDU_TOP = 0 


def get_m_baidu_rank(gtype, _url):
	global BAIDU_SINGLE_RANK
	global BAIDU_WEBGAME_RANK
	global BAIDU_NEW_GAME_RANK
	global BAIDU_TOP

	try:
		p = proxies[random.randrange(len(proxies))]
		r = requests.get(_url, timeout=10, proxies=p)
		if r.status_code == 200:
			j = r.json()
			if 'result' in j and 'data' in j['result']:
				for item in j['result']['data']:
					if 'itemdata' in item:
						if gtype == 'm_baidu_single':
							BAIDU_SINGLE_RANK += 1
							rank = BAIDU_SINGLE_RANK
						elif gtype == 'm_baidu_webgame':
							BAIDU_WEBGAME_RANK += 1
							rank = BAIDU_WEBGAME_RANK
						elif gtype == 'm_baidu_new_game':
							BAIDU_NEW_GAME_RANK += 1
							rank = BAIDU_NEW_GAME_RANK
						else:
							BAIDU_TOP += 1
							rank = BAIDU_TOP
						app = item.get('itemdata', {})
						game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
						game_name = app.get('sname', u'')
						img = app.get('icon', u'')
						downloads = app.get('display_download', u'')
						size = app.get('size', u'')
						game_type = app.get('catename', u'')
						pkg_name = app.get('package', u'')
						pkg_id = app.get('docid', u'')
						if pkg_name and pkg_id:
							url = u"http://m.baidu.com/appsrv?native_api=1&psize=3&pkname=%s&action=detail&docid=%s" % (pkg_name, pkg_id)
						else:
							url = u''
						source = source_map.get(gtype)
						#print rank, game_name, source
						yield rank, game_name, img, downloads, size, source, popular, game_type, status, url
	except Exception,e:
		mylogger.error("%s====>\t%s" % (_url, traceback.format_exc()))


def store_m_baidu_app_rank():
	prefix_single_url = "http://m.baidu.com/appsrv?uid=YPvuu_PqvfgkiHf30uS88liwHulTiSiQYiHPfgiOB8qLuHf3_PvoigaX2ig5uBiN3dqqC&native_api=1&psize=3&abi=armeabi-v7a&cll=_hv19g8O2NAVA&usertype=0&is_support_webp=true&ver=16786356&from=1011454q&board_id=board_102_736&operator=460015&network=WF&pkname=com.dragon.android.pandaspace&country=CN&cen=cuid_cut_cua_uid&gms=false&platform_version_id=19&firstdoc=&name=game&action=ranklist&pu=cua%40_a-qi4uq-igBNE6lI5me6NIy2I_UC-I4juDpieLqA%2Cosname%40baiduappsearch%2Cctv%401%2Ccfrom%401010680f%2Ccuid%40YPvuu_PqvfgkiHf30uS88liwHulTiSiQYiHPfgiOB86QuviJ0O2lfguGv8_Huv8uja20fqqqB%2Ccut%405fXCirktSh_Uh2IJgNvHtyN6moi5pQqAC&language=zh&apn=&native_api=1&f=gameranklist%40tab%401&bannert=26%4027%4028%4029%4030%4031%4032%4043" 
	single_url = [prefix_single_url + "&pn=%s"  %p for p in xrange(5)]
	prefix_new_games_url = 'http://m.baidu.com/appsrv?uid=YPvuu_PqvfgkiHf30uS88liwHulTiSiQYiHPfgiOB8qLuHf3_PvoigaX2ig5uBiN3dqqC&native_api=1&psize=3&abi=armeabi-v7a&cll=_hv19g8O2NAVA&usertype=0&is_support_webp=true&ver=16786356&from=1011454q&board_id=board_102_737&operator=460015&network=WF&pkname=com.dragon.android.pandaspace&country=CN&cen=cuid_cut_cua_uid&gms=false&platform_version_id=19&firstdoc=&name=game&action=ranklist&pu=cua%40_a-qi4uq-igBNE6lI5me6NIy2I_UC-I4juDpieLqA%2Cosname%40baiduappsearch%2Cctv%401%2Ccfrom%401010680f%2Ccuid%40YPvuu_PqvfgkiHf30uS88liwHulTiSiQYiHPfgiOB86QuviJ0O2lfguGv8_Huv8uja20fqqqB%2Ccut%405fXCirktSh_Uh2IJgNvHtyN6moi5pQqAC&language=zh&apn=&&native_api=1&f=gameranklist%40tab%403&bannert=26%4027%4028%4029%4030%4031%4032%4043'
	new_games_url = [prefix_new_games_url+ "&pn=%s" %p for p in xrange(5)]
	prefix_web_game_url = 'http://m.baidu.com/appsrv?uid=YPvuu_PqvfgkiHf30uS88liwHulTiSiQYiHPfgiOB8qLuHf3_PvoigaX2ig5uBiN3dqqC&native_api=1&psize=3&abi=armeabi-v7a&cll=_hv19g8O2NAVA&usertype=0&is_support_webp=true&ver=16786356&from=1011454q&board_id=board_102_735&operator=460015&network=WF&pkname=com.dragon.android.pandaspace&country=CN&cen=cuid_cut_cua_uid&gms=false&platform_version_id=19&firstdoc=&name=game&action=ranklist&pu=cua%40_a-qi4uq-igBNE6lI5me6NIy2I_UC-I4juDpieLqA%2Cosname%40baiduappsearch%2Cctv%401%2Ccfrom%401010680f%2Ccuid%40YPvuu_PqvfgkiHf30uS88liwHulTiSiQYiHPfgiOB86QuviJ0O2lfguGv8_Huv8uja20fqqqB%2Ccut%405fXCirktSh_Uh2IJgNvHtyN6moi5pQqAC&language=zh&apn=&&native_api=1&f=gameranklist%40tab%402&bannert=26%4027%4028%4029%4030%4031%4032%4043'
	web_game_url = [prefix_web_game_url+"&pn=%s" %p for p in xrange(5)]
	prefix_top_url = 'http://m.baidu.com/appsrv?uid=YPvuu_PqvfgkiHf30uS88liwHulTiSiQYiHPfgiOB8qLuHf3_PvoigaX2ig5uBiN3dqqC&native_api=1&psize=3&abi=armeabi-v7a&cll=_hv19g8O2NAVA&usertype=0&is_support_webp=true&ver=16786356&from=1011454q&board_id=board_102_139&operator=460015&network=WF&pkname=com.dragon.android.pandaspace&country=CN&cen=cuid_cut_cua_uid&gms=false&platform_version_id=19&firstdoc=&name=game&action=ranklist&pu=cua%40_a-qi4uq-igBNE6lI5me6NIy2I_UC-I4juDpieLqA%2Cosname%40baiduappsearch%2Cctv%401%2Ccfrom%401010680f%2Ccuid%40YPvuu_PqvfgkiHf30uS88liwHulTiSiQYiHPfgiOB86QuviJ0O2lfguGv8_Huv8uja20fqqqB%2Ccut%405fXCirktSh_Uh2IJgNvHtyN6moi5pQqAC&language=zh&apn=&&native_api=1&f=gameranklist%40tab%400&bannert=26%4027%4028%4029%4030%4031%4032%4043'
	top_game_url = [prefix_top_url+"&pn=%s" %p for p in xrange(5)]
	_dict = {'m_baidu_top': top_game_url, 'm_baidu_single': single_url, 'm_baidu_webgame': web_game_url, 'm_baidu_new_game': new_games_url}
	for gtype, urls in _dict.iteritems():
		for _url in urls:
			for data in get_m_baidu_rank(gtype, _url):
				store_data(data)
		
def get_dangle_app_rank():
	_dict = {"dangle_new_game": "http://api2014.digua.d.cn/newdiguaserver/game/rank?pn=1&type=16&ps=50",
			"dangle_webgame": "http://api2014.digua.d.cn/newdiguaserver/netgame/rank?pn=1&imsi=FFBBF2C3433E688CF21029AF18019E04251E9BD48DA80861850852CA82560C5714CCD4D3D1D31725&se=2D8118F6F152232B6B55EA964A24B0F8&im=882ADF58F29193B2E6F07F6A288D2593&wm=4D0ED9C025B669B25D18F6ECB92DB2A9F05D78CA67BED3B1&ps=20"}
	#_url = 'http://api2014.digua.d.cn/newdiguaserver/game/rank?pn=1&type=16&ps=50'
	headers_map = {
			"dangle_new_game": {'HEAD': {"stamp":1448610575430,"verifyCode":"78492ba9e8569f3b9d9173ac4e4b6cb9","it":2,"resolutionWidth":1080,"imei":"865931027730878","clientChannelId":"100327","versionCode":750,"mac":"34:80:b3:4d:69:87","vender":"Qualcomm","vp":"","version":"7.5","sign":"2ec90f723384b1ec","dd":480,"sswdp":"360","hasRoot":0,"glEsVersion":196608,"device":"MI_4LTE","ss":2,"local":"zh_CN","language":"2","sdk":19,"resolutionHeight":1920,"osName":"4.4.4","gpu":"Adreno (TM) 330"}}, 
			"dangle_webgame":{'HEAD': {"stamp":1450074512609,"verifyCode":"78492ba9e8569f3b9d9173ac4e4b6cb9","it":2,"resolutionWidth":1080,"imei":"865931027730878","clientChannelId":"100327","versionCode":750,"mac":"34:80:b3:4d:69:87","vender":"Qualcomm","vp":"","version":"7.5","sign":"f4fc625aca5d7a08","dd":480,"sswdp":"360","hasRoot":0,"glEsVersion":196608,"device":"MI_4LTE","ss":2,"local":"zh_CN","language":"2","sdk":19,"resolutionHeight":1920,"osName":"4.4.4","gpu":"Adreno (TM) 330"}}}
	for gtype, _url in _dict.iteritems():
		rank = 0
		try:
			headers = headers_map.get(gtype)
			r = requests.post(_url, timeout=10, headers=headers)
			if r.status_code == 200:
				j = r.json()
				if 'list' in j:
					for app in j['list']:
						rank += 1
						game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
						game_name = app.get('name', u'')
						img = app.get('iconUrl', u'')
						downloads = app.get('downs', u'')
						game_type = app.get('categoryName', u'')
						source = source_map.get(gtype)
						url = u"%s\t%s" % (app.get('resourceType', u''), app.get('id', u''))
						store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
		except Exception,e:
			mylogger.error("%s====>\t%s" % (_url, traceback.format_exc()))



def get_vivo_app_rank(gtype, _url):
	rank = 0
	try:
		r = requests.get(_url, timeout=10)
		if r.status_code == 200:
			j = r.json()
			if 'msg' in j:
				for app in j['msg']:
					rank += 1
					game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
					game_name = app.get('name', u'')
					img = app.get('icon', u'')
					downloads = app.get('download', u'')
					size = app.get('size', u'')
					game_type = app.get('type', u'')
					url = u"http://info.gamecenter.vivo.com.cn/clientRequest/gameDetail?id=%s&adrVerName=4.4.4&appVersion=37" % app.get('id', u'') if app.get('id', u'') else u''
					#url = u"%s\t%s" % (app.get('pkgName', u''),  app.get('id', u''))
					source = source_map.get(gtype)
					yield rank, game_name, img, downloads, size, source, popular, game_type, status, url
					#for k, v in app.iteritems():
					#	print k, v
					#print 
	except Exception,e:
		mylogger.error("%s====>\t%s" % (_url, traceback.format_exc()))

def store_vivo_app_rank():
	new_games_url = 'http://main.gamecenter.vivo.com.cn/clientRequest/rankList?appVersionName=2.0.0&model=MI+4LTE&e=11010030313647453200da18b1312200&page_index=1&pixel=3.0&imei=865931027730878&origin=527&type=new&av=19&patch_sup=1&cs=0&adrVerName=4.4.4&appVersion=37&elapsedtime=18535194&s=2%7C1363799553'
	single_url = 'http://main.gamecenter.vivo.com.cn/clientRequest/rankList?appVersionName=2.0.0&model=MI+4LTE&e=11010030313647453200da18b1312200&page_index=1&pixel=3.0&imei=865931027730878&origin=528&type=Alone20150916173741&av=19&patch_sup=1&cs=0&adrVerName=4.4.4&appVersion=37&elapsedtime=18658164&s=2%7C1323451747'
	web_game_url = 'http://main.gamecenter.vivo.com.cn/clientRequest/rankList?appVersionName=2.0.0&model=MI+4LTE&e=11010030313647453200da18b1312200&page_index=1&pixel=3.0&imei=865931027730878&origin=529&type=Compr20150916173717&av=19&patch_sup=1&cs=0&adrVerName=4.4.4&appVersion=37&elapsedtime=18675505&s=2%7C2756240867'
	_dict = {'vivo_single': single_url, 'vivo_webgame': web_game_url, 'vivo_new_game': new_games_url}	
	for gtype, _url in _dict.iteritems():
		for data in get_vivo_app_rank(gtype, _url):
			store_data(data)

def get_gionee_app_rank(gtype, param):
	rank = 0
	try:
		for page in xrange(1, 6):
			_url = 'http://game.gionee.com/Api/Local_Clientrank/%s/?&page=%s' % (param, page)
			r = requests.get(_url, timeout=10)
			if r.status_code == 200:
				j = r.json()
				if 'data' in j and 'list' in j['data']:
					for app in j['data']['list']:
						rank += 1
						game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
						game_name = app.get('name', u'')
						img = app.get('img', u'')
						downloads = app.get('downloadCount', u'')
						size = app.get('size', u'')
						game_type = app.get('category', u'')
						#url = u"%s\t%s" % (app.get('package', u''),  app.get('gameid', u''))
						url = u"http://game.gionee.com/Api/Local_Gameinfo/getDetails?gameId=%s" % app.get('gameid') if app.get('gameid', u'') else u''
						source = source_map.get(gtype)
						yield rank, game_name, img, downloads, size, source, popular, game_type, status, url
	except Exception,e:
		mylogger.error("%s====>\t%s" % (_url, traceback.format_exc()))

def store_gionee_app_rank():
	_map = {
						"gionee_active": 'olactiveRankIndex',
						"gionee_hot": 'soaringRankIndex',
					}
	for gtype, param in _map.iteritems():
		for data in get_gionee_app_rank(gtype, param):
			store_data(data)
		

def get_coolpad_app_rank(gtype, fd):
	rank = 0
	_url = "http://gamecenter.coolyun.com/gameAPI/API/getResList?key=0"
	try:
		r = requests.post(_url, timeout=10, data=fd, headers={'Content-Type': 'application/xml'})
		if r.status_code == 200:
			t = re.sub(u'\r|\n', '', r.text)
			doc = xmltodict.parse(t)
			if '@msg' in doc['response'] and doc['response']['@msg'] == u'成功':
				for app in doc['response']['reslist']['res']:
					rank += 1
					game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
					game_name = app.get('@name', u'')
					img = app.get('icon', u'')
					downloads = app.get('downloadtimes', u'')
					game_type = app.get('levelname', u'')
					source = source_map.get(gtype)
					size = app.get('size', u'')
					url = app.get('@rid', u'')
					#url = u"%s\t%s" % (app.get('package_name', u''),  app.get('@rid', u''))
					yield rank, game_name, img, downloads, size, source, popular, game_type, status, url
	except Exception,e:
		mylogger.error("%s====>\t%s" % (gtype, traceback.format_exc()))



def store_coolpad_app_rank():
	webgame_raw_data="""<?xml version="1.0" encoding="utf-8"?><request username="" cloudId="" openId="" sn="865931027730878" platform="1" platver="19" density="480" screensize="1080*1920" language="zh" mobiletype="MI4LTE" version="4" seq="0" appversion="3350" currentnet="WIFI" channelid="coolpad" networkoperator="46001" simserianumber="89860115851040101064" ><rankorder>0</rankorder><syncflag>0</syncflag><start>1</start><categoryid>1</categoryid><iscoolpad>0</iscoolpad><level>0</level><querytype>5</querytype><max>30</max></request>"""

	new_game_raw_data="""<?xml version="1.0" encoding="utf-8"?><request username="" cloudId="" openId="" sn="865931027730878" platform="1" platver="19" density="480" screensize="1080*1920" language="zh" mobiletype="MI4LTE" version="4" seq="0" appversion="3350" currentnet="WIFI" channelid="coolpad" networkoperator="46001" simserianumber="89860115851040101064" ><rankorder>0</rankorder><syncflag>0</syncflag><start>1</start><categoryid>1</categoryid><iscoolpad>0</iscoolpad><level>0</level><querytype>3</querytype><max>30</max></request>"""

	hot_game_raw_data="""<?xml version="1.0" encoding="utf-8"?><request username="" cloudId="" openId="" sn="865931027730878" platform="1" platver="19" density="480" screensize="1080*1920" language="zh" mobiletype="MI4LTE" version="4" seq="0" appversion="3350" currentnet="WIFI" channelid="coolpad" networkoperator="46001" simserianumber="89860115851040101064" ><rankorder>0</rankorder><syncflag>0</syncflag><start>1</start><categoryid>1</categoryid><iscoolpad>0</iscoolpad><level>0</level><querytype>6</querytype><max>30</max></request>"""

	_dict = {'coolpad_hot': hot_game_raw_data, 'coolpad_webgame': webgame_raw_data, 'coolpad_new_game': new_game_raw_data}	
	for gtype, rd in _dict.iteritems():
		for data in get_coolpad_app_rank(gtype, rd):
			store_data(data)

def get_open_play_app_rank(gtype, _url):
	rank = 0
	try:
		r = requests.get(_url, timeout=10)
		if r.status_code == 200:
			j = r.json()
			if j['code'] == 0:
				for app in j['ext']['main']['content']['game_list']:
					rank += 1
					game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
					game_name = app.get('game_name', u'')
					img = app.get('game_icon', u'')
					downloads = app.get('game_download_count', u'')
					size = app.get('game_size', u'')
					game_type = app.get('class_name', u'')
					url = app.get('game_detail_url', u'')
					source = source_map.get(gtype)
					yield rank, game_name, img, downloads, size, source, popular, game_type, status, url
	except Exception,e:
		mylogger.error("%s====>\t%s" % (_url, traceback.format_exc()))



def store_open_play_app_rank():
	download_page 	= "http://open.play.cn/api/v2/mobile/channel/content.json?channel_id=911&terminal_id=18166&current_page=0&rows_of_page=50"
	free_page		= "http://open.play.cn/api/v2/mobile/channel/content.json?channel_id=914&terminal_id=18166&current_page=0&rows_of_page=50"
	webgame_page 	= "http://open.play.cn/api/v2/mobile/channel/content.json?channel_id=917&terminal_id=18166&current_page=0&rows_of_page=50"
	rise_page 		= "http://open.play.cn/api/v2/mobile/channel/content.json?channel_id=916&terminal_id=18166&current_page=0&rows_of_page=50"
	_dict = {'open_play_download': download_page, 'open_play_free': free_page, 'open_play_webgame': webgame_page, 'open_play_rise': rise_page}	
	for gtype, _url in _dict.iteritems():
		for data in get_open_play_app_rank(gtype, _url):
			store_data(data)

def get_wandoujia_app_rank(gtype, _url):
	rank = 0
	try:
		r = requests.get(_url, timeout=10)
		if r.status_code == 200:
			j = r.json()
			if j['entity'] is not None:
				for item in j['entity']:
					rank += 1
					game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
					game_name = item.get('title', u'')
					img = item.get('icon', u'')
					source = source_map.get(gtype)
					if item['action'] is not None:
						info =  get_wandoujia_detail(item['action']['url'])
						if info is not None:
							game_type, downloads = info 
						url = item['action'].get('url', u'')
					yield rank, game_name, img, downloads, size, source, popular, game_type, status, url
					#for k, v in item['detail']['appDetail'].iteritems():
					#	print k, v
	except Exception,e:
		mylogger.error("%s====>\t%s" % (_url, traceback.format_exc()))

def store_wandoujia_app_rank():
	single_url 		= "http://apis.wandoujia.com/five/v2/games/tops/TOP_WEEKLY_DOWNLOAD_CONSOLE_GAME?max=20"
	web_game_url 	= "http://apis.wandoujia.com/five/v2/games/tops/TOP_WEEKLY_DOWNLOAD_ONLINE_GAME?start=0&max=20"
	_dict = {'wandoujia_single': single_url, 'wandoujia_webgame': web_game_url}	
	for gtype, _url in _dict.iteritems():
		for data in get_wandoujia_app_rank(gtype, _url):
			store_data(data)


def get_wandoujia_detail(url):
	try:
		r = requests.get(url, timeout=10)
		if r.status_code == 200:
			d = r.json()
			entity = d['entity']
			if entity:
				detail = entity[0]['detail']['appDetail']
				if detail is not None:
					categories = detail.get('categories', [])
					game_type = u",".join([c['name'] for c in categories if c['level']==1])
					popular = detail.get('downloadCount', u'')
					return game_type, popular
	except Exception,e:
		mylogger.error("### %s ### %s" % (url.encode('utf-8'), traceback.format_exc()))
	return None


def get_iqiyi_app_rank(gtype, _url):
	rank = 0
	try:
		r = requests.get(_url, timeout=10)
		if r.status_code == 200:
			m = re.search(u'rs\\(([\s\S]*)\\)\\;', r.text)
			if m is not None:
				d = json.loads(m.group(1))
				if d['apps'] is not None:
					for app in d['apps']:
						rank += 1
						game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
						game_name = app.get('name', u'')
						img = app.get('icon', u'')
						size = app.get('size', u'')
						downloads = app.get('cnt', u'')
						url = app.get('qipu_id', u'')
						game_type = app.get('cate_name', u'')
						source = source_map.get(gtype)
						yield rank, game_name, img, downloads, size, source, popular, game_type, status, url
	except Exception, e:
		mylogger.error("### %s ###\n%s" % (_url, traceback.format_exc()))

def store_iqiyi_app_rank():
	_dict = {'iqiyi_download': "http://store.iqiyi.com/gc/top//download?callback=rs&id=download&no=1", 'iqiyi_hot' : "http://store.iqiyi.com/gc/top/up?callback=rs&t=1445585439376"}	
	for gtype, _url in _dict.iteritems():
		for data in get_iqiyi_app_rank(gtype, _url):
			store_data(data)


def get_youku_app_rank(gtype, _url):
	rank = 0
	try:
		r = requests.get(_url, timeout=10)
		if r.status_code == 200:
			j = r.json()
			if j['status'] == u'success':
				for app in j['games']:
					rank += 1
					game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
					game_name = app.get('appname', u'')
					img = app.get('logo', u'')
					downloads = app.get('total_downloads', u'')
					size = app.get('size', u'')
					url = app.get('id', u'')
					source = source_map.get(gtype)
					yield rank, game_name, img, downloads, size, source, popular, game_type, status, url
					#for k,v in app.iteritems():
					#	print k,v
	except Exception,e:
		mylogger.error("%s====>\t%s" % (_url, traceback.format_exc()))


def store_youku_app_rank():
	_dict = {"youku_single": 'http://api.gamex.mobile.youku.com/app/rank/classified?product_id=1&pz=40&pg=1&type=1', 'youku_webgame': 'http://api.gamex.mobile.youku.com/app/rank/classified?product_id=1&pz=40&pg=1&type=0'}
	for gtype, _url in _dict.iteritems():
		for data in get_youku_app_rank(gtype, _url):
			store_data(data)

def get_sogou_app_rank(gtype, _url):
	rank = 0
	try:
		r = requests.get(_url, timeout=10)
		if r.status_code == 200:
			j = r.json()
			if j['recommend_app'] is not None:
				for app in j['recommend_app']:
					rank += 1
					game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
					game_name = app.get('name', u'')
					img = app.get('icon', u'')
					size = app.get('size', u'')
					downloads = app.get('downloadCount', u'')
					size = app.get('size', u'')
					source = source_map.get(gtype)
					#url = u"%s\t%s" % (app.get('packagename', u''),  app.get('appid', u''))
					url = u"http://mouile.zhushou.sogou.com/m/appDetail.html?id=%s" % app.get('appid') if app.get('appid', u'') else u''
					yield rank, game_name, img, downloads, size, source, popular, game_type, status, url
					#for k,v in app.iteritems():
					#	print k,v
	except Exception,e:
		mylogger.error("%s====>\t%s" % (_url, traceback.format_exc()))


def store_sogou_app_rank():
	_dict = {"sogou_single": 'http://mobile.zhushou.sogou.com/android/rank/toplist.html?id=12&limit=25&group=2&start=0&iv=41&uid=f3c2ed94d7d2272de87a8ef3abab2409&vn=4.1.3&channel=baidu&sogouid=a7f30d60a6b1aed168a8c9d7c46bbac5&stoken==SnxL9KjGT6sBvQ7ZJD4Ghw&cellid=&sc=0', 'sogou_webgame': 'http://mobile.zhushou.sogou.com/android/rank/toplist.html?id=11&limit=25&group=2&start=0&iv=41&uid=f3c2ed94d7d2272de87a8ef3abab2409&vn=4.1.3&channel=baidu&sogouid=a7f30d60a6b1aed168a8c9d7c46bbac5&stoken==SnxL9KjGT6sBvQ7ZJD4Ghw&cellid=&sc=0', 'sogou_download':'http://mobile.zhushou.sogou.com/android/rank/toplist.html?id=10&limit=25&group=2&start=0&iv=41&uid=f3c2ed94d7d2272de87a8ef3abab2409&vn=4.1.3&channel=baidu&sogouid=a7f30d60a6b1aed168a8c9d7c46bbac5&stoken==SnxL9KjGT6sBvQ7ZJD4Ghw&cellid=&sc=0'}
	for gtype, _url in _dict.iteritems():
		for data in get_sogou_app_rank(gtype, _url):
			store_data(data)
	mylogger.info("get sogou app rank end... ")

def get_i4_app_rank():
	rank = 0
	_url = 'http://app3.i4.cn/controller/action/online.go?store=3&module=3&rows=50&sort=2&submodule=5&model=101&id=0&reqtype=3&page=1'
	try:
		r = requests.get(_url, timeout=10)
		if r.status_code == 200:
			j = r.json()
			if j['result'] is not None and j['result']['list']:
				for app in j['result']['list']:
					rank += 1
					game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
					game_name = app.get('appName', u'')
					img = u'http://d.image.i4.cn/image/%s' % app.get('icon', u'')
					size = app.get('size', u'')
					game_type = app.get('typeName', u'')
					downloads = app.get('downCount', u'')
					size = app.get('size', u'')
					source = source_map.get('i4_hot')
					#url = u"%s\t%s" % (app.get('sourceId', u''),  app.get('id', u''))
					url = u"http://app3.i4.cn/controller/action/online.go?store=3&module=1&id=%s&reqtype=5" % app.get('id', u'') if app.get('id', u'') else u''
					store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
	except Exception,e:
		mylogger.error("%s====>\t%s" % (_url, traceback.format_exc()))


def get_pp_app_rank():
	rank = 0
	headers = {'tunnel-command':4261421088}
	try:
		d = {"dcType":0, "resType":2, "listType":5, "catId":0, "clFlag":1, "perCount":50, "page":0}
		r = requests.post('http://jsondata.25pp.com/index.html', data=json.dumps(d), headers=headers)
		if r.status_code == 200:
			content = re.sub(u'\ufeff', u'', r.text)
			j = json.loads(content)
			if j['content'] is not None:
				for app in j['content']:
					rank += 1
					game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
					game_name = app.get('title', u'')
					img = app.get('thumb', u'')
					downloads = app.get('downloads', u'')
					size = app.get('fsize', u'')
					source = source_map.get('pp_hot')
					url = app.get('id', u'')
					#url = u"%s\t%s" % (app.get('buid', u''),  app.get('id', u''))
					out = [rank, game_name, img, downloads, size, source, popular, game_type, status, url]
					store_data(out)
	except Exception,e:
		mylogger.error("get pp app rank\t%s" % (traceback.format_exc()))



def get_kuaiyong_app_rank():
	rank = 0
	URL = "http://app.kuaiyong.com/ranking/index/appType/game"
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			for item in soup.find_all('div', class_="app-item-info"):
				info = item.find('a', class_='app-name')
				if info is not None:
					detail_url = u"http://app.kuaiyong.com%s" % info.get('href')
					app = get_kuaiyong_detail(detail_url)
					if app:
						rank += 1
						game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
						game_name = app.get('title', u'')
						img = app.get('img', u'')
						size = app.get(u'大　　小', u'')
						downloads = app.get(u'下载', u'')
						game_type = app.get(u'类　　别', u'')
						source = source_map.get('kuaiyong_hot')
						url = detail_url
						out = [rank, game_name, img, downloads, size, source, popular, game_type, status, url]
						store_data(out)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))


def get_kuaiyong_detail(URL):
	mydict = {}
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			base_left = soup.find('div', class_='base-left')
			if base_left is not None:
				img = base_left.find('img')
				if img is not None:
					mydict['img'] = img.get('src')
			base_right = soup.find('div', class_='base-right')
			if base_right is not None:
				if base_right.find('h1') is not None:
					mydict[u'title'] = base_right.find('h1').text
				base_list = base_right.find('div', class_='base-list')
				if base_list is not None:
					for ret in base_list.find_all('p'):
						if ret.text:
							segs = ret.text.split(u'：')
							if len(segs) == 2:
								mydict[segs[0]] = segs[1]
							elif len(segs)==1 and u'次下载' in ret.text:
								mydict[u'下载'] = re.sub(u'次下载|\n|\r', u'', ret.text)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	return mydict


def get_itools_app_rank():
	rank = 0
	URL = "http://ios.itools.cn/game/iphone/gameall_1"
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			ul = soup.find('ul', class_='ios_app_list')
			if ul is not None:
				for app in ul.find_all('li')[:50]:
					app_on = app.find('div', class_='ios_app_on')
					if app_on is not None:
						detail_url = app_on.find('a').get('href') if app_on.find('a') is not None else u''
						if detail_url:
							detail_url = u"http://ios.itools.cn%s" % detail_url
							app = get_itools_detail(detail_url)
							if app:
								rank += 1
								game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
								game_name = app.get('title', u'')
								img = app.get('img', u'')
								size = app.get(u'大       小', u'')
								source = source_map.get('itools_hot')
								url = detail_url
								out = [rank, game_name, img, downloads, size, source, popular, game_type, status, url]
								store_data(out)
							#for k, v in detail.iteritems():
							#	print k, v
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get itools app rank end... ")


def get_itools_detail(URL):
	mydict = {}
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			details_app = soup.find('div', class_="details_app")
			if details_app is not None:
				img_div = details_app.find('div', class_='fl w140')
				if img_div is not None:
					img = img_div.find('p').find('img').get('src') if img_div.find('p') is not None else u''
					mydict['img'] = img
				info_div = details_app.find('dl', class_='fl')
				if info_div is not None:
					mydict['title'] = info_div.find('dt').text
					for info in info_div.find_all('span'):
						segs =  info.text.split(u'：')
						if len(segs) == 2:
							mydict[segs[0]] = segs[1]
					for info in info_div.find_all('dd'):
						segs =  info.text.split(u'：')
						if len(segs) == 2:
							mydict[segs[0]] = segs[1]
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	return mydict


def get_xyzs_app_rank():
	rank = 0
	URL = "http://interface.xyzs.com/v2/ios/c01/rank/game?p=1&ps=20"
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
			j = response.json()
			if j['code'] == 200:
				for app in j['data']['result']:
					rank += 1
					game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
					game_name = app.get('title', u'')
					img = app.get('icon', u'')
					size = app.get('size', u'')
					game_type = app.get('cus_desc', u'')
					downloads = app.get('downloadnum', u'')
					source = source_map.get('xyzs_hot')
					#url = u"%s\t%s" % (app.get('bundleid', u''),  app.get('itunesid', u''))
					url = app.get('itunesid', u'')
					store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))


def get_91play_app_rank():
	rank = 0
	URL = "http://play.91.com/api.php/Api/index"
	try:
		raw_data = {"firmware":"19","time":1449459810294,"device":1,"action":30011,"app_version":302,"action_version":4,"mac":"7b715ce093480b34d6987","debug":0}
		response = requests.post(URL, data=raw_data, timeout=10)
		if response.status_code == 200:
			j = response.json()
			if j['data'] is not None:
				for app in json.loads(j['data']):
					rank += 1
					#for k, v in app.iteritems():
					#	print k, v
					game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
					game_name = app.get('name', u'')
					img = app.get('icon_url', u'')
					size = app.get('app_size', u'')
					game_type = app.get('type_name', u'')
					downloads = app.get('download_count', u'')
					source = source_map.get('91play_hot')
					url = app.get('id', u'')
					#url = u"%s\t%s" % (app.get('package_name', u''),  app.get('id', u''))
					store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
	except Exception,e:
		mylogger.error("91play app rank\t%s" % (traceback.format_exc()))


def get_360_gamebox_app_rank(gtype, url):
	rank = 0
	try:
		response = requests.get(url, timeout=10)
		if response.status_code == 200:
			j = response.json()
			if j['data'] is not None:
				for app in j['data']:
					rank += 1
					#for k, v in app.iteritems():
					#	print k, v
					game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
					game_name = app.get('name', u'')
					img = app.get('logo_url', u'')
					size = app.get('size', u'')
					game_type = app.get('category_name', u'')
					downloads = app.get('download_times', u'')
					source = source_map.get(gtype)
					#url = u"%s\t%s" % (app.get('apkid', u''),  app.get('id', u''))
					url = u"http://next.gamebox.360.cn/7/xgamebox/getappintro?pname=%s" % app.get('apkid', u'') if app.get('apkid', u'') else u''
					yield rank, game_name, img, downloads, size, source, popular, game_type, status, url
	except Exception,e:
		mylogger.error("360_gamebox app rank\t%s" % (traceback.format_exc()))

def store_360_gamebox_app_rank():
	_dict = {
			"360_gamebox_single" : "http://next.gamebox.360.cn/7/xgamebox/rank?count=20&start=0&typeid=2&type=download", 	
			"360_gamebox_webgame": "http://next.gamebox.360.cn/7/xgamebox/rank?count=20&start=0&typeid=1&type=download", 	
			}
	for gtype, url in _dict.iteritems():
		for data in get_360_gamebox_app_rank(gtype, url):
			store_data(data)

def store_xiaomi_app_rank():
	_dict = {"xiaomi_app_download": "http://app.migc.xiaomi.com/cms/interface/v5/rankgamelist1.php?uid=20150905_132380697&platform=android&os=V6.7.1.0.KXDCNCH&stampTime=1449557687000&density=480&imei=865931027730878&pageSize=20&versionCode=1822&cid=gamecenter_100_1_android%7C865931027730878&clientId=40b53f3e316bda9f83c2e0c094d5b7f6&vn=MIGAMEAPPSTAND_1.8.22&co=CN&page=1&macWifi=3480B34D6987&la=zh&ua=Xiaomi%257CMI%2B4LTE%257C4.4.4%257CKTU84P%257C19%257Ccancro&carrier=unicom&rankId=17&mnc=46001&fuid=&mid=&imsi=460015776509846&sdk=19&mac3g=&bid=701",
			"xiaomi_app_hot": "http://app.migc.xiaomi.com/cms/interface/v5/rankgamelist1.php?uid=20150905_132380697&platform=android&os=V6.7.1.0.KXDCNCH&stampTime=1449557980000&density=480&imei=865931027730878&pageSize=20&versionCode=1822&cid=gamecenter_100_1_android%7C865931027730878&clientId=40b53f3e316bda9f83c2e0c094d5b7f6&vn=MIGAMEAPPSTAND_1.8.22&co=CN&page=1&macWifi=3480B34D6987&la=zh&ua=Xiaomi%257CMI%2B4LTE%257C4.4.4%257CKTU84P%257C19%257Ccancro&carrier=unicom&rankId=18&mnc=46001&fuid=&mid=&imsi=460015776509846&sdk=19&mac3g=&bid=701"}
	for gtype, url in _dict.iteritems():
		get_xiaomi_app_rank(gtype, url)
		

def get_xiaomi_app_rank(gtype, url):
	rank = 0
	try:
		response = requests.get(url, timeout=10)
		if response.status_code == 200:
			j = response.json()
			if j['gameList'] is not None:
				for app in j['gameList']:
					rank += 1
					game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
					game_name = app.get('displayName', u'')
					img = app.get('icon', u'')
					size = app.get('apkSize', u'')
					game_type = app.get('className', u'')
					downloads = app.get('downloadCount', u'')
					source = source_map.get(gtype)
					url = app.get('packageName', u'')
					store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
	except Exception,e:
		mylogger.error("xiaomi game app rank\t%s" % (traceback.format_exc()))

def store_18183_top_app_rank():
	_dict = {'18183_top': 'http://top.18183.com/', '18183_hot': 'http://top.18183.com/hot.html'}
	for gtype, url in _dict.iteritems():
		get_18183_top_app_rank(gtype, url)


def get_18183_top_app_rank(gtype, url):
	rank = 0
	try:
		response = requests.get(url, timeout=10)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			ranking_mod = soup.find('div', class_='ranking-mod')
			if ranking_mod is not None:
				for app in ranking_mod.find_all('li'):
					num_fl = app.find('div', class_='num fl')
					if num_fl is not None:
						game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
						rank = num_fl.text
						dt = app.find('dt')
						if dt is not None and dt.find('a') is not None:
							game_name = dt.find('a').get('title')
							url = dt.find('a').get('href')
							img = dt.find('img').get('src')
						rank_fl = app.find('div', class_='rank fl')
						if rank_fl is not None and rank_fl.find('p') is not None:
							downloads = rank_fl.find('p').text 
						source = source_map.get(gtype)
						store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
						#print rank, game_name, source, url, downloads
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))

def get_tbzs_app_rank():
	raw_data_map = {
			'tbzs_single'	: {"sign":"7c54c6ceded15e80342794c6d13646a4","data":{"flags":193,"count":20,"offset":0,"order":13,"page":1,"positionId":549,"resourceType":1},"id":2472251151577597201,"client":{"caller":"secret.pp.client","versionCode":1393,"ex":{"cityCode":"0755","aid":"gj\/4\/Osm5gwpjlFgnvkVCQ==","ch":"PT_4","osVersion":19,"productId":2002},"VName":"4.7.0","uuid":"bTkwHyimxYyNDQzBWGVG\/kQ5Q9aqRKjrTmkhTksZlxPjWz55Gh0KRgROPDXaQ3T8uOTA\/6onICCEiA=="},"encrypt":"md5"}, 
			'tbzs_webgame'	: {"sign":"988f075faf00cfe11ab2f5278b08ffb1","data":{"flags":193,"count":20,"offset":0,"order":14,"page":1,"positionId":551,"resourceType":1},"id":3601133516216288053,"client":{"caller":"secret.pp.client","versionCode":1393,"ex":{"cityCode":"0755","aid":"gj\/4\/Osm5gwpjlFgnvkVCQ==","ch":"PT_4","osVersion":19,"productId":2002},"VName":"4.7.0","uuid":"bTkwH8QcSHwR84\/R\/PPDDgxVSfaScKaLeouYfn+7HMNzcyo5qsX+Bgj4q4XWDeVMACA2XwLbEoA8TA=="},"encrypt":"md5"}, 
			'tbzs_rise'		: {"sign":"d59759061e1a29cd703496864239d7d1","data":{"flags":193,"order":9,"count":20,"page":1,"resourceType":1},"id":-3452676716686130419,"client":{"caller":"secret.pp.client","versionCode":1393,"ex":{"cityCode":"0755","aid":"gj\/4\/Osm5gwpjlFgnvkVCQ==","ch":"PT_4","osVersion":19,"productId":2002},"VName":"4.7.0","uuid":"bTkwH+NbLMg2sLMFg7IvwsrTkV5Q\/t5zn050App46O\/3D5oJLsFuVuPHPwG9yHnI2tpeB8xhukjmtg=="},"encrypt":"md5"}}

	_dict = {'tbzs_rise'	: 'http://sjzs-api.25pp.com/api/resource.app.getList',
			 'tbzs_single'	: 'http://sjzs-api.25pp.com/api/op.rec.app.list',
			 'tbzs_webgame'	: 'http://sjzs-api.25pp.com/api/op.rec.app.list'}
	for gtype, url in _dict.iteritems():
		rank = 0
		try:
			raw_data = raw_data_map.get(gtype)
			r = requests.post(url, data=json.dumps(raw_data))
			if r.status_code == 200:
				j = r.json()
				if j['state']['msg'] == u'Ok':
					for app in j['data']['content']:
						rank += 1
						game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
						game_name = app.get('name', u'')
						img = app.get('iconUrl', u'')
						size = app.get('size', u'')
						game_type = app.get('categoryName', u'')
						downloads = app.get('downloads', u'')
						source = source_map.get(gtype)
						url = u"%s\t%s" % (app.get('packageName', u''),  app.get('id', u''))
						#print rank, game_name, downloads
						store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
		except Exception,e:
			mylogger.error("%s\t%s" % (url, traceback.format_exc()))

def get_tbzs_detail(game_id):
	raw_data = {"sign":"bc78c22c95972167a0e16edae52994b1","data":[{"data":{"screenWidth":1080,"appId":game_id},"service":"resource.app.getDetail"},{"data":{"count":5,"screenWidth":1080,"appId":game_id},"service":"behavior.question.listByAppId"},{"data":{"appId":game_id},"service":"resource.app.getGameNewsList"},{"data":{"id":game_id},"service":"op.app.article.get"}],"id":-1945496287406372250,"client":{"caller":"secret.pp.client","versionCode":1393,"ex":{"cityCode":"0755","aid":"gj\/4\/Osm5gwpjlFgnvkVCQ==","ch":"PT_4","osVersion":19,"productId":2002},"VName":"4.7.0","uuid":"bTkwH81xSdAoRpAN9ajCuj6PSy58qqBjUYideli6A8dfpy5p9mn6tl1RoGkjeuggXiYoV0jlCJhiSg=="},"encrypt":"md5"}
	r = requests.post('http://sjzs-api.25pp.com/api/combine', data=json.dumps(raw_data))
	if r.status_code == 200:
		j = r.json()
		print j['state']['msg']


def get_wogame_app_rank(gtype, url):
	rank = 0
	try:
		_j = {"page_size":20,"page_num":1}
		params = {"jsondata": json.dumps(_j)}
		r = requests.get(url, timeout=10, params=params)
		if r.status_code == 200:
			j = r.json()
			if j['data'] is not None:
				for app in r.json()['data']:
					rank += 1
					game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
					game_name = app.get('game_name', u'')
					img = app.get('icon_url', u'')
					size = app.get('apk_size', u'')
					downloads = app.get('download_count', u'')#每周下载次数
					source = source_map.get(gtype)
					url = app.get('product_id', u'')
					#url = u"%s\t%s" % (app.get('package_name', u''),  app.get('product_id', u''))
					store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))

def store_wogame_app_rank():
	_dict = {"wogame_hot": "http://wogame4.wostore.cn/wogame/weekHotList.do",
			"wogame_new" : "http://wogame4.wostore.cn/wogame/newGameList.do"}
	for gtype, url in _dict.iteritems():
		get_wogame_app_rank(gtype, url)


def get_lenovo_gamecenter_app_rank():
	_dict = {
				"lenovo_gc_mostuser": "http://yx.lenovomm.com/business/app!getMostUser.action?dpi=480&height=1920&dev=ph&width=1080&t=50&s=0",
				"lenovo_gc_mosttime": "http://yx.lenovomm.com/business/app!getMostTime.action?dpi=480&height=1920&dev=ph&width=1080&t=50&s=0",
				"lenovo_gc_newest": "http://yx.lenovomm.com/business/app!getNewest.action?dpi=480&height=1920&dev=ph&width=1080&t=50&s=0"
			}
	for gtype, url in _dict.iteritems():
		rank = 0
		try:
			r = requests.get(url, timeout=10)
			if r.status_code == 200:
				j = r.json()
				if j['datalist'] is not None:
					for item in j['datalist']:
						rank += 1
						game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
						if 'app' not in item:
							app = item
						else:
							app = item['app']	
						game_name = app.get('name', u'')
						img = app.get('iconAddr', u'')
						size = app.get('size', u'')
						game_type = app.get('categoryName', u'')
						downloads = app.get('realDownCount', u'')
						source = source_map.get(gtype)
						pkg_name = app.get('packageName', u'')
						if pkg_name:
							url = u"http://yx.lenovomm.com/business/app!getAppDetail5.action?dpi=480&height=1920&dev=ph&width=1080&cpu=armeabi-v7a&pn=%s&uid=72DB07100FC223A2EDE82F4A44AE96B4&os=4.4.4&perf=hp&model=MI 4LTE&type=0&density=xx&mac=7A031DAB40535B3F5E204582EB961FC5" % pkg_name
						store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
		except Exception,e:
			mylogger.error("%s\t%s" % (url, traceback.format_exc()))

def get_lenovo_shop_rank():
	_dict = {
			"lenovo_shop_racing_car": "http://223.202.25.30/ams/api/applist?l=zh-CN&si=1&c=20&lt=subject&cg=subject&code=21701&nremark=1&pa=ams5.0_7402535-2-2-22-1-3-1_480-8",
			"lenovo_shop_android_free" : "http://223.202.25.30/ams/api/applist?l=zh-CN&si=1&c=20&lt=subject&cg=subject&code=21569&nremark=1&pa=ams5.0_7402535-2-2-22-1-3-1_480-8",
			"lenovo_shop_parkour" : "http://223.202.25.30/ams/api/applist?l=zh-CN&si=1&c=20&lt=subject&cg=subject&code=21083&nremark=1&pa=ams5.0_7402535-2-2-22-1-3-1_480-8",
			"lenovo_shop_hard_game" : "http://223.202.25.30/ams/api/applist?l=zh-CN&si=1&c=20&lt=subject&cg=subject&code=21565&nremark=1&pa=ams5.0_7402535-2-2-22-1-3-1_480-8"
			}
	headers = {"clientid": "141623-2-2-19-1-3-1_480_i865931027730878t19700201770903586_c20524d1p1"}
	for gtype,url in _dict.iteritems():
		rank = 0
		try:
			r = requests.get(url, timeout=10, headers=headers)
			if r.status_code == 200:
				j = r.json()
				if j['datalist'] is not None:
					for app in j['datalist']:
						rank += 1
						game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
						game_name = app.get('name', u'')
						img = app.get('iconAddr', u'')
						size = app.get('apkSize', u'')
						game_type = app.get('apptype', u'')
						downloads = app.get('downloadCount', u'')
						source = source_map.get(gtype)
						pkg_name = app.get('packageName', u'')
						if pkg_name:
							url = "http://223.202.25.30/ams/api/appinfo?l=zh-CN&pn=%s&vc=100150928&woi=0&pa=ams5.0_141623-2-2-19-1-3-1_480-8" % pkg_name
						store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
		except Exception,e:
			mylogger.error("%s\t%s" % (url, traceback.format_exc()))

def get_meizu_app_rank():
	_dict = {
			"meizu_webgame" : "http://api-game.meizu.com/games/public/top/online/layout?start=0&max=50&os=21",
			"meizu_single" 	: "http://api-game.meizu.com/games/public/top/solo/layout?start=0&os=21&max=50",
			}
	for gtype,url in _dict.iteritems():
		rank = 0
		try:
			r = requests.get(url, timeout=10)
			if r.status_code == 200:
				j = r.json()
				if j['value'] is not None and len(j['value']['blocks'])>=1 and j['value']['blocks'][0]['data']:
					for app in j['value']['blocks'][0]['data']:
						rank += 1
						game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
						game_name = app.get('name', u'')
						img = app.get('icon', u'')
						size = app.get('size', u'')
						game_type = app.get('category_name', u'')
						downloads = app.get('download_count', u'')
						source = source_map.get(gtype)
						url = u"http://api-game.meizu.com/games/public/detail/%s" % app.get('id', u'') if app.get('id', u'') else u''
						store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
		except Exception,e:
			mylogger.error("%s\t%s" % (url, traceback.format_exc()))


def get_wostore_app_rank():
	headers = {
			"phoneAccessMode": "3",
			"version": "android_v5.0.3",
			"handphone": "00000000000"}
	try:
		r = requests.get("http://clientnew.wostore.cn:6106/appstore_agent/unistore/servicedata.do?serviceid=rankingList&channel=2", headers=headers, timeout=10)	
		if r.status_code == 200:
			j = r.json()
			for ranklist in j['RANKINGLIST']:
				source = -1
				rank = 0
				if ranklist.get('rankingName', u'') == u'新游榜':
					source = source_map.get('wostore_new_game', -1)
				elif ranklist.get('rankingName', u'') == u'热门榜':
					source = source_map.get('wostore_hot', -1)
				if source != -1:
					for app in ranklist['RANKINGAPP']:
						rank += 1
						game_name, img, downloads, size, popular, game_type, status, url = [u''] * 8
						game_name = app.get('appName', u'')
						img = app.get('iconURL', u'')
						size = app.get('size', u'')
						downloads = app.get('downloadCout', u'')
						pkg_id = app.get('productIndex', u'')
						if pkg_id:
							url = "http://clientnew.wostore.cn:6106/appstore_agent/unistore/servicedata.do?serviceid=productDetail&productIndex=%s&resource=null&referer=null" % pkg_id
						store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
	except Exception,e:
		mylogger.error("get wostore rank \t%s" % (traceback.format_exc()))
	mylogger.info("get wostore rank done!")


def get_mmstore_app_rank():
	rank = 0
	headers = {
				"appname": "MM5.3.0.001.01_CTAndroid_JT", 
				"ua":"android-19-720x1280-CHE2-UL00"}
	for p in xrange(1, 3):
		url = "http://odp.mmarket.com/t.do?requestid=json_game_total_ranking_library&currentPage=%s&totalRows=824" % p
		try:
			r = requests.get(url, timeout=20, headers=headers)
			if r.status_code == 200:
				j = r.json()
				if j['items'] is not None:
					for app in j['items']:
						rank += 1
						game_name, img, downloads, size, popular, game_type, status, url = [u''] * 8
						game_name = app.get('name', u'')
						img = app.get('iconUrl', u'')
						size = app.get('appsize', u'')
						downloads = app.get('interested', u'')
						url = app.get('detailUrl', u'')
						source = source_map.get('mmstore_hot')
						store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
		except Exception, e:
			mylogger.error("get mmstore app rank \t%s" % (traceback.format_exc()))

def get_vivo_store_app_rank():
	_dict = {
			"vivo_store_single": "http://main.appstore.vivo.com.cn/port/packages_top/?apps_per_page=20&e=150100523832314d4200cf98e451625f&elapsedtime=2564215904&screensize=1080_1920&density=3.0&pictype=webp&cs=0&req_id=7&av=22&an=5.1&app_version=612&imei=867570026068423&nt=WIFI&id=2&page_index=1&cfrom=4&type=9&model=m2+note&s=2%7C0",
			"vivo_store_webgame": "http://main.appstore.vivo.com.cn/port/packages_top/?apps_per_page=20&e=150100523832314d4200cf98e451625f&elapsedtime=2564218581&screensize=1080_1920&density=3.0&pictype=webp&cs=0&req_id=8&av=22&an=5.1&app_version=612&imei=867570026068423&nt=WIFI&id=2&page_index=1&cfrom=4&type=10&model=m2+note&s=2%7C0",
			}
	for gtype, url in _dict.iteritems():
		rank = 0
		try:
			r = requests.get(url, timeout=20)
			if r.status_code == 200:
				j = r.json()
				if j['value'] is not None:
					for app in j['value']:
						rank += 1
						game_name, img, downloads, size, popular, game_type, status, url = [u''] * 8
						game_name = app.get('title_zh', u'')
						img = app.get('icon_url', u'')
						downloads = app.get('download_count', u'')
						url = app.get('id', u'')
						source = source_map.get(gtype)
						store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
		except Exception, e:
			mylogger.error("get vivo store app rank \t%s" % (traceback.format_exc()))

def get_myaora_app_rank():
	_dict = {
			"myaora_download"	: {"TAG":"SOFT_HOT","API_VERSION":9,"MARKET_IMEI":"867570026068423","MARKET_KEY":"5bed9c59b8d64b24d35eedf7b8065115","INDEX_START":0,"INDEX_SIZE":20,"MODEL":"m2 note","PCATID":2},
			"myaora_rise"		: {"TAG":"GET_SOAR_LIST","API_VERSION":9,"MARKET_IMEI":"867570026068423","MARKET_KEY":"5bed9c59b8d64b24d35eedf7b8065115","INDEX_START":0,"INDEX_SIZE":20,"MODEL":"m2 note","PCATID":2} ,
			}
	for gtype, raw_data in _dict.iteritems():
		rank = 0
		try:
			r = requests.post("http://adres.myaora.net:81/api.php", timeout=20, data=json.dumps(raw_data))
			if r.status_code == 200:
				j = r.json()
				if j['ARRAY'] is not None:
					for app in j['ARRAY']:
						rank += 1
						game_name, img, downloads, size, popular, game_type, status, url = [u''] * 8
						game_name = app.get('NAME', u'')
						img = app.get('ICON_URL', u'')
						downloads = app.get('DOWNLOAD_COUNT', u'')
						game_type = app.get('CATALOG_NAME', u'')
						url = app.get('ID', u'')
						size = app.get('SIZE', u'')
						source = source_map.get(gtype)
						#print rank, game_name, source
						store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
		except Exception, e:
			mylogger.error("get myaora  app rank \t%s" % (traceback.format_exc()))

def get_huawei_app_rank():
	_dict = {
			"huawei_single_weekly": "clientPackage=com.huawei.gamebox&cno=4010001&code=0500&hcrId=8BE2222453F8466690700BD3D29AFDF9&isShake=0&iv=jVRKhj%2Flrx0p0HvA9r8usg%3D%3D&maxResults=25&method=client.getTabDetail&net=1&reqPageNum=1&salt=-3169502808676295893&serviceType=5&shakeReqPageNum=0&sign=b9001011cs11105320000000%4021ED0F3A6FB3EB1012341D7446889DC3&trace=618FC606383111E5A1B100188DD60001&ts=1450347536594&uri=618FC606383111E5A1B100188DD60002&userId=5F04B6AE58FFB279B169FA8FA0DA4ED0&ver=1.1&nsp_key=ynhRv46WNXWL8Hcf1rBPrXGizto%3D",
			"huawei_webgame_weekly": "clientPackage=com.huawei.gamebox&cno=4010001&code=0500&hcrId=8BE2222453F8466690700BD3D29AFDF9&isShake=0&iv=Gn0QT5E4AY6OYv1B26Bhag%3D%3D&maxResults=25&method=client.getTabDetail&net=1&reqPageNum=1&salt=-747596652580722219&serviceType=5&shakeReqPageNum=0&sign=b9001011cs11105320000000%4021ED0F3A6FB3EB1012341D7446889DC3&trace=618FC606383111E5A1B100188DD60001&ts=1450347636420&uri=618FC606383111E5A1B100188DD60003&userId=0C838299767D23AD6DD0D966FA5A3CEF&ver=1.1&nsp_key=bZADz5EnfWc2wYMXk7vHH02Rw%2Fk%3D",
			"huawei_newgame": "clientPackage=com.huawei.gamebox&cno=4010001&code=0500&hcrId=8BE2222453F8466690700BD3D29AFDF9&isShake=0&iv=ykERKQ1C%2FSWBOJqRHDp0hA%3D%3D&maxResults=25&method=client.getTabDetail&net=1&reqPageNum=1&salt=-9010689806809620686&serviceType=5&shakeReqPageNum=0&sign=b9001011cs11105320000000%4021ED0F3A6FB3EB1012341D7446889DC3&trace=618FC606383111E5A1B100188DD60001&ts=1450347681402&uri=f7bdb327d25944009c49e85af1e57720&userId=2FCCA764709EA036AA7EFD260899DF6F&ver=1.1&nsp_key=cGFs8TLV6gZd3rWVLzFE7uCRzaI%3D",
			"huawei_hot": "clientPackage=com.huawei.gamebox&cno=4010001&code=0500&hcrId=8BE2222453F8466690700BD3D29AFDF9&isShake=0&iv=7a3zIqRoB2B%2FNmgu3dBBVQ%3D%3D&maxResults=25&method=client.getTabDetail&net=1&reqPageNum=1&salt=4847397490382914763&serviceType=5&shakeReqPageNum=0&sign=b9001011cs11105320000000%4021ED0F3A6FB3EB1012341D7446889DC3&trace=618FC606383111E5A1B100188DD60001&ts=1450347704924&uri=618FC606383111E5A1B100188DD60004&userId=086D895DD0AEC90355EE815AA89C30C2&ver=1.1&nsp_key=zMAT4fnASLck%2BcUsfvwMPhvuQBg%3D",
			}
	headers = {
				'Content-Type': 'text/plain;charset=UTF-8',
				'Postman-Token': '68cc02a1-4403-0c03-0e00-074e7b5eb866',
				}
	for gtype, raw_data in _dict.iteritems():
		print gtype
		rank = 0
		url = "http://hispaceclt1.hicloud.com:8080/hwmarket/api/storeApi2"
		try:
			r = requests.post(url, data=raw_data, headers=headers, timeout=10)
			if r.status_code == 200:
				j = r.json()
				if j['layoutData'] is not None and len(j['layoutData'])>=1:
					layoutData = j['layoutData']
					if len(layoutData) == 1:
						data_list = j['layoutData'][0]['dataList']
						if data_list is not None:
							for app in data_list:
								rank += 1
								game_name, img, downloads, size, popular, game_type, status, url = [u''] * 8
								game_name = app.get('name', u'')
								img = app.get('icon', u'')
								downloads = app.get('downCountDesc', u'')
								url = app.get('detailId', u'')
								size = app.get('size', u'')
								source = source_map.get(gtype)
								#print rank, game_name, source, downloads
								store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
					elif len(layoutData) >= 2:
						for item in layoutData:
							if item.get('dataList-type', 0) == 3:	
								for app in item['dataList']:
									rank += 1
									game_name, img, downloads, size, popular, game_type, status, url = [u''] * 8
									game_name = app.get('name', u'')
									img = app.get('icon', u'')
									downloads = app.get('downCountDesc', u'')
									url = app.get('detailId', u'')
									size = app.get('size', u'')
									source = source_map.get(gtype)
									#print rank, game_name, source, downloads
									store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
		except Exception, e:
			mylogger.error("get huawei game center app rank \t%s" % (traceback.format_exc()))

def get_app12345_app_rank():
	url = "http://www.app12345.com/?area=cn&store=Apple%20Store&device=iPhone&pop_id=27&showdate=2015-12-18&showtime=12&genre_id=6014"
	try:
		r = requests.get(url, timeout=10)
		rank = 0
		if r.status_code == 200:
			soup = BeautifulSoup(r.text)
			for dl in soup.find_all('dl', class_='dldefault'):
				dvimg = dl.find('div', class_='dvimg')
				if dvimg is not None:
					img_class = dvimg.find('img')
					if img_class is not None:
						rank += 1
						game_name, img, downloads, size, popular, game_type, status, url = [u''] * 8
						game_name = img_class.get('title')
						img = img_class.get('src')
						url = dvimg.find('a').get('href') if dvimg.find('a') is not None else u''
						source = source_map.get('app12345')
						store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
	except Exception, e:
		mylogger.error("app12345 ex %s" % traceback.format_exc())



def store_data(ret):
	rank, game_name, img, downloads, size, source, popular, game_type, status, url = ret
	dt = unicode(datetime.date.today())
	ins = db_conn.query(HotGames).filter(HotGames.name==game_name).filter(HotGames.source==source).filter(HotGames.dt==dt).filter(HotGames.rank==rank).first()
	if ins is None:
		item = HotGames(**{
						"name"			: game_name,
						"img"			: img,
						"download_count": downloads,
						"size"			: size,
						"source"		: source,
						"rank"			: rank,
						"popular"		: popular,
						"game_type"		: game_type,
						"status"		: 0,
						"url"			: url,
						"identifying"	: url,
						"dt"			: dt
						})
		db_conn.merge(item)
	db_conn.commit()

def main():
	get_baidu_hot_games()
	store_360_app_rank()
	store_m5qq_app_rank()
	store_m_baidu_app_rank()
	get_dangle_app_rank()
	store_xiaomi_web_rank()
	store_vivo_app_rank()
	store_gionee_app_rank()
	store_coolpad_app_rank()
	store_open_play_app_rank()
	store_wandoujia_app_rank()
	store_iqiyi_app_rank()
	store_youku_app_rank()
	store_sogou_app_rank()
	get_pp_app_rank()
	get_i4_app_rank()
	get_kuaiyong_app_rank()
	get_itools_app_rank()
	get_xyzs_app_rank()
	get_91play_app_rank()
	store_360_gamebox_app_rank()
	store_18183_top_app_rank()
	store_9game_web_app_rank()
	get_360zhushou_web_rank()
	store_xiaomi_app_rank()
	store_wogame_app_rank()
	get_tbzs_app_rank()
	get_lenovo_gamecenter_app_rank()
	get_lenovo_shop_rank()
	get_meizu_app_rank()
	get_wostore_app_rank()
	get_mmstore_app_rank()
	get_vivo_store_app_rank()
	get_myaora_app_rank()
	get_huawei_app_rank()
	get_app12345_app_rank()

if __name__ == '__main__':
	main()

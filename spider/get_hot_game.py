#!/usr/bin/env python
#encoding=utf-8

import sys
import requests
import json
import urllib
import traceback
import re
import sys
sys.path.append('/home/cyp/Utils/common')
from define import *
from model import *
from bs4 import BeautifulSoup
import time
import xmltodict

from get_logger import *
mylogger = get_logger('hot_game')

s = requests.session()
db_conn = new_session()


source_map = {
			"baidu"	: 0,
			"xiaomi_active": 1,
			"360"	: 2,
			"9game"	: 3,
			"9game_hot_wanted"	: 4,
			"360_app_single"	: 5,
			"360_app_webgame"	: 6,
			"360_app_new_game"	: 7,
			"m5_qq_single"	: 8,#应用宝
			"m5_qq_webgame"	: 9,#应用宝
			"m5_qq_new_game"	: 10,#应用宝
			"m_baidu_single"	: 11,
			"m_baidu_webgame"	: 12,
			"m_baidu_new_game"	: 13,
			"dangle_new_game"	: 14,
			"xiaomi_downloads"	: 15,
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
				}

def get_baidu_hot_games():
	url = "http://shouji.baidu.com/game"
	r = s.get(url)
	if r.status_code == 200:
		soup = BeautifulSoup(r.text)
		hot = soup.find("div", class_="sec-hot tophot")
		if hot is not None:
			for k in hot.find_all("li")[:]:
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
					yield game_name, img, downloads, size, source, popular, game_type, status, url

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


def get_xiaomi_app_rank(gtype, rank_id):
	rank = 0
	for page in xrange(5):
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

def store_xiaomi_app_rank():
	type_2_source = {
						"xiaomi_active": 12,
						"xiaomi_downloads": 3,
					}
	for gtype, rank_id in type_2_source.iteritems():
		for data in get_xiaomi_app_rank(gtype, rank_id):
			store_data(data)
		

def get_360_online_games():
	for page in xrange(1,4):
		r = s.get('http://zhushou.360.cn/list/index/cid/100451/order/download/?page=%s' % page)
		if r.status_code == 200:
			soup = BeautifulSoup(r.text)
			for i in soup.find("ul", class_="iconList").find_all("li"):
				popular 	= u""
				game_type 	= u""
				status 		= u""
				item = i.find('h3').find('a')
				url 		= u"http://zhushou.360.cn/detail/index/soft_id/%s" % item.get('sid')
				game_name = item.text
				img = i.find("a", sid="%s" % item.get("sid")).find("img").get("_src")
				downloads = i.find("span").text
				size 		= u""
				source 		= source_map.get("360")
				yield game_name, img, downloads, size, source, popular, game_type, status, url


def get_9game_new_wanted_list():
	r = s.get("http://www.9game.cn/xyqdb/")
	if r.status_code == 200:
		soup = BeautifulSoup(r.text)
		t = soup.find("div", class_="box-text").find("table").find_all("tr")
		for i in t[1:]:
			td_list = i.find_all("td")
			#print td_list
			rank = td_list[0].find("span").text
			title = td_list[1].find("a").get("title")
			url = u"http://www.9game.cn%s" % td_list[1].find("a").get("href")
			game_type = td_list[2].text.rstrip()
			status = td_list[3].text.strip()
			popular = td_list[4].text.strip()
			yield rank, title, url, game_type, status, popular


def get_9game_new_hot_list():
	r = s.get("http://www.9game.cn/xyrb/")
	if r.status_code == 200:
		soup = BeautifulSoup(r.text)
		t = soup.find("div", class_="box-text").find("table").find_all("tr")
		for i in t[1:]:
			td_list = i.find_all("td")
			#print td_list
			rank = td_list[0].find("span").text
			title = td_list[1].find("a").get("title")
			url = u"http://www.9game.cn%s" % td_list[1].find("a").get("href")
			game_type = td_list[2].text
			status = td_list[3].text
			popular = td_list[4].text
			yield rank, title, url, game_type, status, popular

def get_9game_detail():
	for i in get_9game_new_hot_list():
		rank, title, url, game_type, status, popular = i
		r = s.get(url)
		if r.status_code == 200:
			soup = BeautifulSoup(r.text)
			try:
				title_div = soup.find("div", class_="title")
				img_div = soup.find("div", class_="info").find("span", class_="img")
				if img_div is not None:
					img = img_div.find("img").get("src")
				elif soup.find("div", class_="info").find("img") is not None:
					img = soup.find("div", class_="info").find("img").get("src")
				else:
					img 		= u""
				if title_div is not None:
					game_name = title_div.text.strip()
				elif soup.find("div", class_="contain-title").find("div", class_="h-title") is not None:
					game_name = soup.find("div", class_="contain-title").find("div", class_="h-title").find('h1').text
				else:
					game_name = u""
				source = source_map.get('9game')
				downloads 	= popular
				size 		= u""
				yield game_name, img, downloads, size, source, popular, game_type, status, url
			except Exception,e:
				mylogger.error("%s\t%s" % (title, traceback.format_exc()))

def get_9game_detail2():
	for i in get_9game_new_wanted_list():
		rank, title, url, game_type, status, popular = i
		r = s.get(url)
		if r.status_code == 200:
			soup = BeautifulSoup(r.text)
			try:
				title_div = soup.find("div", class_="title")
				img_div = soup.find("div", class_="info").find("span", class_="img")
				if img_div is not None:
					img = img_div.find("img").get("src")
				elif soup.find("div", class_="info").find("img") is not None:
					img = soup.find("div", class_="info").find("img").get("src")
				else:
					img 		= u""
				if title_div is not None:
					game_name = title_div.text.strip()
				elif soup.find("div", class_="contain-title").find("div", class_="h-title") is not None:
					game_name = soup.find("div", class_="contain-title").find("div", class_="h-title").find('h1').text
				else:
					game_name = u""
				source = source_map.get('9game_hot_wanted')
				downloads 	= popular
				size 		= u""
				yield game_name, img, downloads, size, source, popular, game_type, status, url
			except Exception,e:
				mylogger.error("%s\t%s" % (title, traceback.format_exc()))

def get_9game_page_detail():
	r = s.get(url)
	if r.status_code == 200:
		soup = BeautifulSoup(r.text)
		try:
			pass
		except Exception,e:
			mylogger.error("%s" % (traceback.format_exc()))
	


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'}

def get_appannie_hot_list():
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
	for gtype in ['single', 'webgame', 'new']:
		mylogger.info("360 %s rank start... " % gtype)
		for data in get_360_app_rank(gtype):
			store_data(data)

def store_data(ret):
	rank, game_name, img, downloads, size, source, popular, game_type, status, url = ret
	ins = db_conn.query(HotGames).filter(HotGames.name==game_name).filter(HotGames.source==source).filter(HotGames.create_date==date.today()).first()
	if ins is None:
		item = HotGames(**{
						"name"			: game_name,
						"src"			: img,
						"download_count"		: downloads,
						"size"			: size,
						"source"		: source,
						"rank"			: rank,
						"popular"		: popular,
						"game_type"		: game_type,
						"status"		: status,
						"url"			: url
						})
		db_conn.merge(item)
	db_conn.commit()

def get_m5qq_app_rank(gtype):
	#应用宝
	rank = 0
	type_2_source = {
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
					url = u"%s\t%s" % (app.get('pkgName', u''),  app.get('appId', u''))
					source = source_map.get(type_2_source.get(gtype))
					yield rank, game_name, img, downloads, size, source, popular, game_type, status, url
	except Exception,e:
		mylogger.error("%s====>\t%s" % (_url, traceback.format_exc()))

def store_m5qq_app_rank():
	for gtype in ['18', '19', '20']:
		mylogger.info("get_m5qq_app_rank %s rank start... " % gtype)
		for data in get_m5qq_app_rank(gtype):
			store_data(data)


def get_m_baidu_rank(gtype, _url):
	rank = 0
	try:
		r = requests.get(_url, timeout=10)
		if r.status_code == 200:
			j = r.json()
			if 'result' in j and 'data' in j['result']:
				for item in j['result']['data']:
					if 'itemdata' in item:
						rank += 1
						app = item.get('itemdata', {})
						game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
						game_name = app.get('sname', u'')
						img = app.get('icon', u'')
						downloads = app.get('display_download', u'')
						size = app.get('size', u'')
						game_type = app.get('catename', u'')
						url = u"%s\t%s" % (app.get('package', u''),  app.get('docid', u''))
						source = source_map.get(gtype)
						yield rank, game_name, img, downloads, size, source, popular, game_type, status, url
						#for k, v in app.iteritems():
						#	print k, v
						#print 
	except Exception,e:
		mylogger.error("%s====>\t%s" % (_url, traceback.format_exc()))

def store_m_baidu_app_rank():
	single_url = 'http://m.baidu.com/appsrv?uid=YPvuu_PqvfgkiHf30uS88liwHulTiSiQYiHPfgiOB8qLuHf3_PvoigaX2ig5uBiN3dqqC&native_api=1&psize=3&abi=armeabi-v7a&cll=_hv19g8O2NAVA&usertype=0&is_support_webp=true&ver=16786356&from=1011454q&board_id=board_102_736&operator=460015&network=WF&pkname=com.dragon.android.pandaspace&country=CN&cen=cuid_cut_cua_uid&gms=false&platform_version_id=19&firstdoc=&name=game&action=ranklist&pu=cua%40_a-qi4uq-igBNE6lI5me6NIy2I_UC-I4juDpieLqA%2Cosname%40baiduappsearch%2Cctv%401%2Ccfrom%401010680f%2Ccuid%40YPvuu_PqvfgkiHf30uS88liwHulTiSiQYiHPfgiOB86QuviJ0O2lfguGv8_Huv8uja20fqqqB%2Ccut%405fXCirktSh_Uh2IJgNvHtyN6moi5pQqAC&language=zh&apn=&native_api=1&pn=0&f=gameranklist%40tab%401&bannert=26%4027%4028%4029%4030%4031%4032%4043'
	new_games_url = 'http://m.baidu.com/appsrv?uid=YPvuu_PqvfgkiHf30uS88liwHulTiSiQYiHPfgiOB8qLuHf3_PvoigaX2ig5uBiN3dqqC&native_api=1&psize=3&abi=armeabi-v7a&cll=_hv19g8O2NAVA&usertype=0&is_support_webp=true&ver=16786356&from=1011454q&board_id=board_102_737&operator=460015&network=WF&pkname=com.dragon.android.pandaspace&country=CN&cen=cuid_cut_cua_uid&gms=false&platform_version_id=19&firstdoc=&name=game&action=ranklist&pu=cua%40_a-qi4uq-igBNE6lI5me6NIy2I_UC-I4juDpieLqA%2Cosname%40baiduappsearch%2Cctv%401%2Ccfrom%401010680f%2Ccuid%40YPvuu_PqvfgkiHf30uS88liwHulTiSiQYiHPfgiOB86QuviJ0O2lfguGv8_Huv8uja20fqqqB%2Ccut%405fXCirktSh_Uh2IJgNvHtyN6moi5pQqAC&language=zh&apn=&&native_api=1&pn=0&f=gameranklist%40tab%403&bannert=26%4027%4028%4029%4030%4031%4032%4043'
	web_game_url = 'http://m.baidu.com/appsrv?uid=YPvuu_PqvfgkiHf30uS88liwHulTiSiQYiHPfgiOB8qLuHf3_PvoigaX2ig5uBiN3dqqC&native_api=1&psize=3&abi=armeabi-v7a&cll=_hv19g8O2NAVA&usertype=0&is_support_webp=true&ver=16786356&from=1011454q&board_id=board_102_735&operator=460015&network=WF&pkname=com.dragon.android.pandaspace&country=CN&cen=cuid_cut_cua_uid&gms=false&platform_version_id=19&firstdoc=&name=game&action=ranklist&pu=cua%40_a-qi4uq-igBNE6lI5me6NIy2I_UC-I4juDpieLqA%2Cosname%40baiduappsearch%2Cctv%401%2Ccfrom%401010680f%2Ccuid%40YPvuu_PqvfgkiHf30uS88liwHulTiSiQYiHPfgiOB86QuviJ0O2lfguGv8_Huv8uja20fqqqB%2Ccut%405fXCirktSh_Uh2IJgNvHtyN6moi5pQqAC&language=zh&apn=&&native_api=1&pn=0&f=gameranklist%40tab%402&bannert=26%4027%4028%4029%4030%4031%4032%4043'
	_dict = {'m_baidu_single': single_url, 'm_baidu_webgame': web_game_url, 'm_baidu_new_game': new_games_url}	
	for gtype, _url in _dict.iteritems():
		for data in get_m_baidu_rank(gtype, _url):
			store_data(data)
		
def get_dangle_app_rank():
	_url = 'http://api2014.digua.d.cn/newdiguaserver/game/rank?pn=1&type=16&ps=50'
	headers = {'HEAD': {"stamp":1448610575430,"verifyCode":"78492ba9e8569f3b9d9173ac4e4b6cb9","it":2,"resolutionWidth":1080,"imei":"865931027730878","clientChannelId":"100327","versionCode":750,"mac":"34:80:b3:4d:69:87","vender":"Qualcomm","vp":"","version":"7.5","sign":"2ec90f723384b1ec","dd":480,"sswdp":"360","hasRoot":0,"glEsVersion":196608,"device":"MI_4LTE","ss":2,"local":"zh_CN","language":"2","sdk":19,"resolutionHeight":1920,"osName":"4.4.4","gpu":"Adreno (TM) 330"}}
	rank = 0
	try:
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
					source = source_map.get('dangle_new_game')
					store_data((rank, game_name, img, downloads, size, source, popular, game_type, status, url))
	except Exception,e:
		mylogger.error("%s====>\t%s" % (_url, traceback.format_exc()))



def get_data(f):
	for i in enumerate(f()):
		rank, ret = i
		game_name, img, downloads, size, source, popular, game_type, status, url = ret
		ins = db_conn.query(HotGames).filter(HotGames.name==game_name).filter(HotGames.source==source).filter(HotGames.create_date==date.today()).first()
		if ins is None:
			item = HotGames(**{
							"name"			: game_name,
							"src"			: img,
							"download_count"		: downloads,
							"size"			: size,
							"source"		: source,
							"rank"			: rank+1,
							"popular"		: popular,
							"game_type"		: game_type,
							"status"		: status,
							"url"			: url
							})
			db_conn.merge(item)
	db_conn.commit()
	mylogger.info("%s done!" % f.__name__)


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
					url = u"%s\t%s" % (app.get('pkgName', u''),  app.get('id', u''))
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
						url = u"%s\t%s" % (app.get('package', u''),  app.get('gameid', u''))
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
		r = requests.post(_url, timeout=10, data=fd, headers=headers)
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
					url = u"%s\t%s" % (app.get('package_name', u''),  app.get('@rid', u''))
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

	_dict = {'open_play_download': download_page, 'open_play_free': free_page, 'open_play_webgame': webgame_page}	
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
	except Exception,e:
		r = T(404)
		mylogger.error("### %s ### %s" % (url.encode('utf-8'), traceback.format_exc()))
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
					for app in d['apps'][:1]:
						rank += 1
						game_name, img, downloads, size, source, popular, game_type, status, url = [u''] * 9
						game_name = app.get('name', u'')
						img = app.get('icon', u'')
						size = app.get('size', u'')
						downloads = app.get('cnt', u'')
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
					url = u"%s\t%s" % (app.get('packagename', u''),  app.get('appid', u''))
					yield rank, game_name, img, downloads, size, source, popular, game_type, status, url
					#for k,v in app.iteritems():
					#	print k,v
	except Exception,e:
		mylogger.error("%s====>\t%s" % (_url, traceback.format_exc()))


def store_sogou_app_rank():
	_dict = {"sogou_single": 'http://mobile.zhushou.sogou.com/android/rank/toplist.html?id=12&limit=25&group=2&start=0&iv=41&uid=f3c2ed94d7d2272de87a8ef3abab2409&vn=4.1.3&channel=baidu&sogouid=a7f30d60a6b1aed168a8c9d7c46bbac5&stoken==SnxL9KjGT6sBvQ7ZJD4Ghw&cellid=&sc=0', 'sogou_webgame': 'http://mobile.zhushou.sogou.com/android/rank/toplist.html?id=11&limit=25&group=2&start=0&iv=41&uid=f3c2ed94d7d2272de87a8ef3abab2409&vn=4.1.3&channel=baidu&sogouid=a7f30d60a6b1aed168a8c9d7c46bbac5&stoken==SnxL9KjGT6sBvQ7ZJD4Ghw&cellid=&sc=0'}
	for gtype, _url in _dict.iteritems():
		for data in get_sogou_app_rank(gtype, _url):
			store_data(data)

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
					img = app.get('icon', u'')
					size = app.get('size', u'')
					game_type = app.get('typeName', u'')
					downloads = app.get('downCount', u'')
					size = app.get('size', u'')
					source = source_map.get('i4_hot')
					url = u"%s\t%s" % (app.get('sourceId', u''),  app.get('itemId', u''))
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
					url = u"%s\t%s" % (app.get('buid', u''),  app.get('itemId', u''))
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
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		response = T(404)
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


def main():
	mylogger.info("holy shit!")
	get_data(get_baidu_hot_games)
	get_data(get_360_online_games)
	get_data(get_9game_detail)
	get_data(get_9game_detail2)
	store_360_app_rank()
	store_m5qq_app_rank()
	store_m_baidu_app_rank()
	get_dangle_app_rank()
	store_xiaomi_app_rank()
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

if __name__ == '__main__':
	main()

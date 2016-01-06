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

db_conn = new_session()
mylogger = get_logger('ad_raw_data')

from get_kc_list import source_map


#推荐位类型
#u"首页大图/大屏轮播图/banner"
#u"热门图标推荐"
#u"精品速递/专题推荐"
#u"榜单推荐"

def get_position_type_map():
	mydict = {}
	localIP = socket.gethostbyname(socket.gethostname())
	if localIP == u'192.168.1.215':
		conn = MySQLdb.connect(host="127.0.0.1", port=3307, user="root", passwd="dc@2013", db='new_publish_game', charset="utf8")
	else:
		conn = MySQLdb.connect(host="127.0.0.1", port=3306, user="root", passwd="admin", db='dataeye', charset="utf8")
	cursor = conn.cursor()
	cursor.execute("select * from position_type")
	for re in cursor.fetchall():
		id, name = re
		mydict[name] = id
	return mydict

position_type_map = get_position_type_map()


def get_data_from_api(url, timeout=10, headers={}, proxies={}, params={}):
	if isinstance(url, unicode):
		url = url.encode('utf-8')
	try:
		r = requests.get(url, timeout=timeout, params=params, headers=headers, proxies=proxies)
		if r.status_code == 200:
			return r.json()
	except Exception,e:
		mylogger.error("get jsondata from ### %s ### \n%s" % (url, traceback.format_exc()))
	return None

def get_page_source_from_web(url, timeout=10, headers={}, proxies={}):
	if isinstance(url, unicode):
		url = url.encode('utf-8')
	try:
		r = requests.get(url, timeout=timeout, headers=headers, proxies=proxies)
		if r.status_code == 200:
			return BeautifulSoup(r.text)
	except Exception,e:
		mylogger.error("get soup from ### %s ### \n%s" % (url, traceback.format_exc()))
	return None

def get_9game_raw_data():
	flags = [u"首页", u'新游推荐', u"发号专区", u"论坛"]
	urls = [u"http://www.9game.cn/", u"http://www.9game.cn/newgame/", u"http://ka.9game.cn/", u"http://bbs.9game.cn/"]
	
	soup = get_page_source_from_web("http://www.9game.cn/", timeout = 20)
	if soup is not None and soup:
		try:
			speard_con = soup.find('div',class_='box speard-con')
			if speard_con is not None:
				for app in speard_con.find_all('a'):
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					identifying = app.get('href')
					img_div = app.find('img')
					if img_div is not None:
						game_name = img_div.get('alt')
						picUrl = img_div.get('xlazyimg')
						if picUrl is not None and picUrl:
							game_id = insert_ad_game(game_name, picUrl)
							channel = source_map.get('9game')
							position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
							position_name = u'首页大图'
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))

			new_game_ul = soup.find('ul', class_='game-ul-list')
			if new_game_ul is not None:
				for li in new_game_ul.find_all('li'):
					app = li.find('a')
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					if app is not None:
						identifying = app.get('href')
						img_div = app.find('img')
						if img_div is not None:
							game_name = img_div.get('alt')
							picUrl = img_div.get('xlazyimg')
							if picUrl is not None and picUrl:
								game_id = insert_ad_game(game_name, picUrl)
								channel = source_map.get('9game')
								position_type_id = position_type_map.get(u'热门图标推荐')
								position_name = u'手机游戏推荐'
								insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
						
			suggest_game = soup.find('div', class_='suggest-con box')						
			if suggest_game is not None:
				for ul in suggest_game.find_all('ul', class_='game-ul-list'):
					for li in ul.find_all('li'):
						app = li.find('a')
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						if app is not None:
							identifying = app.get('href')
							img_div = app.find('img')
							if img_div is not None:
								game_name = img_div.get('alt')
								picUrl = img_div.get('xlazyimg')
								if picUrl is not None and picUrl:
									game_id = insert_ad_game(game_name, picUrl)
									channel = source_map.get('9game')
									position_type_id = position_type_map.get(u'热门图标推荐')
									position_name = u'游戏分类'
									insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())
				
def get_9game_newgame():
	soup = get_page_source_from_web("http://www.9game.cn/newgame/", timeout = 20)
	if soup is not None and soup:
		try:
			top_game_recom = soup.find('div',class_='box top-game-recom')
			if top_game_recom is not None:
				top_recom = top_game_recom.find('div', class_='top-recom')
				if top_recom is not None:
					for app in top_recom.find_all('a'):
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						identifying = app.get('href')
						game_name = app.get('title')
						if game_name is not None and game_name:
							game_id = insert_ad_game(game_name, picUrl)
							channel = source_map.get('9game')
							position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
							position_name = u'新游推荐'
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
				down_side = soup.find('ul', class_='down-side')
				if down_side is not None:
					for li in down_side.find_all('li'):
						app = li.find('a')
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						if app is not None:
							identifying = app.get('href')
							img_div = app.find('img')
							if img_div is not None:
								game_name = img_div.get('alt')
								picUrl = img_div.get('xlazyimg')
								if picUrl is not None and picUrl:
									game_id = insert_ad_game(game_name, picUrl)
									channel = source_map.get('9game')
									position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
									position_name = u'新游推荐'
									insert_ad_data((channel, position_type_id, position_name, game_id, identifying))

				focus_img = soup.find('ul', class_='focus-img')
				if focus_img is not None:
					for li in focus_img.find_all('li'):
						app = li.find('a')
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						if app is not None:
							identifying = app.get('href')
							img_div = app.find('img')
							if img_div is not None:
								game_name = img_div.get('alt')
								picUrl = img_div.get('src')
								if picUrl is not None and picUrl:
									game_id = insert_ad_game(game_name, picUrl)
									channel = source_map.get('9game')
									position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
									position_name = u'新游宣传图'
									insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())

def get_9game_ka():
	#异步加载, 暂未解决...
	soup = get_page_source_from_web("http://ka.9game.cn/", timeout=20)
	if soup is not None and soup:
		img_box = soup.find('div', class_='img-box')
		if img_box is not None:
			for app in img_box.find_all('a'):
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				identifying = app.get('href')
				img_div = app.find('img')
				if img_div is not None:
					game_name = img_div.get('alt')
					picUrl = img_div.get('src')
					channel = source_map.get('9game')
					position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
					position_name = u'发号宣传图'
					insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))

def get_9game_bbs():
	soup = get_page_source_from_web("http://bbs.9game.cn/", timeout=20)
	if soup is not None and soup:
		try:
			img_box = soup.find('p', id='top_change_img')
			if img_box is not None:
				for app in img_box.find_all('a'):
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					identifying = app.get('href')
					img_div = app.find('img')
					if img_div is not None:
						game_name = img_div.get('alt')
						picUrl = img_div.get('src')
						if picUrl is not None and picUrl:
							game_id = insert_ad_game(game_name, picUrl)
							channel = source_map.get('9game')
							position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
							position_name = u'论坛宣传图'
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
			category_3 = soup.find('div', id='category_3')
			if category_3 is not None:
				for td in category_3.find_all('td'):
					icon_nor = td.find('div', class_='icon-nor')
					if icon_nor is not None:
						app = icon_nor.find('a')
						if app is not None:
							identifying = app.get('href')
							img_div = app.find('img')
							if img_div is not None:
								game_name = img_div.get('alt')
								picUrl = img_div.get('src')
								if picUrl is not None and picUrl:
									game_id = insert_ad_game(game_name, picUrl)
									channel = source_map.get('9game')
									position_type_id = position_type_map.get(u'精品速递/专题推荐')
									position_name = u'论坛新游推荐专区'
									insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
			category_1 = soup.find('div', id='category_1')
			if category_1 is not None:
				for td in category_1.find_all('td'):
					icon_nor = td.find('div', class_='icon-nor')
					if icon_nor is not None:
						app = icon_nor.find('a')
						if app is not None:
							identifying = app.get('href')
							img_div = app.find('img')
							if img_div is not None:
								game_name = img_div.get('alt')
								picUrl = img_div.get('src')
								if picUrl is not None and picUrl:
									game_id = insert_ad_game(game_name, picUrl)
									channel = source_map.get('9game')
									position_type_id = position_type_map.get(u'精品速递/专题推荐')
									position_name = u'热门游戏专区'
									insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())
						


def get_appicsh_raw_data():
	flags = [u"应用宝-banner", u"应用宝-礼包", u"应用宝-精品推荐", u"应用宝-新游推荐", u"应用宝-热门网游", u"应用宝-热门单机", u"应用宝-每日精选"]
	urls = [u"http://m5.qq.com/app/banner.htm?sceneId=1", u"http://m5.qq.com/app/getgifboxtips.htm?sceneId=0", u"http://m5.qq.com/app/groupapps.htm?type=4&pageSize=30&cardId=2", u"http://m5.qq.com/app/applist.htm?listType=0&pageSize=10", u"http://m5.qq.com/app/applist.htm?listType=1&pageSize=15", u"http://m5.qq.com/app/applist.htm?listType=2&pageSize=15", u"http://m5.qq.com/app/banner.htm?sceneId=0"]

	j = get_data_from_api("http://m5.qq.com/app/banner.htm?sceneId=1")

	if j is not None and j:
		try:
			for br in j['obj']['bigBanners']:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = br.get('picUrl', u'')
				if picUrl:
					info = br.get('app', {})
					game_name = info.get('appName', u'')
					game_id = insert_ad_game(game_name, picUrl)
					identifying = info.get('pkgName', u'')
					position_name = u'游戏精选大图'
					position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
					channel = source_map.get('appicsh')
					insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
			for br in j['obj']['smallBanners']:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				info = br['app']
				if info is not None:
					picUrl = info.get('picUrl', u'')
					if picUrl:
						game_name = info.get('appName', u'')
						game_id = insert_ad_game(game_id, picUrl)
						identifying = info.get('pkgName', u'')
						position_name = u'游戏精选每日推荐'
						position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
						channel = source_map.get('appicsh')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception, e:
			mylogger.error(traceback.format_exc())

	j = get_data_from_api("http://m5.qq.com/app/banner.htm?sceneId=0")
	if j is not None and j:
		try:
			for br in j['obj']['bigBanners']:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = br.get('picUrl', u'')
				if picUrl:
					info = br.get('app', {})
					game_name = info.get('appName', u'')
					game_id = insert_ad_game(game_name, picUrl)
					identifying = info.get('pkgName', u'')
					position_name = u'每日游戏精选大图'
					position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
					channel = source_map.get('appicsh')
					insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
			for br in j['obj']['smallBanners']:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				info = br['app']
				if info is not None:
					picUrl = info.get('picUrl', u'')
					if picUrl:
						game_name = info.get('appName', u'')
						game_id = insert_ad_game(game_name, picUrl)
						identifying = info.get('pkgName', u'')
						position_name = u'游戏精选每日推荐'
						position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
						channel = source_map.get('appicsh')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception, e:
			mylogger.error(traceback.format_exc())


	j = get_data_from_api("http://m5.qq.com/app/getgifboxtips.htm?sceneId=0")
	if j is not None and j:
		try:
			for br in j['obj']['tipsList']:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				info = br['appInfo']
				if info is not None:
					picUrl = info.get('iconUrl', u'')
					if picUrl:
						game_name = info.get('appName', u'')
						game_id = insert_ad_game(game_name, picUrl)
						identifying = info.get('pkgName', u'')
						position_name = u'礼包中心弹出广告'
						position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
						channel = source_map.get('appicsh')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception, e:
			mylogger.error(traceback.format_exc())


	flags = [u"新游推荐", u"热门网游", u"热门单机"]
	urls = [u"http://m5.qq.com/app/applist.htm?listType=0&pageSize=10", u"http://m5.qq.com/app/applist.htm?listType=1&pageSize=15", u"http://m5.qq.com/app/applist.htm?listType=2&pageSize=15"]
	for i in xrange(3):
		url = urls[i]
		j = get_data_from_api(url, timeout=20)
		if j is not None and j:
			try:
				for app in j['obj']['appList']:
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = app.get('iconUrl', u'')
					if picUrl:
						game_name = app.get('appName', u'')
						game_id = insert_ad_game(game_name, picUrl)
						identifying = app.get('pkgName', u'')
						position_name = flags[i]
						position_type_id = position_type_map.get(u'精品速递/专题推荐')
						channel = source_map.get('appicsh')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
			except Exception, e:
				mylogger.error(traceback.format_exc())


	j = get_data_from_api("http://m5.qq.com/app/groupapps.htm?type=4&pageSize=30&cardId=2")
	if j is not None and j:
		try:
			for group in j['obj']['groupList']:
				if group.get('groupName', u'') == u"精品推荐":
					for app in group['appList']:
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						picUrl = app.get('iconUrl', u'')
						if picUrl:
							game_name = app.get('appName', u'')
							game_id = insert_ad_game(game_name, picUrl)
							identifying = app.get('pkgName', u'')
							position_name = u'精品推荐'
							position_type_id = position_type_map.get(u'精品速递/专题推荐')
							channel = source_map.get('appicsh')
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception, e:
			mylogger.error(traceback.format_exc())

def get_360gamebox_raw_data():
	flags = [u"首页精选", u"新游推荐"]
	j = get_data_from_api('http://next.gamebox.360.cn/7/xgamebox/dashboardex?jdata=1450946296&bir=2&nonce=f5ace931-1c70-4018-acae-144065f7ad7a&clienttype=gameunion&v=41611&ch=100100&sk=19&md=mi+4lte&m1=72db07100fc223a2ede82f4a44ae96b4&m2=881f853779fe69ad88926d8ac5ec4930&nt=1&rkey=qe1QeJMtttWAwKjMNmz1sUGKvUW9hZcRPYCJlc0u0SAlJbOan9R3ZYbH%2BREB1MvA1nj%2Bmnc9IQJ%2BY8fhrbWNmEGzCapRZN3SI15iNDTdK2cGmxlvYxuOZkVattKui2NB4nfj4wfphYdIf3VpMfh8Hak1WKmszbBPO0hpBiBBhG8%3D&signid=x9vKfiKUGm%2F9twXAVCCFSVoIB0hHXf5053BA5B6bwzPAgVlvmily9g%3D%3D%0A')
	if j is not None:
		try:
			for br in j['data']['topic']['list']:
				title = br.get('title', u'')
				if title in [u'必玩的精品网游', u'口碑游戏', u'优秀新游戏']:
					banner = br.get('banner')
					if banner is not None:
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						picUrl = banner.get('logo', u'')
						if picUrl:
							info = banner.get('game',{})
							game_name = info.get('name', u'')
							game_id = insert_ad_game(game_name, picUrl)
							position_name = u'图标推荐' 
							position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
							channel = source_map.get('360_gamebox')
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
					gamelist = br['games']
					if gamelist is not None:
						for game in gamelist:
							channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
							picUrl = game.get('logo_url', u'')
							if picUrl:
								game_name = game.get('name', u'')
								game_id = insert_ad_game(game_name, picUrl)
								position_name = title 
								position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
								channel = source_map.get('360_gamebox')
								insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())

	j = get_data_from_api('http://next.gamebox.360.cn/7/xgamebox/newgame?nonce=7dd27e13-94c9-4ff0-889e-24df08880a43&clienttype=gameunion&v=41611&ch=100100&sk=19&md=mi+4lte&m1=72db07100fc223a2ede82f4a44ae96b4&m2=881f853779fe69ad88926d8ac5ec4930&nt=1&rkey=fs3KwB%2BEBQjaurPvRWJ3TmorukDpHgCGeh0XMgCibwlCPCJdgBnpEEddl7X6aL7YljJqhjcboCWhIKIkJl%2BYyFkEYJxDJRE%2BIGTMg6lEzPs5FRWJHzIKdfeWmJDrxJBAYi%2BSgNS2Z0ATaufVe1buU0L4bjATNb2NsRtQQmig8ms%3D&signid=PbtzCFU9AFQv6b081FU7zFQEruUM1ZyNDSCS6A8ihkKn2cydBwJJfw%3D%3D%0A')
	if j is not None:
		try:
			for k, v in j['data'].iteritems():
				if k == 'zone':
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = v.get('bg', u'')
					if picUrl:
						game_id = insert_ad_game(game_name, picUrl)
						position_name = u'首页大图'
						position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
						channel = source_map.get('360_gamebox')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
				if k == 'newgame':
					for game in v['games']:	
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						picUrl = game.get('logo_url', u'')
						if picUrl:
							game_name = game.get('name', u'')
							game_id = insert_ad_game(game_name, picUrl)
							position_name = u'新游关注榜' 
							position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
							channel = source_map.get('360_gamebox')
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
				if k == 'ontest':
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = v.get('bg', u'')
					if picUrl:
						game_id = insert_ad_game(game_name, picUrl)
						position_name = u'图标推荐'
						position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
						channel = source_map.get('360_gamebox')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))

					if v['games']  is not None:	
						for game in v['games']:	
							channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
							picUrl = game.get('logo_url', u'')
							if picUrl:
								game_name = game.get('name', u'')
								game_id = insert_ad_game(game_name, picUrl)
								position_name = u'最近开测'
								position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
								channel = source_map.get('360_gamebox')
								insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())


def get_360zhushou_app_ad():
	prefix = u"http://125.88.193.234/AppStore/getRecomendAppsBytype?type=2&s_3pk=1&os=22&vc=300030515&withext=1&model=m2+note&sn=4.589389937671455&cu=mt6753&ca1=armeabi-v7a&ca2=armeabi&&se=1920x1080&webp=1&fm=gm001&m=13389b498494c1230fab6b4c04572848&s_stream_app=1&m2=1680ae9efad81fb51224ec048d296b6a&v=3.5.15&re=1&nt=1&ch=100130&ppi=1080x1920&cpc=1&startCount=0&snt=-1&timestamp=1450431524724"
	for page in xrange(1, 3):
		url = prefix + "&page=%s" % page
		j = get_data_from_api(url)
		try:
			if j is not None:
				for data in j['data']:
					if 'category' in data:
						for br in data['category']:
							channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
							game_name = br.get('name', u'')
							if game_name:
								picUrl = br.get('soft_large_logo_url', u'')
							else:
								picUrl = br.get('image_url_704_244', u'')
							if picUrl:
								game_id = insert_ad_game(game_name, picUrl)
								channel = source_map.get('360zhushou')
								position_name = u'首页大图'
								position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
								insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
				for card in j['card_list']:
					title = card.get('name', u'')
					if title == u'每日单机':
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						picUrl = card.get('banner', u'')
						if picUrl:
							game_id = insert_ad_game(game_name, picUrl)
							channel = source_map.get('360zhushou')
							position_name = title
							position_type_id = position_type_map.get(u'热门图标推荐')
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
						for game in card['apps']:
							channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
							picUrl = game.get('logo_url', u'')
							if picUrl:
								game_name = game.get('name', u'')
								game_id = insert_ad_game(game_name, picUrl)
								position_name = title
								position_type_id = position_type_map.get(u'热门图标推荐')
								channel = source_map.get('360zhushou')
								insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
			
					if title == u'新游预约':
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						picUrl = card.get('banner', u'')
						if picUrl:
							game_id = insert_ad_game(game_name, picUrl)
							channel = source_map.get('360zhushou')
							position_name = title
							position_type_id = position_type_map.get(u'热门图标推荐')
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
						for game in card['apps']:
							channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
							picUrl = game.get('logo_url', u'')
							if picUrl:
								game_name = game.get('name', u'')
								game_id = insert_ad_game(game_name, picUrl)
								position_name = title
								position_type_id = position_type_map.get(u'热门图标推荐')
								channel = source_map.get('360zhushou')
								insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
						for game in card['reserves']:
							channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
							picUrl = game.get('logo_url', u'')
							if picUrl:
								game_name = game.get('name', u'')
								game_id = insert_ad_game(game_name, picUrl)
								position_name = title
								position_type_id = position_type_map.get(u'热门图标推荐')
								channel = source_map.get('360zhushou')
								insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())
			
		
def get_360zhushou_web_ad():
	#360手机助手PC官网
	url = "http://zhushou.360.cn/Game/"
	soup = get_page_source_from_web(url, timeout=30)
	if soup is not None and soup:
		try:
			slideCon = soup.find('div', class_='slideCon')
			if slideCon is not None:
				for br in slideCon.find_all('a'):
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					img_div = br.find('img')
					if img_div is not None:
						game_name = img_div.get('alt')
						picUrl = img_div.get('src')
						if picUrl:
							game_id = insert_ad_game(game_name, picUrl)
							position_name = u'首页大图'
							position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
							channel = source_map.get('360zhushou_web')
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
			mrit = soup.find('div', class_='fr mrit')
			if mrit is not None:
				scripts = mrit.find_all('script')
				if len(scripts) == 3:
					tpcdata = scripts[2].text
					names= re.findall(u"title : '([\u4e00-\u9fa5\S]+)'", tpcdata)
					icons= re.findall(u"sicon : '([\S]+)'", tpcdata)
					if len(names) == len(icons):
						for i in xrange(len(names)):
							channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
							game_name = names[i]
							picUrl = icons[i]
							game_id = insert_ad_game(game_name, picUrl)
							position_name = u'首页大图'
							position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
							channel = source_map.get('360zhushou_web')
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
			ctcon = soup.find('div', class_='ctcon')
			if ctcon is not None:
				ul = ctcon.find('ul', class_='sty1')
				if ul is not None:
					for li in ul.find_all('li'):
						channel, position_type_id, position_name, picUrl, game_id, identifying = [u''] * 6
						infos = li.find_all('a')
						if len(infos) == 2:
							game_info = infos[1]
							href =  game_info.get('href')
							for param in re.split('&', href):
								segs = param.split('=')
								if len(segs) == 2:
									if segs[0] == 'name':
										game_name = segs[1]
						app = li.find('a')
						if app is not None:
							img_div = app.find('img')
							if img_div is not None:
								picUrl = img_div.get('src')
								if picUrl is not None and picUrl:
									game_id = insert_ad_game(game_name, picUrl)
									position_name = u'精品推荐'
									position_type_id = position_type_map.get(u'热门图标推荐')
									channel = source_map.get('360zhushou_web')
									insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())

def get_mmstore_ad():
	#游戏 推荐
	url = "http://odp.mmarket.com/t.do?requestid=json_hot_recommend_game_library"
	headers = {
				"appname": "MM5.3.0.001.01_CTAndroid_JT", 
				"ua":"android-19-720x1280-CHE2-UL00"}
	j = get_data_from_api(url, headers=headers, timeout=30)
	if j is not None:
		try:
			for item in j['cards']:
				for adv in item['advs']:
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					game_name = adv.get('slogan', u'')
					picUrl = adv.get('picurl', u'')
					if picUrl:
						position_name = u'首页大图'
						game_id = insert_ad_game(game_name, picUrl)
						position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
						channel = source_map.get('mmstore')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())
		
	for i in xrange(1,7):
		url = "http://odp.mmarket.com/t.do?requestid=android_mm5.0_index&pktype=mmindex&adKey=adList_MM5_AD_CATEGORY&outputWay=list&currentPage=%s&totalRows=33" % i
		j = get_data_from_api(url, headers=headers, timeout=30)
		try:
			if j is not None:
				for item in j['cards']:
					title = item.get('title', u'')
					if title in [u'热门游戏', u'精选单机', u'天天有奖', u'新游试玩']:
						for game in item['items']:
							channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
							game_name = game.get('name', u'')
							picUrl = game.get('iconUrl', u'')
							if picUrl:
								game_id = insert_ad_game(game_name, picUrl)
								position_name = title
								position_type_id = position_type_map.get(u'热门图标推荐')
								channel = source_map.get('mmstore')
								insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
					if 'advs' in item:
						for adv in item['advs']:
							channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
							picUrl = adv.get('picurl', u'')
							game_name = adv.get('slogan', u'')
							if picUrl:
								game_id = insert_ad_game(game_name, picUrl)
								position_name = u'首页大图'
								position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
								channel = source_map.get('mmstore')
								insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())


def get_open_play_ad():
	url = "http://open.play.cn/api/v2/mobile/channel/content.json?channel_id=728&terminal_id=18166&current_page=0&rows_of_page=1"
	j = get_data_from_api(url)
	if j is not None:
		try:
			if j['code'] == 0:
				sub_channel = j['ext']['main']['content']['sub_channel']
				if len(sub_channel) >= 1:
					channel = sub_channel[0]
					adv_url = channel['game_list'][0]['image_detail']['link_url']
					ad_data =  get_data_from_api(adv_url)
					if ad_data is not None:
						for item in ad_data['ext']['main']['content']['game_list']:
							channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
							image_detail = item.get('image_detail')
							if image_detail is not None:
								picUrl = image_detail.get('img_url', u'')
								if picUrl:
									game_id = insert_ad_game(game_name, picUrl)
									position_name = u'首页大图'
									position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
									channel = source_map.get('open_play')
									insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
							game_detail = item.get('game_detail')
							if game_detail is not None:
								game_name = game_detail.get('game_name', u'')
								picUrl = game_detail.get('game_icon', u'')
								if picUrl:
									game_id = insert_ad_game(game_name, picUrl)
									position_name = u'游戏推荐'
									position_type_id = position_type_map.get(u'热门图标推荐')
									channel = source_map.get('open_play')
									insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())
							
	#网游频道banner	
	url = "http://open.play.cn/api/v2/mobile/channel/version/show_advs.json?channel_id=762&terminal_id=18166&vc=770"
	j = get_data_from_api(url)
	if j is not None:
		try:
			if j['code'] == 0:
				for adv in j['ext'][0]['detail_list']:
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = adv.get('img_url', u'')
					if picUrl:
						game_id = insert_ad_game(game_name, picUrl)
						position_name = u'大屏轮播图'
						position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
						channel = source_map.get('open_play')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())
		
	#必玩
	url = "http://open.play.cn/api/v2/mobile/channel/content.json?channel_id=1807&terminal_id=18166&current_page=0&rows_of_page=20&order_id=0"
	j = get_data_from_api(url)
	if j is not None:
		try:
			if j['code'] == 0:
				for d in ad_data['ext']['main']['content']['game_list']:
					if d['game_detail'] is not None:
						
						item = d['game_detail']
						if item is not None:
							channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
							picUrl = item.get('game_icon', u'')
							if picUrl:
								game_name = item.get('game_name')
								game_id = insert_ad_game(game_name, picUrl)
								position_name = u'必玩'
								position_type_id = position_type_map.get(u'热门图标推荐')
								channel = source_map.get('open_play')
								insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())

def get_wostore_ad():
	headers = {"phoneAccessMode": "3",
				"version": "android_v5.0.3",
				"handphone": "00000000000"}
	#必玩顶部广告
	url = "http://clientnew.wostore.cn:6106/appstore_agent/unistore/servicedata.do?serviceid=ADListNew&channel=1"
	j = get_data_from_api(url, headers=headers)
	if j is not None and j['RANKINGAPP'] is not None:
		try:
			for app in j.get('RANKINGAPP', []):
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = app.get('appIconURL', u'')
				if picUrl:
					game_name = app.get('appName', u'')
					game_id = insert_ad_game(game_name, picUrl)
					position_name = u'首页大图'
					position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
					channel = source_map.get('wostore')
					insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())

	#必玩
	for p in xrange(1, 6):
		url = "http://clientnew.wostore.cn:6106/appstore_agent/unistore/servicedata.do?serviceid=appList&channel=18&pageNum=%s&count=20" % p
		j = get_data_from_api(url, headers=headers)
		try:
			if j is not None and j['WOSTORE'] is not None:
				for d in j.get('WOSTORE',[]):
					if d.get('appType', -1) == 6:
						for g in d.get('appArray', []):
							picUrl = g.get('iconURL', u'')
							if picUrl:
								game_name = g.get('appName', u'')
								game_id = insert_ad_game(game_name, picUrl)
								position_name = u'图标推荐'
								position_type_id = position_type_map.get(u'热门图标推荐')
								channel = source_map.get('wostore')
								insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
					if d.get('isBigPic', -1) == u'1':
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						picUrl = d.get('iconURL', u'')
						if picUrl:
							game_name = d.get('appName', u'')
							game_id = insert_ad_game(game_name, picUrl)
							position_name = u'首页大图'
							position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
							channel = source_map.get('wostore')
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())

	#礼包频道
	for p in xrange(1,5):
		url = "http://clientnew.wostore.cn:6106/appstore_agent/unistore/servicedata.do?serviceid=appList&channel=19&categoryID=0&pageNum=%s&count=20" % p
		j = get_data_from_api(url, headers=headers)
		try:
			if j is not None and j['WOSTORE'] is not None:
				for d in j['WOSTORE']:
					if d.get('isBigPic', -1) == u'1':
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						picUrl = d.get('iconURL', u'')
						if picUrl:
							game_name = d.get('appName', u'')
							game_id = insert_ad_game(game_name, picUrl)
							position_name = u'首页大图'
							position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
							channel = source_map.get('wostore')
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())
	

def get_wogame_ad():
	
	headers = {
				"phoneAccessMode": "3",
				"imei": "865931027730878",
				"IP": "", 
				"networkOperator": "4",
				"UUID": "97fed435-aef3-4acf-aa06-0ac3be255723",
				"channel_id": "12243",
				"version_code": "20151117",
				"If-Modified-Since": "Fri, 25 Dec 2015 06:29:37 GMT+00:00",
				"phone_num": "18565778352",
				"wogame_version": "20151117",
				"user_id": "8910319542245213232",
				"imsi": "460015776509846",
				"phone_model": "MI 4LTE",
				"User-Agent": "Dalvik/1.6.0 (Linux; U; Android 4.4.4; MI 4LTE MIUI/V7.0.5.0.KXDCNCI)"
				}

	#banner
	url = "http://wogame4.wostore.cn/wogame/getBannerList.do"
	j = get_data_from_api(url, headers=headers)
	if j is not None and j['banners'] is not None:
		try:
			for br in j['banners']:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = br.get('banner_url', u'')
				if picUrl:
					game_name = br.get('title', u'')
					game_id = insert_ad_game(game_name, picUrl)
					position_name = u'大屏轮播图'
					position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
					channel = source_map.get('wogame')
					insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())
	

	#首页
	url = "http://wogame4.wostore.cn/wogame/initialize.do"
	j = get_data_from_api(url, headers=headers)
	if j is not None:
		try:
			for tp in j['data']['template']:
				title = tp.get('name', u'')
				load_url = tp.get('load_url')
				if title in [u'推荐网游', u'猜你喜欢', u'精选单机']:
					detail_url = "http://wogame4.wostore.cn/wogame%s" % load_url
					j = get_data_from_api(detail_url, headers=headers)
					if j is not None:
						for game in j['data']:
							channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
							picUrl = game.get('icon_url', u'')
							if picUrl:
								game_name = game.get('game_name', u'')
								game_id = insert_ad_game(game_name, picUrl)
								position_name = title
								position_type_id = position_type_map.get(u'热门图标推荐')
								channel = source_map.get('wogame')
								insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
				if title == u'光棍福利大派送':
					detail_url = "http://wogame4.wostore.cn/wogame%s" % load_url
					j = get_data_from_api(detail_url, headers=headers)
					if j is not None:
						for game in j['data']:
							channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
							picUrl = game.get('banner_url', u'')
							if picUrl:
								game_name = game.get('game_name', u'')
								game_id = insert_ad_game(game_name, picUrl)
								position_name = title
								position_type_id = position_type_map.get(u'热门图标推荐')
								channel = source_map.get('wogame')
								insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
				if title == u'最IN网游':
					detail_url = "http://wogame4.wostore.cn/wogame%s" % load_url
					j = get_data_from_api(detail_url, headers=headers)
					if j is not None:
						for item in j['data']:
							game = item['game']
							channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
							picUrl = game.get('banner_url', u'')
							if picUrl:
								game_name = game.get('game_name', u'')
								game_id = insert_ad_game(game_name, picUrl)
								position_name = title
								position_type_id = position_type_map.get(u'热门图标推荐')
								channel = source_map.get('wogame')
								insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())

	#礼包
	url = "http://wogame4.wostore.cn/wogame/interestGifts.do?jsondata=%7B%22data%22%3A%5B%22-20151117%22%5D%7D"
	j = get_data_from_api(url, headers=headers)
	if j is not None and j['data'] is not None:
		try:
			for item in j['data']:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				br = item['game']
				picUrl = br.get('icon_url', u'')
				if picUrl:
					game_name = br.get('game_name', u'')
					game_id = insert_ad_game(game_name, picUrl)
					position_name = u'你可能感兴趣的礼包'
					position_type_id = position_type_map.get(u'热门图标推荐')
					channel = source_map.get('wogame')
						
					insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())
	
def get_oppo_ad():
	#单机
	single_url = "https://igame.oppomobile.com/gameapp/game/single"
	#网游
	online_url = "https://igame.oppomobile.com/gameapp/game/online"
	headers = {'sign':'', 'param':'imei=868008021943653&model=Che2-UL00&osversion=19'}
	md5_suffix = 'MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBANYFY/UJGSzhIhpx6YM5KJ9yRHc7YeURxzb9tDvJvMfENHlnP3DtVkOIjERbpsSd76fjtZnMWY60TpGLGyrNkvuV40L15JQhHAo9yURpPQoI0eg3SLFmTEI/MUiPRCwfwYf2deqKKlsmMSysYYHX9JiGzQuWiYZaawxprSuiqDGvAgMBAAECgYEAtQ0QV00gGABISljNMy5aeDBBTSBWG2OjxJhxLRbndZM81OsMFysgC7dq+bUS6ke1YrDWgsoFhRxxTtx/2gDYciGp/c/h0Td5pGw7T9W6zo2xWI5oh1WyTnn0Xj17O9CmOk4fFDpJ6bapL+fyDy7gkEUChJ9+p66WSAlsfUhJ2TECQQD5sFWMGE2IiEuz4fIPaDrNSTHeFQQr/ZpZ7VzB2tcG7GyZRx5YORbZmX1jR7l3H4F98MgqCGs88w6FKnCpxDK3AkEA225CphAcfyiH0ShlZxEXBgIYt3V8nQuc/g2KJtiV6eeFkxmOMHbVTPGkARvt5VoPYEjwPTg43oqTDJVtlWagyQJBAOvEeJLno9aHNExvznyD4/pR4hec6qqLNgMyIYMfHCl6d3UodVvC1HO1/nMPl+4GvuRnxuoBtxj/PTe7AlUbYPMCQQDOkf4sVv58tqslO+I6JNyHy3F5RCELtuMUR6rG5x46FLqqwGQbO8ORq+m5IZHTV/Uhr4h6GXNwDQRh1EpVW0gBAkAp/v3tPI1riz6UuG0I6uf5er26yl5evPyPrjrD299L4Qy/1EIunayC7JYcSGlR01+EDYYgwUkec+QgrRC/NstV'
	import md5
	md5_str = headers.get('param') + md5_suffix
	hash = md5.new()
	hash.update(md5_str)
	headers['sign'] =  hash.hexdigest()
	for url in [single_url, online_url]:
		j = get_data_from_api(url, headers=headers)
		if j is not None:
			if 'banners' in j:
				brs = j['banners']
			else:
				brs = j['bannerList']
			if brs is not None:
				for br in brs:
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = br.get('showPicUrl', u'')
					if picUrl:
						game_name = br.get('showText', u'')
						game_name = u'' if game_name is None else game_name
						game_id = insert_ad_game(game_name, picUrl)
						position_name = u'首页大图'
						position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
						channel = source_map.get('oppo_app')
							
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))

	#首页
	url = "https://igame.oppomobile.com/gameapp/game/index"
	j = get_data_from_api(url, headers=headers)
	if j is not None and j['bigBannerList'] is not None:
		for game in j['bigBannerList']:
			channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
			picUrl = game.get('showPicUrl', u'')
			if picUrl:
				game_name = game.get('showText', u'')
				game_name = u'' if game_name is None else game_name
				game_id = insert_ad_game(game_name, picUrl)
				position_name = u'大屏轮播图'
				position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
				channel = source_map.get('oppo_app')
				print position_name, game_name, '****'
				insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		if len(j['gameList']) >= 1:
			channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
			game = j['gameList'][0]
			picUrl = game.get('gameIcon', u'')
			if picUrl:
				game_name = game.get('gameName', u'')
				game_id = insert_ad_game(game_name, picUrl)
				position_name = u'每日一荐'
				position_type_id = position_type_map.get(u'热门图标推荐')
				channel = source_map.get('oppo_app')
				insert_ad_data((channel, position_type_id, position_name, game_id, identifying))


	#新游热度榜
	url = "https://igame.oppomobile.com/gameapp/newGame/recommend?start=0"
	md5_str = headers.get('param') + "&start=0" + md5_suffix
	hash = md5.new()
	hash.update(md5_str)
	headers['sign'] =  hash.hexdigest()
	j = get_data_from_api(url, headers=headers)
	if j is not None:
		try:
			if 'rankUnit' in j:
				for game in j['rankUnit']['gameList']:
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = game.get('gameIcon', u'')
					if picUrl:
						game_name = game.get('gameName', u'')
						game_id = insert_ad_game(game_name, picUrl)
						position_name = u'新游热度榜'
						position_type_id = position_type_map.get(u'精品速递/专题推荐')
						channel = source_map.get('oppo_app')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())

def get_vivo_gamecenter_ad():

	#首页banner
	url = "http://main.gamecenter.vivo.com.cn/clientRequest/recommendTop?appVersionName=2.0.0&adrVerName=4.4.4&model=MI+4LTE&e=11010030313647453200da18b1312200&pixel=3.0&appVersion=37&elapsedtime=352889163&imei=865931027730878&origin=20&type=top&av=19&patch_sup=1&cs=0&s=2%7C2434573514"
	j = get_data_from_api(url)
	if j is not None and j['adinfo'] is not None:
		try:
			for ad in j['adinfo']:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = ad.get('picUrl', u'')
				game_name = ad.get('showText', u'')
				game_name = u'' if game_name is None else game_name
				game_id = insert_ad_game(game_name, picUrl)
				position_name = u'大屏轮播图'
				position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
				channel = source_map.get('vivo')
				insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())

	#首页详情
	url = "http://main.gamecenter.vivo.com.cn/clientRequest/recommendBottomList?appVersionName=2.0.0&model=MI+4LTE&e=11010030313647453200da18b1312200&page_index=1&pixel=3.0&imei=865931027730878&origin=20&type=list&av=19&patch_sup=1&cs=0&adrVerName=4.4.4&appVersion=37&elapsedtime=352889173&s=2%7C2094637094"
	j = get_data_from_api(url)
	if j is not None:
		try:
			for game in j['app'][:4]:
				#每日一荐
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = game.get('icon', u'')
				game_name = game.get('name', u'')
				game_id = insert_ad_game(game_name, picUrl)
				position_name = u'每日一荐'
				position_type_id = position_type_map.get(u'热门图标推荐')
				channel = source_map.get('vivo')
				insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
			for item in j['module']:
				if item.get('title') == u'小编推荐':
					for game in item['msg']:
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						picUrl = game.get('icon', u'')
						if picUrl:
							game_name = game.get('name', u'')
							game_id = insert_ad_game(game_name, picUrl)
							position_name = item.get('title')
							position_type_id = position_type_map.get(u'热门图标推荐')
							channel = source_map.get('vivo')
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())
	
	url = "http://main.gamecenter.vivo.com.cn/clientRequest/recommendBottomList?appVersionName=2.0.0&model=MI+4LTE&e=11010030313647453200da18b1312200&page_index=2&pixel=3.0&imei=865931027730878&origin=20&type=list&av=19&patch_sup=1&cs=0&adrVerName=4.4.4&appVersion=37&elapsedtime=355152353&s=2%7C1435892598"
	j = get_data_from_api(url)
	if j is not None and j['module'] is not None:
		try:
			for item in j['module']:
				if item.get('title') == u'抢鲜推荐':
					for game in item['msg']:
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						picUrl = game.get('icon', u'')
						if picUrl:
							game_name = game.get('name', u'')
							game_id = insert_ad_game(game_name, picUrl)
							position_name = item.get('title')
							position_type_id = position_type_map.get(u'热门图标推荐')
							channel = source_map.get('vivo')
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())
			
	#网游banner
	url = "http://main.gamecenter.vivo.com.cn/clientRequest/onlineTop?appVersionName=2.0.0&model=MI+4LTE&e=11010030313647453200da18b1312200&pixel=3.0&showPosition=0&imei=865931027730878&origin=515&type=top&av=19&patch_sup=1&cs=0&adrVerName=4.4.4&appVersion=37&elapsedtime=353790968&s=2%7C4261617499"
	j = get_data_from_api(url)
	if j is not None:
		try:
			if j['adinfo'] is not None:
				for ad in j['adinfo']:
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = ad.get('picUrl', u'')
					if picUrl:
						game_name = ad.get('showText', u'')
						game_name = u'' if game_name is None else game_name
						game_id = insert_ad_game(game_name, picUrl)
						position_name = u'大屏轮播图'
						position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
						channel = source_map.get('vivo')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
			if j['excellentNewGames'] is not None:
				for ad in j['excellentNewGames']:
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = ad.get('icon', u'')
					if picUrl:
						game_name = ad.get('name', u'')
						game_name = u'' if game_name is None else game_name
						game_id = insert_ad_game(game_name, picUrl)
						position_name = u'优秀新游'
						position_type_id = position_type_map.get(u'热门图标推荐')
						channel = source_map.get('vivo')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
			if j['fashionableGames'] is not None:
				for ad in j['fashionableGames']:
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = ad.get('icon', u'')
					if picUrl:
						game_name = ad.get('name', u'')
						game_name = u'' if game_name is None else game_name
						game_id = insert_ad_game(game_name, picUrl)
						position_name = u'流行精品'
						position_type_id = position_type_map.get(u'热门图标推荐')
						channel = source_map.get('vivo')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())

	#单机
	url = "http://main.gamecenter.vivo.com.cn/clientRequest/aloneTop?appVersionName=2.0.0&model=MI+4LTE&e=11010030313647453200da18b1312200&pixel=3.0&showPosition=0&imei=865931027730878&origin=517&type=top&av=19&patch_sup=1&cs=0&adrVerName=4.4.4&appVersion=37&elapsedtime=354896896&s=2%7C3844052902"

	j = get_data_from_api(url)
	if j is not None and j['weeklyTopGames'] is not None:
		try:
			for ad in j['weeklyTopGames']:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = ad.get('icon', u'')
				if picUrl:
					game_name = ad.get('name', u'')
					game_name = u'' if game_name is None else game_name
					game_id = insert_ad_game(game_name, picUrl)
					position_name = u'本周最佳'
					position_type_id = position_type_map.get(u'热门图标推荐')
					channel = source_map.get('vivo')
					insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())

def get_coolpad_ad():
	#banner
	url = "http://gamecenter.coolyun.com/gameAPI/API/getSubjectList?key=0"
	raw_data = """<?xml version="1.0" encoding="utf-8"?><request username="" cloudId="" openId="" sn="865931027730878" platform="1" platver="19" density="480" screensize="1080*1920" language="zh" mobiletype="MI4LTE" version="4" seq="0" appversion="3350" currentnet="WIFI" channelid="coolpad" networkoperator="46001" simserianumber="89860115851040101064" ><syncflag>0</syncflag><subjecttype>1</subjecttype><max>10</max></request>"""
	
	try:	
		r = requests.post(url, data=raw_data, headers={'Content-Type': 'application/xml'}, timeout=10)
		if r.status_code == 200:
			t = re.sub(u'<briefdescription>[\S\s]*</briefdescription>', u'', r.text)
			t = re.sub(u'\r|\n', u'', t)
			doc = xmltodict.parse(t)
			for ad in doc['response']['ads']['ad']:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = ad.get('@picurl', u'')
				if picUrl:
					if u'res' in ad.keys():
						game_name = ad['res'].get('@name', u'')
					else:
						game_name =  u''
					game_id = insert_ad_game(game_name, picUrl)
					position_name = u'大屏轮播图'
					position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
					channel = source_map.get('coolpad')
					insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
	except Exception,e:
		mylogger.error(traceback.format_exc())

	#首页广告位
	raw_data = """<?xml version="1.0" encoding="utf-8"?><request username="" cloudId="" openId="" sn="865931027730878" platform="1" platver="19" density="480" screensize="1080*1920" language="zh" mobiletype="MI4LTE" version="4" seq="0" appversion="3350" currentnet="WIFI" channelid="coolpad" networkoperator="46001" simserianumber="89860115851040101064" ><syncflag>0</syncflag><subjecttype>2</subjecttype><max>10</max></request>"""
	try:
		r = requests.post(url, data=raw_data, headers={'Content-Type': 'application/xml'}, timeout=10)
		if r.status_code == 200:
			t = re.sub(u'\r|\n', '', r.text)
			doc = xmltodict.parse(t)
			for ad in doc['response']['ads']['ad'][:10]:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = ad.get('@picurl', u'')
				if picUrl:
					if u'res' in ad.keys():
						game_name = ad['res'].get('@name', u'')
					else:
						game_name =  u''
					game_id = insert_ad_game(game_name, picUrl)
					position_name = u'首页大图'
					position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
					channel = source_map.get('coolpad')
					insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
	except Exception,e:
		mylogger.error(traceback.format_exc())

	#网游广告位
	raw_data = """<?xml version="1.0" encoding="utf-8"?><request username="" cloudId="" openId="" sn="865931027730878" platform="1" platver="19" density="480" screensize="1080*1920" language="zh" mobiletype="MI4LTE" version="4" seq="0" appversion="3350" currentnet="WIFI" channelid="coolpad" networkoperator="46001" simserianumber="89860115851040101064" ><syncflag>0</syncflag><subjecttype>4</subjecttype><max>4</max></request>"""
	try:
		r = requests.post(url, data=raw_data, headers={'Content-Type': 'application/xml'}, timeout=10)
		if r.status_code == 200:
			t = re.sub(u'\r|\n', '', r.text)
			doc = xmltodict.parse(t)
			for ad in doc['response']['ads']['ad'][:4]:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = ad.get('@picurl', u'')
				if picUrl:
					if u'res' in ad.keys():
						game_name = ad['res'].get('@name', u'')
					else:
						game_name =  u''
					game_id = insert_ad_game(game_name, picUrl)
					position_name = u'首页大图'
					position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
					channel = source_map.get('coolpad')
					insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
	except Exception,e:
		mylogger.error(traceback.format_exc())

def get_gionee_gamecenter_ad():
	raw_data = {
		'brand': 'Xiaomi',
		'client_pkg': 'gn.com.android.gamehall',
		'imei': 'F69F31CE88DEBF8569A00B953A43343E',
		'sp': 'MI%2B4LTE_1.6.1.b_null_Android4.4.4_1080*1920_N06000_wifi_F69F31CE88DEBF8569A00B953A43343E',
		'version': '1.6.1.b'}
	#top banner
	url = "http://game.gionee.com/Api/Local_Home/slideAd"
	j = get_data_from_api(url, params=raw_data)
	if j is not None:
		try:
			for slide in j['data']['slideItems']:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = slide.get('imageUrl', u'')
				if picUrl:
					game_name = slide.get('title', u'')
					game_id = insert_ad_game(game_name, picUrl)
					position_name = u'大屏轮播图'
					position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
					channel = source_map.get('gionee')
					insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())
	for p in xrange(1, 3):
		url = "http://game.gionee.com/api/Local_Home/newRecomendList?&page=%s" % p
		try:
			j = get_data_from_api(url, params=raw_data)
			if j is not None:
				for item in j['data']['list']:
					item_type = item.get('listItemType', u'')
					title = item.get('title', u'')
					if item_type == u'SimpleBanner':
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						picUrl = item.get('bannerImg', u'')
						if picUrl:
							game_name = item.get('title', u'')
							game_id = insert_ad_game(game_name, picUrl)
							position_name = u'首页大图'
							position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
							channel = source_map.get('gionee')
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
					else:
						if len(item.get('gameItems', []))>=1:
							for game in item['gameItems']:
								channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
								picUrl = game.get('img', u'')
								if picUrl:
									game_name = game.get('name', u'')
									game_id = insert_ad_game(game_name, picUrl)
									position_name = title
									position_type_id = position_type_map.get(u'热门图标推荐')
									channel = source_map.get('gionee')
									insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())

		
	#每日一推荐
	url = "http://game.gionee.com/api/Local_Home/dailyRecommend"
	j = get_data_from_api(url, params=raw_data)
	if j is not None:
		try:
			for slide in j['data']['list']:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = slide.get('img', u'')
				if picUrl:
					game_name = slide.get('title', u'')
					game_id = insert_ad_game(game_name, picUrl)
					position_name = u'每日一荐'
					position_type_id = position_type_map.get(u'热门图标推荐')
					channel = source_map.get('gionee')
					insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())

def get_myaora_ad():
	url = "http://adres.myaora.net:81/api.php"
	raw_data = {"API_VERSION":7,"IS_APP":0,"MODEL":"MI 4LTE","MARKET_IMEI":"865931027730878","TAG":"GAME_BANNER_LIST","MARKET_KEY":"0f1cb7f18e7fb49f049cbead725f990d"}
	try:
		r = requests.post(url, timeout=20, data=json.dumps(raw_data))
		if r.status_code == 200:
			j = r.json()
			for slide in j.get('ARRAY', []):
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = slide.get('IMG_URL', u'')
				if picUrl:
					game_name = slide.get('AD_NAME', u'')
					game_id = insert_ad_game(game_name, picUrl)
					position_name = u'大屏轮播图'
					position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
					channel = source_map.get('myaora')
					insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
	except Exception,e:
		mylogger.error("get jsondata from ### %s ### \n%s" % (url, traceback.format_exc()))



def get_iqiyi_ad():
	url = "http://store.iqiyi.com/gc/home?callback=rs&t=1451141147179"
	try:
		r = requests.get(url)
		if r.status_code == 200:
			m = re.search(u'rs\\(([\s\S]*)\\)\\;', r.text)
			if m is not None:
				j = json.loads(m.group(1))
				for slide in j['focuses']:
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = slide.get('pic', u'')
					if picUrl:
						game_name = slide.get('name', u'')
						game_id = insert_ad_game(game_name, picUrl)
						position_name = u'大屏轮播图'
						position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
						channel = source_map.get('iqiyi')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
				#每日一荐
				dailyapp = j['dailyapp']
				if dailyapp is not None:
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = dailyapp.get('icon', u'')
					if picUrl:
						game_name = dailyapp.get('name', u'')
						game_id = insert_ad_game(game_name, picUrl)
						position_name = u'每日一荐'
						position_type_id = position_type_map.get(u'热门图标推荐')
						channel = source_map.get('iqiyi')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
				for item in j['collectionApps']:
					title = item.get('name', u'')
					for game in item['apps']:
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						picUrl = game.get('icon', u'')
						if picUrl:
							game_name = game.get('name', u'')
							game_id = insert_ad_game(game_name, picUrl)
							position_name = title
							position_type_id = position_type_map.get(u'精品速递/专题推荐')
							channel = source_map.get('iqiyi')
							insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
				for game in j['newapps']:
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = game.get('icon', u'')
					if picUrl:
						game_name = game.get('name', u'')
						game_id = insert_ad_game(game_name, picUrl)
						position_name = u'每日新游'
						position_type_id = position_type_map.get(u'精品速递/专题推荐')
						channel = source_map.get('iqiyi')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))

				for game in j['hotapps']:
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = game.get('icon', u'')
					if picUrl:
						game_name = game.get('name', u'')
						game_id = insert_ad_game(game_name, picUrl)
						position_name = u'热门游戏'
						position_type_id = position_type_map.get(u'热门图标推荐')
						channel = source_map.get('iqiyi')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
	except Exception, e:
		mylogger.error("get iqiyi ad ### \n%s" % (traceback.format_exc()))

def get_jinshan_pc_ad():
	#首页弹出广告
	url = "http://app.sjk.ijinshan.com/app/activity-mask-layer/maskLayer.json"
	j = get_data_from_api(url)
	if j is not None and j['data'] is not None:
		slide = j['data']
		channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
		picUrl = slide.get('imageUrl', u'')
		if picUrl:
			game_name = slide.get('appName', u'')
			game_id = insert_ad_game(game_name, picUrl)
			position_name = u'首页弹出广告'
			position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
			channel = source_map.get('jinshan')
			insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
			

	#本周精品
	url = "http://app.sjk.ijinshan.com/app/api/cdn/label/mix-label-list/778.json?rows=20&page=1"
	j = get_data_from_api(url)
	if j is not None and j['data'] is not None:
		try:
			if j['data']['label-apps'] is not None and len(j['data']['label-apps']) >= 1:
				top_games = j['data']['label-apps'][0]['tagApps']
				for game in top_games:
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = game.get('logoThUrls', u'')
					if picUrl:
						game_name = game.get('name', u'')
						game_id = insert_ad_game(game_name, picUrl)
						position_name = u'本周精品'
						position_type_id = position_type_map.get(u'精品速递/专题推荐')
						channel = source_map.get('jinshan')
						insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())


	#轮播图
	url = "http://app.sjk.ijinshan.com/app/api/redbanners.json?type=1"
	j = get_data_from_api(url)
	if j is not None and j['data'] is not None:
		try:
			for game in j['data']:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = game.get('logoThUrls', u'')
				if picUrl:
					game_name = game.get('name', u'')
					game_id = insert_ad_game(game_name, picUrl)
					position_name = u'轮播图'
					position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
					channel = source_map.get('jinshan')
					insert_ad_data((channel, position_type_id, position_name, game_id, identifying))
		except Exception,e:
			mylogger.error(traceback.format_exc())


def insert_ad_data(ret):
	channel, position_type_id, position_name, game_id, identifying = ret
	dt = datetime.date.today()
	ins = db_conn.query(ADVRecord2).filter(ADVRecord2.update_date==dt).filter(ADVRecord2.channel_id==channel).filter(ADVRecord2.position_type_id==position_type_id).filter(ADVRecord2.adv_game_detail_id==game_id).filter(ADVRecord2.position_name==position_name).first()
	if ins is None:
		item = ADVRecord2(**{
						"channel_id"		: channel,
						"position_type_id"	: position_type_id,
						"position_name"		: position_name,
						"adv_game_detail_id": game_id,
						"update_date"		: dt,
						})
		db_conn.merge(item)
	db_conn.commit()

def insert_ad_game(game_name, img):
	ins = db_conn.query(ADVGameDetail).filter(ADVGameDetail.game_name==game_name).filter(ADVGameDetail.img_url==img).first()
	if ins is None:
		item = ADVGameDetail(**{
						"img_url"			: img,
						"game_name"			: game_name,
						})
		db_conn.add(item)
		db_conn.commit()
		return item.id
	else:
		return ins.id

def main():
	mylogger.info("get ad info ...")
	get_appicsh_raw_data()
	get_9game_raw_data()
	get_9game_newgame()
	get_9game_bbs()
	get_360zhushou_app_ad()
	get_360zhushou_web_ad()
	get_mmstore_ad()
	get_open_play_ad()
	get_wostore_ad()
	get_wogame_ad()
	get_oppo_ad()
	get_vivo_gamecenter_ad()
	get_gionee_gamecenter_ad()
	get_myaora_ad()
	get_iqiyi_ad()
	get_jinshan_pc_ad()
	get_360gamebox_raw_data()
	get_coolpad_ad()

if __name__ == "__main__":
	main()

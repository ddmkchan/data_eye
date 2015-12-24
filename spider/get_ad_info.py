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
	conn = MySQLdb.connect(host="127.0.0.1",port=3306,user="root",passwd="admin",charset="utf8")
	cursor = conn.cursor()
	cursor.execute("select * from dataeye.position_type")
	for re in cursor.fetchall():
		id, name = re
		mydict[name] = id
	return mydict

position_type_map = get_position_type_map()


def get_data_from_api(url, timeout=10, headers={}, proxies={}):
	if isinstance(url, unicode):
		url = url.encode('utf-8')
	try:
		r = requests.get(url, timeout=timeout, headers=headers, proxies=proxies)
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
						channel = source_map.get('9game')
						position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
						position_name = u'首页大图'
						insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))

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
						channel = source_map.get('9game')
						position_type_id = position_type_map.get(u'热门图标推荐')
						position_name = u'手机游戏推荐'
						insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))
					
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
							channel = source_map.get('9game')
							position_type_id = position_type_map.get(u'热门图标推荐')
							position_name = u'游戏分类'
							insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))
				
def get_9game_newgame():
	soup = get_page_source_from_web("http://www.9game.cn/newgame/", timeout = 20)
	if soup is not None and soup:
		top_game_recom = soup.find('div',class_='box top-game-recom')
		if top_game_recom is not None:
			top_recom = top_game_recom.find('div', class_='top-recom')
			if top_recom is not None:
				for app in top_recom.find_all('a'):
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					identifying = app.get('href')
					game_name = app.get('title')
					if game_name is not None and game_name:
						channel = source_map.get('9game')
						position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
						position_name = u'新游推荐'
						insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))
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
							channel = source_map.get('9game')
							position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
							position_name = u'新游推荐'
							insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))

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
							channel = source_map.get('9game')
							position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
							position_name = u'新游宣传图'
							insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))

def get_9game_ka():
	#异步加载
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
		img_box = soup.find('p', id='top_change_img')
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
					position_name = u'论坛宣传图'
					insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))
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
							channel = source_map.get('9game')
							position_type_id = position_type_map.get(u'精品速递/专题推荐')
							position_name = u'论坛新游推荐专区'
							insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))
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
							channel = source_map.get('9game')
							position_type_id = position_type_map.get(u'精品速递/专题推荐')
							position_name = u'热门游戏专区'
							insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))
						


def get_appicsh_raw_data():
	flags = [u"应用宝-banner", u"应用宝-礼包", u"应用宝-精品推荐", u"应用宝-新游推荐", u"应用宝-热门网游", u"应用宝-热门单机", u"应用宝-每日精选"]
	urls = [u"http://m5.qq.com/app/banner.htm?sceneId=1", u"http://m5.qq.com/app/getgifboxtips.htm?sceneId=0", u"http://m5.qq.com/app/groupapps.htm?type=4&pageSize=30&cardId=2", u"http://m5.qq.com/app/applist.htm?listType=0&pageSize=10", u"http://m5.qq.com/app/applist.htm?listType=1&pageSize=15", u"http://m5.qq.com/app/applist.htm?listType=2&pageSize=15", u"http://m5.qq.com/app/banner.htm?sceneId=0"]

	j = get_data_from_api("http://m5.qq.com/app/banner.htm?sceneId=1")

	if j is not None and j:
		for br in j['obj']['bigBanners']:
			channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
			picUrl = br.get('picUrl', u'')
			if picUrl:
				info = br['app']
				if info is not None:
					game_name = info.get('appName', u'')
					identifying = info.get('pkgName', u'')
				position_name = u'游戏精选大图'
				position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
				channel = source_map.get('appicsh')
				insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))
		for br in j['obj']['smallBanners']:
			channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
			info = br['app']
			if info is not None:
				game_name = info.get('appName', u'')
				identifying = info.get('pkgName', u'')
				picUrl = info.get('picUrl', u'')
				position_name = u'游戏精选每日推荐'
				position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
				channel = source_map.get('appicsh')
				if picUrl:
					insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))


	j = get_data_from_api("http://m5.qq.com/app/banner.htm?sceneId=0")

	if j is not None and j:
		for br in j['obj']['bigBanners']:
			channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
			picUrl = br.get('picUrl', u'')
			if picUrl:
				info = br['app']
				if info is not None:
					game_name = info.get('appName', u'')
					identifying = info.get('pkgName', u'')
				position_name = u'每日游戏精选大图'
				position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
				channel = source_map.get('appicsh')
				insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))
		for br in j['obj']['smallBanners']:
			channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
			info = br['app']
			if info is not None:
				game_name = info.get('appName', u'')
				identifying = info.get('pkgName', u'')
				picUrl = info.get('picUrl', u'')
				position_name = u'游戏精选每日推荐'
				position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
				channel = source_map.get('appicsh')
				if picUrl:
					insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))

	j = get_data_from_api("http://m5.qq.com/app/getgifboxtips.htm?sceneId=0")
	if j is not None and j:
		for br in j['obj']['tipsList']:
			channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
			info = br['appInfo']
			if info is not None:
				picUrl = info.get('iconUrl', u'')
				if picUrl:
					game_name = info.get('appName', u'')
					identifying = info.get('pkgName', u'')
					position_name = u'礼包中心弹出广告'
					position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
					channel = source_map.get('appicsh')
					insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))

	flags = [u"新游推荐", u"热门网游", u"热门单机"]
	urls = [u"http://m5.qq.com/app/applist.htm?listType=0&pageSize=10", u"http://m5.qq.com/app/applist.htm?listType=1&pageSize=15", u"http://m5.qq.com/app/applist.htm?listType=2&pageSize=15"]
	for i in xrange(3):
		url = urls[i]
		j = get_data_from_api(url)
		if j is not None and j:
			for app in j['obj']['appList']:
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = app.get('iconUrl', u'')
				if picUrl:
					game_name = app.get('appName', u'')
					identifying = app.get('pkgName', u'')
					position_name = flags[i]
					position_type_id = position_type_map.get(u'精品速递/专题推荐')
					channel = source_map.get('appicsh')
					insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))

	j = get_data_from_api("http://m5.qq.com/app/groupapps.htm?type=4&pageSize=30&cardId=2")
	if j is not None and j:
		for group in j['obj']['groupList']:
			if group.get('groupName', u'') == u"精品推荐":
				for app in group['appList']:
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = app.get('iconUrl', u'')
					if picUrl:
						game_name = app.get('appName', u'')
						identifying = app.get('pkgName', u'')
						position_name = u'精品推荐'
						position_type_id = position_type_map.get(u'精品速递/专题推荐')
						channel = source_map.get('appicsh')
						insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))

def get_360gamebox_raw_data():
	flags = [u"首页精选", u"新游推荐"]
	j = get_data_from_api('http://next.gamebox.360.cn/7/xgamebox/dashboardex?jdata=1450946296&bir=2&nonce=f5ace931-1c70-4018-acae-144065f7ad7a&clienttype=gameunion&v=41611&ch=100100&sk=19&md=mi+4lte&m1=72db07100fc223a2ede82f4a44ae96b4&m2=881f853779fe69ad88926d8ac5ec4930&nt=1&rkey=qe1QeJMtttWAwKjMNmz1sUGKvUW9hZcRPYCJlc0u0SAlJbOan9R3ZYbH%2BREB1MvA1nj%2Bmnc9IQJ%2BY8fhrbWNmEGzCapRZN3SI15iNDTdK2cGmxlvYxuOZkVattKui2NB4nfj4wfphYdIf3VpMfh8Hak1WKmszbBPO0hpBiBBhG8%3D&signid=x9vKfiKUGm%2F9twXAVCCFSVoIB0hHXf5053BA5B6bwzPAgVlvmily9g%3D%3D%0A')
	if j is not None:
		for br in j['data']['topic']['list']:
			title = br.get('title', u'')
			if title in [u'必玩的精品网游', u'口碑游戏', u'优秀新游戏']:
				banner = br['banner']
				if banner is not None:
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = banner.get('logo', u'')
					if picUrl:
						info = banner['game']
						game_name = info.get('name', u'')
						position_name = u'图标推荐' 
						position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
						channel = source_map.get('360_gamebox')
						insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))
				gamelist = br['games']
				if gamelist is not None:
					for game in gamelist:
						channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
						picUrl = game.get('logo_url', u'')
						if picUrl:
							game_name = game.get('name', u'')
							position_name = title 
							position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
							channel = source_map.get('360_gamebox')
							insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))

	j = get_data_from_api('http://next.gamebox.360.cn/7/xgamebox/newgame?nonce=7dd27e13-94c9-4ff0-889e-24df08880a43&clienttype=gameunion&v=41611&ch=100100&sk=19&md=mi+4lte&m1=72db07100fc223a2ede82f4a44ae96b4&m2=881f853779fe69ad88926d8ac5ec4930&nt=1&rkey=fs3KwB%2BEBQjaurPvRWJ3TmorukDpHgCGeh0XMgCibwlCPCJdgBnpEEddl7X6aL7YljJqhjcboCWhIKIkJl%2BYyFkEYJxDJRE%2BIGTMg6lEzPs5FRWJHzIKdfeWmJDrxJBAYi%2BSgNS2Z0ATaufVe1buU0L4bjATNb2NsRtQQmig8ms%3D&signid=PbtzCFU9AFQv6b081FU7zFQEruUM1ZyNDSCS6A8ihkKn2cydBwJJfw%3D%3D%0A')
	if j is not None:
		for k, v in j['data'].iteritems():
			if k == 'zone':
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = v.get('bg', u'')
				if picUrl:
					position_name = u'首页大图'
					position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
					channel = source_map.get('360_gamebox')
					insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))
			if k == 'newgame':
				for game in v['games']:	
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = game.get('logo_url', u'')
					if picUrl:
						game_name = game.get('name', u'')
						position_name = u'新游关注榜' 
						position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
						channel = source_map.get('360_gamebox')
						insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))
			if k == 'ontest':
				channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
				picUrl = v.get('bg', u'')
				if picUrl:
					position_name = u'图标推荐'
					position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
					channel = source_map.get('360_gamebox')
					insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))

				for game in v['games']:	
					channel, position_type_id, position_name, picUrl, game_name, identifying = [u''] * 6
					picUrl = game.get('logo_url', u'')
					if picUrl:
						game_name = game.get('name', u'')
						position_name = u'最近开测'
						position_type_id = position_type_map.get(u'首页大图/大屏轮播图/banner')
						channel = source_map.get('360_gamebox')
						insert_ad_data((channel, position_type_id, position_name, picUrl, game_name, identifying))
			


def get_360_ad_raw_data():
	prefix = u"http://125.88.193.234/AppStore/getRecomendAppsBytype?type=2&s_3pk=1&os=22&vc=300030515&withext=1&model=m2+note&sn=4.589389937671455&cu=mt6753&ca1=armeabi-v7a&ca2=armeabi&&se=1920x1080&webp=1&fm=gm001&m=13389b498494c1230fab6b4c04572848&s_stream_app=1&m2=1680ae9efad81fb51224ec048d296b6a&v=3.5.15&re=1&nt=1&ch=100130&ppi=1080x1920&cpc=1&startCount=0&snt=-1&timestamp=1450431524724"
	for page in xrange(1, 3):
		url = prefix + "&page=%s" % page
		is_json = True
		flag = u'360手机助手app首页大图_%s' % page
		channel = source_map.get('360zhushou')
		rd = get_data_from_api(url)
		if rd is not None and rd: 
			src = url
			store_data((rd, src, channel, is_json, flag))
	

	#360手机助手PC官网
	url = u"http://zhushou.360.cn/Game/"
	rd = get_data_from_api(url, jsondata=False)
	if rd is not None and rd:
		is_json = False
		flag = u'360手机助手PC官网'
		channel = source_map.get('360zhushou')
		src = url
		store_data((rd, src, channel, is_json, flag))


def get_vivo_gamecenter_raw_data():

	flags = [u'首页大图'] 
	urls = [u'http://main.gamecenter.vivo.com.cn/clientRequest/recommendTop?appVersionName=2.0.1&patch_sup=1&appVersion=38&imei=867570024967881&e=150100523832314d4200fe7dc6356213&elapsedtime=11636411&origin=20&adrVerName=5.1&cs=0&pixel=3.0&type=top&av=22&model=m2+note&s=2%7C2009401673']

def insert_ad_data(ret):
	channel, position_type_id, position_name, img, game_name, identifying = ret
	dt = datetime.date.today()
	ins = db_conn.query(ADVRecord).filter(ADVRecord.update_date==dt).filter(ADRawData.channel==channel).filter(ADVRecord.position_type_id==position_type_id).filter(ADVRecord.img_path==img).filter(ADVRecord.position_name==position_name).first()
	if ins is None:
		item = ADVRecord(**{
						"channel_id"		: channel,
						"position_type_id"	: position_type_id,
						"position_name"		: position_name,
						"img_path"			: img,
						"game_name"			: game_name,
						"identifying"		: identifying,
						"update_date"		: dt,
						})
		db_conn.merge(item)
	db_conn.commit()



def main():
	get_appicsh_raw_data()
	get_9game_raw_data()
	get_9game_newgame()
	get_9game_bbs()
	get_360gamebox_raw_data()

if __name__ == "__main__":
	main()

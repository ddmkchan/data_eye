#!/usr/bin/env python
#encoding=utf-8

import requests
import json
import re
from bs4 import BeautifulSoup
from time import sleep
import traceback
from config import *
import random
import datetime
import xmltodict

db_conn = new_session()
s = requests.session()
mylogger = get_logger('kc')

source_map = {
			"9game": 0,
			"18183": 2,
			"u360": 1,
			"appicsh": 3,#应用宝app
			"360zhushou": 4,#360助手app
			"xiaomi_new": 5,#小米app 最新
			"xiaomi_rpg": 6,#小米app rpg
			"open_play": 7,#爱游戏app
			"vivo": 8,#vivo游戏中心
			"coolpad": 9,
			"gionee": 10,
			"lenovo": 11,
			"iqiyi": 12,
			"youku": 13,
			"sogou": 14,
			"dangle": 15,
			"i4": 16,
			"muzhiwan": 17,
			"huawei": 18,
			"kuaiyong": 19,
			"itools": 20,
			"anzhi": 21,
			"360zhushou_web": 22,#360助手web
			"wandoujia": 23,
			"pp": 24,
			"meizu": 25,
			"xyzs": 26,
			"91play": 27,#酷玩汇
			"360_gamebox": 28,
			"m_baidu_app": 29,#百度手机助手
			"lenovo_shop": 30,
			"wostore": 31,#沃商店
			"mmstore": 32,
			"vivo_store": 33,
			"huawei_app": 34,
			"ipaddown": 35,
			"i4_app": 36,
			"tgbus": 37,
			"4399": 38,
			"yxhi": 39,
			"oppo_app": 50,
			"wogame": 998,
			"myaora": 997,#易用汇
			"jinshan": 996,#金山手机助手
				}

class T:
	
	def __init__(self, status_code):
		self.status_code = status_code

def get_9game_today_kc():
	URL = u"http://www.9game.cn/kc/"
	mylogger.info("9game gogo")
	try:
		r = s.get(URL, timeout=10)
		soup = BeautifulSoup(r.text)
		publish_date = unicode(datetime.date.today())
		time 		= u""
		title 		= u""
		title2 		= u""
		img 		= u""
		url 		= u""
		device 		= u""
		publish_status 		= u""
		game_type 	= u""
		popular 	= u""
		today_list = soup.find("ul", class_="today-server-list").find_all("li")
		#today_list = soup.find("ul", class_="today-server-list").find_all("li", class_='timeli')
		if today_list is not None:
			mylogger.info("kc games : %s" %len(today_list))
			for t in today_list:
				try:
					time_div = t.find("div", class_="time")
					time = time_div.text if time_div is not None else time
					#print '****', time
					pic_div = t.find("div", class_="pic")
					if pic_div is not None:
						img = pic_div.find("img").get("src")
						#img = pic_div.find("a").find("img").get("src")
					rt = t.find("div", class_="right-text")
					if rt is not None:
						tit_p = rt.find("p", class_="tit")
						if tit_p is not None:
							title 	= tit_p.find("a").get("title")
							title2 	= tit_p.find("a").text
							url 	= tit_p.find("a").get("href")
							device 	= tit_p.find("span").get("class")
							popular 	= tit_p.find("span", class_="type-con").find("span").text
						type_div = rt.find("div", class_="type").find_all("span", class_="type-con")
						if type_div is not None:
							time 		= type_div[0].text
							publish_status 		= type_div[0].find("span").text
							#game_type 	= type_div[1].find('td')
							#print type_div
							#print re.split(u"：| ", time)[1], status, game_type
					if title and url:
						ins = db_conn.query(KC_LIST).filter(KC_LIST.source==source_map.get('9game')).filter(KC_LIST.url==url).filter(KC_LIST.publish_date==publish_date).first()
						#ins = db_conn.query(KC_LIST).filter(KC_LIST.source==source_map.get('9game')).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).first()
						if not ins:
							item = KC_LIST(**{
								"time"		: re.split(u"：| ", time)[1],
								"title" 		: title,
								"title2" 		: title2, 
								"img" 		: img, 
								"url" 		: url, 		
								"device" 		: u",".join(device), 		
								"publish_status" 		: publish_status, 		
								"game_type" 	: game_type, 	
								"popular" 	: popular,
								"source" 	: source_map.get('9game'),
								"publish_date" 	: unicode(datetime.date.today()) 	
									})
							db_conn.merge(item)
				except Exception,e:
					db_conn.rollback()
					mylogger.error("--------%s" % (traceback.format_exc()))
		else:
			mylogger.info("no kc games....")
	except Exception,e:
		mylogger.error("====>\t%s" % (traceback.format_exc()))
	db_conn.commit()



def get_18183_kc():
	count = 0
	URL = "http://xin.18183.com/ceshi/"
	try:
		response = s.get(URL, timeout=10)
		r = response.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(response.text)[0])
		soup = BeautifulSoup(r)
		publish_dates = soup.find("ul", class_="tab_menu").find_all("li")
		tabs = soup.find_all("div", class_="tab_main")
		for j in xrange(len(tabs)):
			if publish_dates[j].find("a").text == u"今日": 
				publish_date = u"2015-%s" % publish_dates[j].find("a").text if publish_dates[j].find("a").text!=u"今日" else datetime.date.today().strftime("%Y-%m-%d") 
				tab = tabs[j]
				kc_div = tab.find_all("div")
				for i in xrange(0, len(kc_div), 2):
					type_div = kc_div[i:i+2][0]
					if type_div.text == u"开测游戏":
						content = kc_div[i:i+2][1]
						for t in content.find("ul").find_all("li"):
							count += 1
							title = t.find("div", class_="tait").find("h4").text
							url = t.find("div", class_="down").find("a").get('href')
							img = t.find("img").get("src")
							time = t.find("div", class_="pt").find("div", class_="time fl").find("i").text
							devices = [i.get("class")[0] for i in t.find("div", class_="pt").find("div", class_="xy fl").find_all("span") if i.get("class") is not None]
							publish_status = t.find("div", class_="pt m6").find("code").text
							ins = db_conn.query(KC_LIST).filter(KC_LIST.url==url).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('18183')).first()
							#ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.status==status).filter(KC_LIST.source==source_map.get('18183')).first()
							if not ins:
								item = KC_LIST(**{
										"title"		: 	title,
										"url"		: 	url,
										"img" 		:	img,
										"time" 		:	time,
										"device" 	:	",".join(devices),
										"publish_status"	:	publish_status,
										"publish_date"	:	publish_date,
										"source"	:	source_map.get('18183')
											})
								db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	db_conn.commit()
	mylogger.info("get %s records from 18183 kc" % count)

def get_360_kc():
	count = 0
	URL = "http://u.360.cn/xin/ceshi/"
	try:
		response = s.get(URL, timeout=10)
		r = response.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(response.text)[0])
		soup = BeautifulSoup(r)
		c = soup.find_all("div", class_="content")
		for content in c:
			table = content.find("table", class_="tablists tablists_green")
			if table is not None:
				pass
			else:
				publish_date = u""
				date_h3 = content.find("h3")
				if date_h3 is not None:
					publish_date = date_h3.text[5:-1]
					publish_date = re.sub(u"月", u"-", publish_date)
					publish_date = re.sub(u"日", u"", publish_date)
					publish_date = u"2015-%s" % publish_date
				tablists = content.find("table",  class_="tablists").find_all("tr")
				if tablists is not None:
					for tr in tablists[1:]:
						time 	= u""
						title 	= u""
						img 	= u""
						publish_status	= u""
						game_type = u""
						tds = tr.find_all("td")
						if tds is not None:
							title = re.sub(u"\xa0", u"", tds[0].text)
							img = u"" if tds[0].find("img") is None else tds[0].find("img").get("src")
							url = u"" if tds[0].find("a") is None else tds[0].find("a").get("href")
							publish_status = tds[1].text
							game_type = tds[3].text
							if url and publish_date:
								ins = db_conn.query(KC_LIST).filter(KC_LIST.url==url).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('u360')).first()
								#ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.status==status).filter(KC_LIST.source==source_map.get('u360')).first()
								if not ins:
									count += 1								
									item = KC_LIST(**{
												"publish_date": publish_date,
												"time": time,
												"title": title,
												"url": url,
												"publish_status": publish_status,
												"game_type": game_type,
												"img": img,
												"source": source_map.get('u360')
												})
									db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from 360 kc" % count)
	db_conn.commit()				

def get_appicsh_kc():
	count = 0
	#url = "http://m5.qq.com/app/applist.htm?listType=18&pageSize=150" #pc url
	url = "http://appicsh.qq.com/cgi-bin/appstage/FirstPublishTab?type=3&index=0&pageSize=30"
	try:
		r = requests.get(url, timeout=10)
		if r.status_code == 200:
			d = r.json()
			if d['msg'] == u'success':
				new_games_list = d['new_games']['list']
				#new_games_list = d['obj']['appList']
				for game in new_games_list:
					title = game.get('name', u"")
					game_type = game.get('categor', u"")
					img = game.get('icon', u"")
					publishtime = game.get('publishtime', u"")
					pkg_name = game.get('pkgname', u'')
					url = u"http://m5.qq.com/app/getappdetail.htm?pkgName=%s&sceneId=0" % pkg_name if pkg_name else u''
					publish_date = unicode(datetime.date.fromtimestamp(publishtime)) if publishtime else u""
					#print title, img, publish_date
					if pkg_name and publish_date:
						ins = db_conn.query(KC_LIST).filter(KC_LIST.pkg_name==pkg_name).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('appicsh')).first()
						#ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('appicsh')).first()
						if ins is None:
							count += 1
							item = KC_LIST(**{
										"title": title,
										"game_type": game_type,
										"publish_date": publish_date,
										"img": img,
										"source": source_map.get('appicsh'),
										"url": url,
										"pkg_name": pkg_name,
										})
							db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	mylogger.info("get %s records from appicsh" % count)
	db_conn.commit()

def get_360zhushou_kc():
	count = 0
	URL = "http://openbox.mobilem.360.cn/gamestart/list?type=2"
	try:
		r = requests.get(URL, timeout=10)
		if r.status_code == 200:
			soup = BeautifulSoup(r.text)
			item_list = soup.find_all("div", class_="app-item-list")[0]
			if item_list is not None:
				app_list = item_list.find_all('div', class_='app-main app-item')
				#print logo_list
				#app_list = item_list.find_all('div', class_='app-detail')
				for app in app_list:
					logo = app.find('div', class_='app-logo')
					item = app.find('div', class_='app-detail')
					title = u""
					game_type = u""
					size = u""
					publish_date = u""
					publish_status = u""
					time = u""
					img = u""
					if logo is not None:
						if logo.find('img') is not None:
							img = logo.find('img').get('data-icon')
					title_h3 = item.find('h3')
					if title is not None:
						title = title_h3.text
						meta = item.find('div', class_="app-meta text-over")
						if meta is not None:
							m2 = re.search(u'[\u4e00-\u9fa5\s]+', meta.text)
							game_type = m2.group() if m2 is not None else u''
						meta2 = item.find('div', class_="app-meta2 text-over")
						if meta2 is not None:
							spans = meta2.find_all('span')
							if len(spans) == 2:
								dt, publish_status = [i.text for i in spans]
								publish_date, time = dt.split(u' ')
						#print title, game_type, '****', publish_date, img
					pkg_id = app.get('data-sid', u'')
					pkg_name = app.get('data-pname', u'')	
					if pkg_name and publish_date:
						ins = db_conn.query(KC_LIST).filter(KC_LIST.pkg_name==pkg_name).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('360zhushou')).first()
						#ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('360zhushou')).first()
						if ins is None:
							count += 1
							item = KC_LIST(**{
												"title" : title,
												"game_type" : game_type,
												"publish_date" : publish_date,
												"time" : time,
												"img" : img,
												"title2" : pkg_name,
												"pkg_name" : pkg_name,
												"game_id" : pkg_id,
												"publish_status" : publish_status,
												"source" : source_map.get('360zhushou'),
											})
							db_conn.merge(item)
						else:
							ins.img = img
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from 360 zhushou app" % count)
	db_conn.commit()

def get_xiaomi_new_kc(page):
	count = 0
	url = "http://app.migc.xiaomi.com/cms/interface/v5/subjectgamelist1.php?pageSize=20&page=%s&subId=138" % page
	try:
		r = requests.get(url, timeout=10)
		if r.status_code == 200:
			d = r.json()
			if d['errCode'] == 200:
				new_games_list = d.get('gameList', [])
				for g in new_games_list:
					title = g.get('displayName', u'')
					img = g.get('icon', u'')
					popular = g.get('downloadCount', u'')
					game_type = g.get('className', u'')
					pubTime = g.get('pubTime', u'')
					publish_date = u""
					pkg_name = g.get('packageName', u'')
					if pubTime:
						t = unicode(pubTime)[:10]
						publish_date = unicode(datetime.date.fromtimestamp(int(t)))
					if pkg_name and publish_date :
						ins = db_conn.query(KC_LIST).filter(KC_LIST.pkg_name==pkg_name).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('xiaomi_new')).first()
						if ins is None:
							count += 1
							item = KC_LIST(**{
										"title": title,
										"game_type": game_type,
										"publish_date": publish_date,
										"img": img,
										"game_id": g.get('gameId', u''),
										"pkg_name": pkg_name,
										"popular": popular,
										"source": source_map.get('xiaomi_new')
										})
							db_conn.merge(item)
						else:
							ins.game_id = g.get('gameId', u'')
							ins.pkg_name = g.get('packageName', u'')
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	mylogger.info("get %s records from xiaomi_new" % count)
	db_conn.commit()

def get_xiaomi_rpg_kc(page):
	count = 0
	url = "http://app.migc.xiaomi.com/cms/interface/v5/subjectgamelist1.php?subId=203&pageSize=20&page=%s" % page
	try:
		r = requests.get(url, timeout=10)
		if r.status_code == 200:
			d = r.json()
			if d['errCode'] == 200:
				new_games_list = d.get('gameList', [])
				for g in new_games_list:
					title = g.get('displayName', u'')
					img = g.get('icon', u'')
					popular = g.get('downloadCount', u'')
					game_type = g.get('className', u'')
					summary = g.get('summary', u'')
					pubTime = g.get('pubTime', u'')
					publish_status = u""
					publish_date = u""
					pkg_name = g.get('packageName', u'')
					if pubTime:
						t = unicode(pubTime)[:10]
						publish_date = unicode(datetime.date.fromtimestamp(int(t)))
					#if summary:
						#if u'|' in summary:
						#	dt, publish_status = summary.split(u'|')
					if pkg_name and publish_date :
						ins = db_conn.query(KC_LIST).filter(KC_LIST.pkg_name==pkg_name).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('xiaomi_rpg')).first()
						if ins is None:
							count += 1
							item = KC_LIST(**{
										"title": title,
										"game_type": game_type,
										"publish_date": publish_date,
										"game_id": g.get('gameId', u''),
										"pkg_name": pkg_name,
										"img": img,
										"popular": popular,
										"publish_status": publish_status,
										"source": source_map.get('xiaomi_rpg')
										})
							db_conn.merge(item)
						else:
							ins.game_id = g.get('gameId', u'')
							ins.pkg_name = g.get('packageName', u'')
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	mylogger.info("get %s records from xiaomi_rpg" % count)
	db_conn.commit()

def get_open_play_kc():
	count = 0
	url = "http://open.play.cn/api/v2/mobile/channel/content.json?channel_id=702&terminal_id=18166&current_page=0&rows_of_page=20"
	try:
		r = requests.get(url, timeout=10)
		if r.status_code == 200:
			d = r.json()
			if d['code'] == 0:
				new_games_list = d['ext']['main']['content']['game_list']
				for g in new_games_list:
					title = g.get('game_name', u'')
					img = g.get('game_icon', u'')
					popular = g.get('game_download_count', u'')
					game_type = g.get('class_name', u'')
					publish_date = u""
					game_id = g.get('game_id', u'')
					if game_id:
						online_time = g.get('last_online_time', u'')
						if online_time:
							dt, time = online_time.split(u' ')
							publish_date = dt
						if publish_date:
							ins = db_conn.query(KC_LIST).filter(KC_LIST.game_id==game_id).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('open_play')).first()
							if ins is None:
								count+=1
								item = KC_LIST(**{
											"title": title,
											"title2": game_id,
											"game_id": game_id,
											"game_type": game_type,
											"publish_date": publish_date,
											"img": img,
											"popular": popular,
											"source": source_map.get('open_play')
											})
								db_conn.merge(item)
							else:
								ins.game_id = game_id
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	mylogger.info("get %s records from open_play" % count)
	db_conn.commit()

def get_vivo_kc(page):
	count = 0
	#url = "http://gamecenter.vivo.com.cn/clientRequest/topicGame?id=214&page_index=1"
	url = "http://main.gamecenter.vivo.com.cn/clientRequest/startingGame?page_index=%s" % page
	try:
		r = requests.get(url, timeout=10)
		if r.status_code == 200:
			d = r.json()
			for ret in d['msg']:
				title = ret.get('name', u'')
				game_type = ret.get('type', u'')
				popular = ret.get('download', u'')
				img = ret.get('icon', u'')
				pkg_name = ret.get('pkgName', u'')
				comment = ret.get('comment', u'')
				dt = ret.get('categoryType', u'')
				m = re.search(u'(\d+)月(\d+)日', dt)
				_date = u''
				game_id = ret.get('id', u'')
				try:
					if m.group(1) == u'12':
						_date = u"2015-%s-%s" % (m.group(1), m.group(2))
					else:
						_date = u"%s-%s-%s" % (datetime.date.today().year, m.group(1), m.group(2))
				except Exception, e:
					mylogger.error("%s" % (traceback.format_exc()))
				if _date and game_id:
					detail_url = "http://info.gamecenter.vivo.com.cn/clientRequest/gameDetail?id=%s&adrVerName=4.4.4&appVersion=37" % game_id
					publish_date = datetime.datetime.strptime(_date, '%Y-%m-%d')
					ins = db_conn.query(KC_LIST).filter(KC_LIST.game_id==game_id).filter(KC_LIST.publish_date==unicode(publish_date.date())).filter(KC_LIST.source==source_map.get('vivo')).first()
					if ins is None:
						count+=1
						item = KC_LIST(**{
								"title": title,
								"game_id": game_id,
								"game_type": game_type,
								"publish_date": unicode(publish_date.date()),
								"img": img,
								"url": detail_url,
								"popular": popular,
								"source": source_map.get('vivo')
								})
						db_conn.merge(item)
					else:
						ins.url = detail_url
						ins.game_id = game_id
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	mylogger.info("get %s records from vivo" % count)
	db_conn.commit()
			

def get_coolpad_kc():
	count = 0
	url = "http://gamecenter.coolyun.com/gameAPI/API/getResList?key=0"
	raw_data = """<?xml version="1.0" encoding="utf-8"?>
<request username="" cloudId="" openId="" sn="865931027730878" platform="1" platver="19" density="480" screensize="1080*1920" language="zh" mobiletype="MI4LTE" version="4" seq="0" appversion="3120" currentnet="WIFI" channelid="coolpad" networkoperator="46001" simserianumber="89860115851040101064">
  <rankorder>0</rankorder>
  <syncflag>0</syncflag>
  <start>1</start>
  <categoryid>1</categoryid>
  <iscoolpad>0</iscoolpad>
  <level>0</level>
  <querytype>3</querytype>
  <max>10</max>
</request>
"""
	try:
		r = requests.post(url, data=raw_data, headers={'Content-Type': 'application/xml'}, timeout=10)
		if r.status_code == 200:
			t = re.sub(u'\r|\n', '', r.text)
			doc = xmltodict.parse(t)
			for k in doc['response']['reslist']['res']:
				title = k.get('@name', u'')
				game_type = k.get('levelname', u'')
				pkg_name = k.get('package_name', u'')
				score = k.get('score', u'')
				img = k.get('icon', u'')
				popular = k.get('downloadtimes', u'')
				resid = k.get('@rid', u'')
				if resid:
					publish_date = get_coolpad_pubtime_by_id(resid)
					if publish_date:
						ins = db_conn.query(KC_LIST).filter(KC_LIST.game_id==resid).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('coolpad')).first()
						if ins is None:
							count += 1
							item = KC_LIST(**{
										"title": title,
										"game_id": resid,
										"title2": resid,
										"game_type": game_type,
										"publish_date": publish_date,
										"img": img,
										"popular": popular,
										"source": source_map.get('coolpad')
										})
							db_conn.merge(item)
						else:
							ins.game_id = resid
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	mylogger.info("get %s records from coolpad" % count)
	db_conn.commit()


def get_coolpad_pubtime_by_id(resid):
	url = "http://gamecenter.coolyun.com/gameAPI/API/getDetailResInfo?key=0"
	raw_data = """<?xml version="1.0" encoding="utf-8"?>
<request username="" cloudId="" openId="" sn="865931027730878" platform="1" platver="19" density="480" screensize="1080*1920" language="zh" mobiletype="MI4LTE" version="4" seq="0" appversion="3350" currentnet="WIFI" channelid="coolpad" networkoperator="46001" simserianumber="89860115851040101064">
  <resid>%s</resid>
</request>""" % resid
	try:
		r = requests.post(url, data=raw_data, headers={'Content-Type': 'application/xml'})
		if r.status_code == 200:
			t = re.sub(u'\r|\n', '', r.text)
			doc = xmltodict.parse(t)
			d = doc['response']['reslist']['res']
			pubtime = d.get('pubtime', u'')
			if pubtime is not None:
				m = re.search(u'\d+-\d+-\d+', pubtime)
				if m is not None:
					dt = datetime.datetime.strptime(m.group(), '%Y-%m-%d')
					return unicode(dt.date())
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	return u''

def get_gionee_kc(page):
	count = 0
	url = "http://game.gionee.com/Api/Local_Rank/clientIndex?&page=%s" % page
	try:
		r = requests.get(url, timeout=10)
		if r.status_code == 200:
			d = r.json()
			for ret in d['data']['list']:
				title = ret.get('name', u'')
				img = ret.get('img', u'')
				score = ret.get('score', u'')
				game_id = ret.get('gameid', u'')
				game_type = ret.get('category', u'')
				dt = ret.get('date', u'')
				m = re.search(u'(\d+)月(\d+)日', dt)
				publish_date = u''
				try:
					if m.group(1) == u'12':
						publish_date = u"2015-%s-%s" % (m.group(1), m.group(2))
					else:
						publish_date = u"%s-%s-%s" % (datetime.date.today().year, m.group(1), m.group(2))
				except Exception, e:
					mylogger.error("### %s ###\t%s" % (dt.encode('utf-8'), traceback.format_exc()))
				if publish_date and game_id:
					ins = db_conn.query(KC_LIST).filter(KC_LIST.game_id==game_id).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('gionee')).first()
					if ins is None:
						count += 1
						item = KC_LIST(**{
										"title": title,
										"title2": game_id,
										"game_id": game_id,
										"game_type": game_type,
										"publish_date": publish_date,
										"img": img,
										"source": source_map.get('gionee')
										})
						db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	mylogger.info("get %s records from gionee" % count)
	db_conn.commit()

def get_lenovo_kc():
	count = 0
	urls = ["http://yx.lenovomm.com/business/app!getNewest.action?width=1080&t=22&s=0&dpi=480&height=1920", "http://yx.lenovomm.com/business/app_category!getTest.action?dpi=480&height=1920&dev=ph&width=1080&t=20&s=0"]
	try:
		for url in urls:
			r = requests.get(url, timeout=10)
			if r.status_code == 200:
				d = r.json()
				for ret in d['datalist']:
					title = ret.get('name', u'')
					game_type = ret.get('categoryName', u'')
					img = ret.get('iconAddr', u'')
					publishDate= ret.get('publishDate', u'')
					popular = ret.get('downloadCount', u'')
					pkg_name = ret.get('packageName', u'')
					if publishDate and pkg_name:
						publish_date = unicode(datetime.date.fromtimestamp(int(unicode(publishDate)[:-3])))
						ins = db_conn.query(KC_LIST).filter(KC_LIST.pkg_name==pkg_name).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('lenovo')).first()
						if ins is None:
							count += 1
							item = KC_LIST(**{
											"title": title,
											"title2": pkg_name,
											"pkg_name": pkg_name,
											"game_type": game_type,
											"publish_date": publish_date,
											"popular": popular,
											"img": img,
											"source": source_map.get('lenovo')
											})
							db_conn.merge(item)
						else:
							ins.title2 = ret.get('packageName', u'')
							ins.pkg_name = ret.get('packageName', u'')
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	mylogger.info("get %s records from lenovo" % count)
	db_conn.commit()
				

def get_iqiyi_kc(page):
	count = 0
	url = "http://store.iqiyi.com/gc/list?callback=rs&id=228&no=%s" % page
	try:
		r = requests.get(url, timeout=10)
		if r.status_code == 200:
			m = re.search(u'rs\\(([\s\S]*)\\)\\;', r.text)
			if m is not None:
				d = json.loads(m.group(1))
				for ret in d['list']:
					title = ret.get('name', u'')
					img = ret.get('icon', u'')
					game_type = ret.get('cate_name', u'')
					qipu_id = ret.get('qipu_id', u'')
					popular = ret.get('cnt', u'')
					if qipu_id:
						publish_date = get_iqiyi_pubtime_by_id(qipu_id)
						if publish_date:
							ins = db_conn.query(KC_LIST).filter(KC_LIST.game_id==qipu_id).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('iqiyi')).first()
							#ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.title2==qipu_id).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('iqiyi')).first()
							if ins is None:
								count += 1
								item = KC_LIST(**{
												"title": title,
												"title2": qipu_id,
												"game_id": qipu_id,
												"game_type": game_type,
												"publish_date": publish_date,
												"popular": popular,
												"img": img,
												"source": source_map.get('iqiyi')
												})
								db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	mylogger.info("get %s records from iqiyi" % count)
	db_conn.commit()
						
					
def get_iqiyi_pubtime_by_id(qipu_id):
	url = "http://store.iqiyi.com/gc/game/detail?callback=rs&id=%s" % qipu_id
	try:
		r = requests.get(url)
		if r.status_code == 200:
			m = re.search(u'rs\\(([\s\S]*)\\)\\;', r.text)
			if m is not None:
				d = json.loads(m.group(1))
				dt = d['app']['date']
				m = re.search(u'(\d+)年(\d+)月(\d+)日', dt)
				try:
					publish_date = u"%s-%s-%s" % (m.group(1), m.group(2), m.group(3))
					return publish_date
				except Exception, e:
					mylogger.error("### %s ###\t%s" % (dt.encode('utf-8'), traceback.format_exc()))
	except Exception, e:
		if isinstance(qipu_id, int):
			qipu_id = str(qipu_id)
		if isinstance(qipu_id, unicode):
			qipu_id = qipu_id.encode('utf-8')
		mylogger.error("### get iqiyi %s pubtime error ###\t%s" % (qipu_id, traceback.format_exc()))
	return u''	
	
def get_youku_kc():
	count = 0
	url = "http://api.gamex.mobile.youku.com/app/new_game_tab/get?pg=1&pz=40"
	try:
		r = requests.get(url, timeout=10)
		if r.status_code == 200:
			d = r.json()
			for ret in d['games']:
				publish_date = ret.get('apk_update_time', u'')
				popular = ret.get('total_downloads', u'')
				title = ret.get('appname', u'')
				game_type = ret.get('type', u'')
				img = ret.get('logo', u'')
				game_id = ret.get('id', u'')
				if publish_date and game_id:
					ins = db_conn.query(KC_LIST).filter(KC_LIST.game_id==game_id).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('youku')).first()
					#ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.title2==game_id).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('youku')).first()
					if ins is None:
						count += 1
						item = KC_LIST(**{
										"title": title,
										"title2": game_id,
										"game_id": game_id,
										"game_type": game_type,
										"publish_date": publish_date,
										"popular": popular,
										"img": img,
										"source": source_map.get('youku')
										})
						db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	mylogger.info("get %s records from youku" % count)
	db_conn.commit()

def get_wandoujia_kc():
	count = 0
	urls = ["http://apis.wandoujia.com/apps/v1/topics/smart150/list?start=0&max=15", "http://apis.wandoujia.com/apps/v1/topics/smart438/list?start=0&max=15"]
	try:
		for url in urls:
			r = requests.get(url, timeout=20)
			if r.status_code == 200:
				d = r.json()
				for ret in d['entity']:
					title = ret.get('title', u'')
					action = ret.get('action', u'')
					img = ret.get('icon', u'')
					if action is not None:
						detail_url = action.get('url', u'')
						if detail_url:
							detail = get_wandoujia_detail(detail_url)	
							if detail is not None:
								game_type, popular, publish_date = detail
								if publish_date:
										ins = db_conn.query(KC_LIST).filter(KC_LIST.url==detail_url).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('wandoujia')).first()
										if ins is None:
											count += 1
											item = KC_LIST(**{
															"title": title,
															"url": detail_url,
															"game_type": game_type,
															"publish_date": publish_date,
															"popular": popular,
															"img": img,
															"source": source_map.get('wandoujia')
															})
											db_conn.merge(item)
	except Exception,e:
		mylogger.error("### %s ### %s" % (url, traceback.format_exc()))
	mylogger.info("get %s records from wandoujia" % count)
	db_conn.commit()

def get_wandoujia_detail(url):
	try:
		r = requests.get(url, timeout=30)
		if r.status_code == 200:
			d = r.json()
			entity = d['entity']
			if entity:
				detail = entity[0]['detail']['appDetail']
				if detail is not None:
					categories = detail.get('categories', [])
					game_type = u",".join([c['name'] for c in categories if c['level']==1])
					popular = detail.get('downloadCount', u'')
					publishtime = detail.get('publishDate', u'')
					publish_date = unicode(datetime.date.fromtimestamp(int(unicode(publishtime)[:10]))) if publishtime else u""
					return game_type, popular, publish_date
	except Exception,e:
		mylogger.error("### %s ### %s" % (url.encode('utf-8'), traceback.format_exc()))
	return None
		

def get_sogou_kc():
	count = 0
	url = "http://mobile.zhushou.sogou.com/android/rank/toplist.html?limit=25&start=0&group=2&id=13"
	try:
		r = requests.get(url, timeout=10)
		if r.status_code == 200:
			d = r.json()
			for ret in d['recommend_app']:
				img = ret.get('icon', u'')
				title = ret.get('name', u'')
				popular = ret.get('downloadCount', u'')
				game_type = ret.get('category_name', u'')
				dt = ret.get('date', u'')
				game_id = ret.get('appid', u'')
				if dt and game_id:
					publish_date = dt[:11]
					ins = db_conn.query(KC_LIST).filter(KC_LIST.game_id==game_id).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('sogou')).first()
					if ins is None:
						count += 1
						item = KC_LIST(**{
										"title": title,
										"title2": game_id,
										"game_id": game_id,
										"game_type": game_type,
										"publish_date": publish_date,
										"popular": popular,
										"img": img,
										"source": source_map.get('sogou')
										})
						db_conn.merge(item)
					else:
						ins.title2 = ret.get('appid', u'')
						ins.game_id = ret.get('appid', u'')
	except Exception,e:
		mylogger.error("### %s ### %s" % (url, traceback.format_exc()))
	mylogger.info("get %s records from sogou" % count)
	db_conn.commit()
			
def get_dangle_kc():
	count = 0
	url = "http://api2014.digua.d.cn/newdiguaserver/netgame/memorabilia"
	
	headers = {"HEAD": {
    #"stamp": 1446714106000,
    "stamp": 1446712885154,
    "verifyCode": "78492ba9e8569f3b9d9173ac4e4b6cb9",
    "it": 2,
    "resolutionWidth": 1080,
    "imei": "865931027730878",
    "clientChannelId": "100327",
    "versionCode": 750,
    "mac": "34:80:b3:4d:69:87",
    "vender": "Qualcomm",
    "vp": "",
    "version": "7.5",
    "sign": "8bb4d72622576380",
    "dd": 480,
    "sswdp": "360",
    "hasRoot": 0,
    "glEsVersion": 196608,
    "device": "MI_4LTE",
    "ss": 2,
    "local": "zh_CN",
    "language": "2",
    "sdk": 19,
    "resolutionHeight": 1920,
    "osName": "4.4.4",
    "gpu": "Adreno (TM) 330"
	}}
	try:
		r = requests.post(url, headers=headers, timeout=15)
		if r.status_code == 200:
			d = r.json()
			for ret in d['list']:
				game_type = ret.get('categoryName', u'')
				publish_status = ret.get('operationStatus', u'')
				title = ret.get('name', u'')
				publishtime = ret.get('activityDate', u'')
				publish_date = unicode(datetime.date.fromtimestamp(int(unicode(publishtime)[:10]))) if publishtime else u""
				img = ret.get('iconUrl', u'')
				game_id = ret.get('id', u'')
				if publish_date and game_id:
					ins = db_conn.query(KC_LIST).filter(KC_LIST.game_id==game_id).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('dangle')).first()
					if ins is None:
						count += 1
						item = KC_LIST(**{
										"title": title,
										"title2": game_id,
										"game_id": game_id,
										"game_type": game_type,
										"publish_status": publish_status,
										"publish_date": publish_date,
										"img": img,
										"source": source_map.get('dangle')
										})
						db_conn.merge(item)
	except Exception,e:
		mylogger.error("### get dangle kc ### %s" % (traceback.format_exc()))
	mylogger.info("get %s records from dangle" % count)
	db_conn.commit()
				
def get_i4_kc(page):
	count = 0
	url = "http://app3.i4.cn/controller/action/online.go?store=3&module=3&rows=20&sort=2&submodule=6&model=101&id=0&reqtype=3&page=%s" % page
	try:
		r = requests.get(url, timeout=20)
		if r.status_code == 200:
			d = r.json()
			for ret in d['result']['list']:
				game_type = ret.get('typeName', u'')
				title = ret.get('appName', u'')
				game_id = ret.get('id', u'')
				popular = ret.get('downloadCount', u'')
				newUpdateTime = ret.get('newUpdateTime', u'')
				img = u'http://d.image.i4.cn/image/%s' % ret.get('icon', u'')
				publish_date = newUpdateTime[:10] if newUpdateTime else u''
				ins = db_conn.query(KC_LIST).filter(KC_LIST.game_id==game_id).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('i4')).first()
				if ins is None:
					count += 1
					item = KC_LIST(**{
									"title": title,
									"title2": game_id,
									"game_id": game_id,
									"game_type": game_type,
									"publish_date": publish_date,
									"img": img,
									"popular": popular,
									"source": source_map.get('i4')
									})
					db_conn.merge(item)
	except Exception,e:
		mylogger.error("### %s ### %s" % (url, traceback.format_exc()))
	mylogger.info("get %s records from i4" % count)
	db_conn.commit()

def get_i4_detail_by_id():
	url = "http://app3.i4.cn/controller/action/online.go?store=3&module=1&id=253283&reqtype=5"


def get_muzhiwan_kc():
	count = 0
	URL = "http://www.muzhiwan.com/wangyou/kaice/"
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			today_kc_list = soup.find('ul', class_='td_del hot_list')
			if today_kc_list is not None:
				for li in today_kc_list.find_all('li', class_='clearfix li_contents_list'):
					title = u''
					pkg_name = u''
					game_type = u''
					publish_status = u''
					img = u''
					tag_td = li.find('div', class_='tag tag_td')
					if tag_td is not None and tag_td.find('a') is not None:
						title = tag_td.find('a').text
						pkg_name = tag_td.find('a').get('href')
					fl = li.find('div', class_='fl')
					if fl is not None and fl.find('a') is not None:
						if fl.find('a').find('img') is not None:
							img = fl.find('a').find('img').get('src')
					publish_status_div = soup.find('div', class_='fl pl10 ')
					if publish_status_div is not None:
						for g in publish_status_div.find_all('p'):
							segs = re.sub('\s+', u'', g.text).split(':')
							if len(segs) == 2:
								if segs[0] == u'游戏状态':
									publish_status = segs[1]
								if segs[0] == u'游戏类型':
									game_type = segs[1]
					if pkg_name:
						count += 1
						url = u"http://www.muzhiwan.com%s" % pkg_name
						publish_date = unicode(datetime.date.today())
						ins = db_conn.query(KC_LIST).filter(KC_LIST.url==url).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('muzhiwan')).first()
						if ins is None:
							count += 1
							item = KC_LIST(**{
									"title": title,
									"url": url,
									"game_type": game_type,
									"publish_status": publish_status,
									"publish_date": publish_date,
									"img": img,
									"source": source_map.get('muzhiwan')
									})
							db_conn.merge(item)
						else:
							ins.img = img
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from muzhiwan" % count)
	db_conn.commit()


def get_muzhiwan_kc_v1(page):
	count = 0
	#URL = "http://www.muzhiwan.com/category/12/"
	URL = "http://www.muzhiwan.com/category/12/new-0-0-%s.html" % page
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			ul = soup.find('ul', class_="gamelist pt10 pb20 pl10")
			if ul is not None:
				for ret in ul.find_all('li'):
					detail = ret.find('a')
					comments_div = ret.find('div').find('span')
					popular = u'0'
					if comments_div is not None and u'评论数' in comments_div.text:
						m = re.search(u'(\d+)个', comments_div.text)
						popular = m.group(1) if m is not None else u'0'
					if detail is not None:
						_img = detail.find('img')
						if _img is not None:
							title = _img.get('alt')
							img = _img.get('lazy-src')
							info = get_muzhiwan_detail(detail.get('href'))
							url = detail.get('href')
							if u'发布' in info:
								publish_date = info.get(u'发布', u'')
								if publish_date and url is not None:
									ins = db_conn.query(KC_LIST).filter(KC_LIST.url==url).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('muzhiwan')).first()
									if ins is None:
										count += 1
										item = KC_LIST(**{
												"title": title,
												"url": url,
												"title2": info.get('title2', u''),
												"game_type": info.get(u'分类', u''),
												"publish_date": info.get(u'发布', u''),
												"img": img,
												"popular": popular,
												"source": source_map.get('muzhiwan')
												})
										db_conn.merge(item)
									else:
										ins.url = detail.get('href')
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from muzhiwan" % count)
	db_conn.commit()

def get_muzhiwan_detail(url):
	mydict = {}
	try:
		response = s.get(url, timeout=10)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			info = soup.find('div', class_='detail_info')
			if info is not None:
				game_name = info.find('div', class_='game_name')
				title2 = game_name.find('h1').text if game_name is not None else u''
				mydict[u'title2'] = title2
				for ret in info.find('div', class_='clearfix').find_all('li'):
					segs = ret.text.split(u'：')
					if len(segs) == 2:
						mydict[segs[0]] = segs[1]
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	return mydict

def get_huawei_kc(page):
	count = 0
	URL = "http://appstore.huawei.com/game/list_2_1_%s" % page
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			unit_list = soup.find('div', class_='unit-main')
			if unit_list is not None:
				for unit in unit_list.find_all('div', class_='list-game-app dotline-btn nofloat'):
					title = u""
					publish_date = u""
					img = u""
					url = u""
					popular = u""
					info_ico_div = unit.find('div',class_='game-info-ico')
					if info_ico_div is not None:
						if info_ico_div.find('a') is not None:
							url = info_ico_div.find('a').get('href')
						img_div = info_ico_div.find('img')
						if img_div is not None:
							title = img_div.get('title')
							if img_div.get('lazyload') is not None:
								img = img_div.get('lazyload')
					date_p = unit.find('p', class_='date')	
					if date_p is not None:
						date_span = date_p.find('span')
						if date_span is not None:
							publish_date = date_span.text.split(u'：')[1].strip()
							if publish_date and title:
								download_div = unit.find('div', class_="app-btn")
								if download_div is not None:
									if len(download_div.find_all('span'))==2:
										download_span = download_div.find_all('span')[1]
										m = re.search('\d+', download_span.text)
										popular = m.group() if m is not None else u''
								#print publish_date, title, popular, img
								ins = db_conn.query(KC_LIST).filter(KC_LIST.url==url).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('huawei')).first()
								if ins is None:
									count += 1
									item = KC_LIST(**{
												"title": title,
												"publish_date": publish_date,
												"img": img,
												"url": url,
												"popular": popular,
												"source": source_map.get('huawei')
												})
									db_conn.merge(item)
								else:
									ins.url = url
									ins.img = img
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from huawei" % count)
	db_conn.commit()
				

def get_kuaiyong_kc(page):
	count = 0
	URL = "http://app.kuaiyong.com/list/index/appType/game/page/%s" % page
	try:
		response = s.get(URL, timeout=30)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			for ret in soup.find_all('div', class_="app-item"):
				item_icon = ret.find('a', class_="app-item-icon")
				if item_icon is not None:
					img_div = item_icon.find('img')
					img = img_div.get('data-src') if img_div is not None else u''
					detail_url = u"http://app.kuaiyong.com%s" % item_icon.get('href')
					if detail_url:
						info = get_kuaiyong_detail(detail_url)
						if u'时　　间' in info:
							title = info.get('title', u'')
							publish_date = info.get(u'时　　间', u'')
							ins = db_conn.query(KC_LIST).filter(KC_LIST.url==detail_url).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('kuaiyong')).first()
							if ins is None:
								count += 1
								item = KC_LIST(**{
												"title": title,
												"publish_date": publish_date,
												"img": img,
												"url": detail_url,
												"game_type": info.get(u'类　　别', u''),
												"popular": info.get(u'下载', u''),
												"source": source_map.get('kuaiyong')
												})
								db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from kuaiyong" % count)
	db_conn.commit()
						

def get_kuaiyong_detail(URL):
	mydict = {}
	try:
		response = s.get(URL, timeout=30)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			base_right = soup.find('div', class_='base-right')
			mydict = {}
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

def get_itools_kc():
	count = 0
	URL = "http://ios.itools.cn/game/iphone/gameall_3_1"
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			ul = soup.find('ul', class_='ios_app_list')
			if ul is not None:
				for app in ul.find_all('li'):
					app_on = app.find('div', class_='ios_app_on')
					if app_on is not None:
						detail_url = app_on.find('a').get('href') if app_on.find('a') is not None else u''
						if detail_url:
							detail_url = u"http://ios.itools.cn%s" % detail_url
							info = get_itools_detail(detail_url)
							if 'title' in info and u'更新时间' in info:
								title = info.get('title', u'')
								dt = info.get(u'更新时间', u'')
								if title and dt:
									publish_date = re.sub(u'年|月|日', u'-', dt)[:-1]
									#print title, publish_date
									ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('itools')).first()
									if ins is None:
										count += 1
										item = KC_LIST(**{
														"title": title,
														"publish_date": publish_date,
														"img": info.get('img', u''),
														"url": detail_url,
														"game_type": info.get(u'标       签', u''),
														"source": source_map.get('itools')
														})
										db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from itools" % count)
	db_conn.commit()

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

def get_anzhi_kc(page):
	count = 0
	URL = "http://www.anzhi.com/list_2_%s_new.html" % page
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			app_list = soup.find('div', 'app_list border_three')
			if app_list is not None:
				for app in app_list.find_all('div', class_='app_info'):
					app_name = app.find('span', class_='app_name')
					if app_name is not None:
						title_a = app_name.find('a')
						if title_a is not None:
							detail_url = u"http://www.anzhi.com%s" % title_a.get('href')
							title = title_a.text
							info = get_anzhi_detail(detail_url)
							if u'时间' in info:
								dt = info.get(u'时间', u'')
								if title and dt:
									publish_date = re.sub(u'年|月|日', u'-', dt)[:-1]
									ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('anzhi')).first()
									if ins is None:
										count += 1
										item = KC_LIST(**{
														"title": title,
														"publish_date": publish_date,
														"img": info.get('img', u''),
														"url": detail_url,
														"popular": info.get(u'下载', u''),
														"game_type": info.get(u'分类', u''),
														"source": source_map.get('anzhi')
														})
										db_conn.merge(item)
									else:
										ins.popular = info.get(u'下载', '')
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from anzhi" % count)
	db_conn.commit()

def get_anzhi_detail(URL):
	mydict = {}
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			detail_icon = soup.find('div', class_='detail_icon')
			if detail_icon is not None:
				img_div = detail_icon.find('img')
				if img_div is not None:
					mydict['img'] = u"http://www.anzhi.com%s" % img_div.get('src')
			detail_line_ul = soup.find('ul', id='detail_line_ul')
			if detail_line_ul is not None:
				for li in detail_line_ul.find_all('li'):
					segs = li.text.split(u'：')
					if len(segs) == 2:
						mydict[segs[0]] = segs[1]
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	return mydict

def get_360_web_kc(page):
	count = 0
	URL = "http://zhushou.360.cn/list/index/cid/2/order/newest/?page=%s" % page
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
		#pg = get_page_source_by_phantomjs(URL)
		#if pg:
			#soup = BeautifulSoup(pg)
			soup = BeautifulSoup(response.text)
			iconList = soup.find('ul', 'iconList')
			if iconList is not None:
				for li in iconList.find_all('li'):
					title = u''
					publish_date = li.find('span').text if li.find('span') is not None else u''
					img = u''
					if li.find('h3') is not None:
						if li.find('h3').find('a') is not None:
							title = li.find('h3').find('a').text
					if title and publish_date:
						if li.find('a') is not None:
							img  = li.find('a').find('img').get('_src')
							if li.find('a').get('href') is not None:
								_url = u"http://zhushou.360.cn%s" % li.find('a').get('href')
								ins = db_conn.query(KC_LIST).filter(KC_LIST.url==_url).filter(KC_LIST.source==source_map.get('360zhushou_web')).filter(KC_LIST.publish_date==publish_date).first()
								if not ins:
									count += 1
									item = KC_LIST(**{
													'publish_date':publish_date,
													'title':title,
													'img':img,
													'url':_url,
													'source':source_map.get('360zhushou_web'),
														})
									db_conn.merge(item)
								else:
									ins.img = img
									ins.last_update = datetime.datetime.now()
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from 360 zhushou web page %s" % (count, page))
	db_conn.commit()
				

def get_pp_kc(page):
	count = 0
	headers = {'tunnel-command':4261421088}
	try:
		j = {"dcType":0, "resType":2, "listType":0, "catId":0, "clFlag":1, "perCount":32, "page": page}
		r = requests.post('http://jsondata.25pp.com/index.html', timeout=20, data=json.dumps(j), headers=headers)
		if r.status_code == 200:
			content = re.sub(u'\ufeff', u'', r.text)
			d = json.loads(content)
			for g in d['content']:
				game_id = g.get('id', u'')
				if game_id:
					detail = get_pp_detail_by_id(game_id)
					title = g.get('title', u'')
					updatetime = g.get('updatetime', u'')
					publish_date = unicode(datetime.date.fromtimestamp(updatetime))
					ins = db_conn.query(KC_LIST).filter(KC_LIST.game_id==game_id).filter(KC_LIST.source==source_map.get('pp')).filter(KC_LIST.publish_date==publish_date).first()
					if not ins:
						count += 1
						item = KC_LIST(**{
										'publish_date':publish_date,
										'title':title,
										'game_type': detail.get('catName', u''),
										'game_id': game_id,
										'title2': game_id,
										'img': g.get('thumb', u''),
										'source':source_map.get('pp'),
										'popular' : g.get('downloads', u'')
											})
						db_conn.merge(item)
	except Exception,e:
		mylogger.error("get pp kc list\t%s" % (traceback.format_exc()))
	mylogger.info("get %s records from pp %s" % (count, page))
	db_conn.commit()


def get_pp_detail_by_id(game_id):
	try:
		d = {"site":1, "id": game_id}
		r = requests.post('http://pppc2.25pp.com/pp_api/ios_appdetail.php', data=d)
		if r.status_code == 200:
			return r.json()
	except Exception,e:
		if isinstance(game_id, unicode):
			game_id = game_id.encode('utf-8')
		mylogger.error("get %s detail \t%s" % (game_id, traceback.format_exc()))
	return {}

def get_meizu_kc():
	count = 0
	URL = "http://api-game.meizu.com/games/public/new/layout?start=0&max=50"
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
			j = response.json() 
			if j.get('code', 9527) == 200:
				blocks = j['value']['blocks']
				if blocks:
					for rt in blocks[0]['data']:
						title = rt.get('name', u'')
						game_id = rt.get('id', 0)
						detail = get_meizu_detail_by_id(game_id)
						if title and game_id and detail is not None:
							version_time = detail.get('version_time', u'')
							if version_time and game_id:
								publish_date = unicode(datetime.date.fromtimestamp(int(unicode(version_time)[:10])))
								ins = db_conn.query(KC_LIST).filter(KC_LIST.game_id==game_id).filter(KC_LIST.source==source_map.get('meizu')).filter(KC_LIST.publish_date==publish_date).first()
								if not ins:
									count += 1
									item = KC_LIST(**{
												'publish_date': publish_date,
												'title': rt.get('name', u''),
												'game_type': rt.get('category_name', u''),
												'title2': game_id,
												'game_id': game_id,
												'img': rt.get('icon', u''),
												'source': source_map.get('meizu'),
												'popular' : rt.get('download_count', u'')
													})
									db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from meizu " % (count))
	db_conn.commit()
		

def get_meizu_detail_by_id(game_id):
	URL = "http://api-game.meizu.com/games/public/detail/%s" % game_id
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
			j = response.json()
			if 'value' in j:
				return j['value']
	except Exception,e:
		mylogger.error("%s" % (traceback.format_exc()))
	return None


def get_xyzs_kc(page):
	count = 0
	URL = "http://interface.xyzs.com/v2/ios/c01/game/latest?p=%s&ps=20" % page
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
			j = response.json() 
			if j.get('code') == 200:
				if 'data' in j:
					for rt in j['data'].get('result', []):
						title = rt.get('title', u'')
						addtime = rt.get('addtime', u'')
						game_id = rt.get('itunesid', 0)
						#detail = get_xyzs_detail_by_id(gid)
						if addtime and game_id:
							# addtime字段内容不一定正确，日期会异常
							#game_type = detail.get('apptypesno', u'') if detail is not None else u''
							publish_date = unicode(datetime.date.fromtimestamp(int(addtime)))
							ins = db_conn.query(KC_LIST).filter(KC_LIST.game_id==game_id).filter(KC_LIST.source==source_map.get('xyzs')).filter(KC_LIST.publish_date==publish_date).first()
						if not ins:
							count += 1
							item = KC_LIST(**{
											'publish_date': publish_date,
											'title': title,
											'title2': game_id,
											'game_id': game_id,
											'img': rt.get('icon', u''),
											'source': source_map.get('xyzs'),
											'popular' : rt.get('downloadnum', u'')
												})
							db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from xyzs " % (count))
	db_conn.commit()

def get_91play_detail_by_id(game_id):
	URL = "http://play.91.com/api.php/Api/index"
	try:
		raw_data = {"id": game_id,"firmware":"19","time":1449458211590,"device":1,"action":30005,"app_version":302,"action_version":4,"mac":"7b715ce093480b34d6987","debug":0}
		response = requests.post(URL, data=raw_data, timeout=10)
		if response.status_code == 200:
			j = response.json() 
			if j['data'] is not None:
				return json.loads(j['data'])
	except Exception,e:
		mylogger.error("91play %s detail\t%s" % (game_id, traceback.format_exc()))
	return None
		

def get_91play_kc():
	count = 0
	URL = "http://play.91.com/api.php/Api/index"
	try:
		raw_data = {"id":2,"firmware":"19","time":1449455693994,"index":0,"device":1,"action":30002,"app_version":302,"action_version":4,"mac":"7b715ce093480b34d6987","debug":0,"size":20}
		response = requests.post(URL, data=raw_data, timeout=10)
		if response.status_code == 200:
			j = response.json() 
			if j['data'] is not None:
				for rt in json.loads(j['data']):
					game_id = rt.get('id', 0)
					detail = get_91play_detail_by_id(game_id)
					#for k, v in detail.iteritems():
					#	print k,v
					if detail is not None:
						title = detail.get('name', u'')
						update_time = detail.get('update_time', u'')
						if update_time and title:
							publish_date = unicode(datetime.date.fromtimestamp(int(update_time)))
							#print title, publish_date
							ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.source==source_map.get('91play')).filter(KC_LIST.publish_date==publish_date).first()
							if not ins:
								count += 1
								item = KC_LIST(**{
												'publish_date': publish_date,
												'title': title,
												'title2': game_id,
												'game_id': game_id,
												'img': rt.get('icon_url', u''),
												'source': source_map.get('91play'),
												'popular' : rt.get('download_count', u'')
													})
								db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from 91play " % (count))
	db_conn.commit()


def get_360_gamebox_kc(start):
	count = 0
	URL = "http://next.gamebox.360.cn/7/xgamebox/newzone?count=20&start=%s&type=ontest" % start
	try:
		response = requests.get(URL, timeout=10)
		if response.status_code == 200:
			j = response.json() 
			if j.get('errno') == 0 and j['data'] is not None:
				for rt in j['data']:
					#for k, v in rt.iteritems():
					#	print k, v
					publish_date = u''
					title = rt.get('name', u'')
					kc_state = rt.get('state')
					pkg_name = rt.get('apkid', u'')
					if kc_state is not None:
						open_time_human = kc_state.get('open_time_human', u'')
						if open_time_human:
							try:
								m = re.search(u'(\d+)月(\d+)日', open_time_human)
								if m.group(1) == u'12':
									str_dt = u"2015-%s-%s" % (m.group(1), m.group(2))
								else:
									str_dt = u"%s-%s-%s" % (unicode(datetime.date.today().year), m.group(1), m.group(2))
								dt = datetime.datetime.strptime(str_dt, '%Y-%m-%d')
								publish_date = unicode(dt.date())
							except Exception, e:
								mylogger.error("### gamebox open time %s ###\t%s" % (title.encode('utf-8'), traceback.format_exc()))
					if pkg_name and publish_date:
						ins = db_conn.query(KC_LIST).filter(KC_LIST.pkg_name==pkg_name).filter(KC_LIST.source==source_map.get('360_gamebox')).filter(KC_LIST.publish_date==publish_date).first()
						if not ins:
							count += 1
							item = KC_LIST(**{
										'publish_date': publish_date,
										'title': rt.get('name', u''),
										'game_type': rt.get('category_name', u''),
										'title2': pkg_name,
										'pkg_name': pkg_name,
										'game_id': rt.get('id', u''),
										'img': rt.get('logo_url', u''),
										'source': source_map.get('360_gamebox'),
										'popular' : rt.get('download_times', u'')
											})
							db_conn.merge(item)
						else:
							ins.game_id = rt.get('id', u'')
							ins.pkg_name = rt.get('apkid', u'')
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from 360_gamebox " % (count))
	db_conn.commit()


def get_lenovo_shop_kc(page):
	count = 0
	headers = {"clientid": "141623-2-2-19-1-3-1_480_i865931027730878t19700201770903586_c20524d1p1"}
	url = "http://223.202.25.30/ams/api/applist?l=zh-CN&si=%s&c=20&lt=subject&cg=subject&code=21568&nremark=1&pa=ams5.0_7402535-2-2-22-1-3-1_480-8" % page
	try:
		r = requests.get(url, timeout=10,headers=headers)
		if r.status_code == 200:
			d = r.json()
			if d['datalist'] is not None:
				for ret in d['datalist']:
					title = ret.get('name', u'')
					img = ret.get('iconAddr', u'')
					pkg_name = ret.get('packageName', u'')
					game_type = ret.get('typeName', u'')
					popular = ret.get('downloadCount', u'')
					publishtime = ret.get('publishDate', u'')
					publish_date = u''
					publish_date = unicode(datetime.date.fromtimestamp(int(unicode(publishtime)[:10]))) if publishtime else u""
					if publish_date and pkg_name:
						ins = db_conn.query(KC_LIST).filter(KC_LIST.pkg_name==pkg_name).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('lenovo_shop')).first()
						if ins is None:
							count += 1
							item = KC_LIST(**{
											"title": title,
											"pkg_name": pkg_name,
											"game_type": game_type,
											"publish_date": publish_date,
											"img": img,
											"popular": popular,
											"source": source_map.get('lenovo_shop')
											})
							db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	mylogger.info("get %s records from lenovo" % count)
	db_conn.commit()

def get_wostore_detail_by_id(product_id):
	try:
		headers = {"phoneAccessMode": "3",
				"mac" : "50:a7:2b:33:57:56",
				"version": "android_v4.2.1",
				"Androidversion": "android4.4.2",
				"companylogo": "10269",
				"settertype": "3",
				"handphone": "00000000000"}
		url = "http://clientnew.wostore.cn:6106/appstore_agent/unistore/servicedata.do?serviceid=productDetail&productIndex=%s&resource=null&referer=null" % product_id
		r = requests.get(url, timeout=30, headers=headers)
		if r.status_code == 200 and r.text:
			return r.json()
	except Exception, e:
		if isinstance(product_id, unicode):
			product_id = product_id.encode('utf-8')
		mylogger.error("=== %s ==== wostore detail \t%s" % (product_id, traceback.format_exc()))
	return None

def get_wostore_kc():
	count = 0
	headers = {"phoneAccessMode": "3",
				"mac" : "50:a7:2b:33:57:56",
				"version": "android_v4.2.1",
				"Androidversion": "android4.4.2",
				"companylogo": "10269",
				"settertype": "3",
				"handphone": "00000000000"}
	try:
		url = ""
		r = requests.get("http://clientnew.wostore.cn:6106/appstore_agent/unistore/servicedata.do?serviceid=appList&channel=5&categoryID=0&pageNum=1&count=20", headers=headers, timeout=10)
		if r.status_code == 200:
			j = r.json()
			if j['WOSTORE'] is not None:
				for app in j['WOSTORE']:
					#for k, v in app.iteritems():
					#	print k, v
					product_id = app.get('productIndex', u'')
					if product_id:
						info = get_wostore_detail_by_id(product_id)
						if info is not None:
							updatetime = info.get('updatetime', u'')
							if updatetime:
								publish_date = "%s-%s-%s" % (updatetime[:4], updatetime[4:6], updatetime[6:8])
								#print app.get('appName'), publish_date
								ins = db_conn.query(KC_LIST).filter(KC_LIST.game_id==product_id).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('wostore')).first()
								if ins is None:
									count += 1
									item = KC_LIST(**{
													"title": app.get('appName', u''),
													"game_id": product_id,
													"publish_date": publish_date,
													"img": app.get('iconURL', u''),
													"popular": app.get('downloadCount', u''),
													"source": source_map.get('wostore')
													})
									db_conn.merge(item)
	except Exception,e:
		mylogger.error("get wostore kc \t%s" % (traceback.format_exc()))
	mylogger.info("get %s records from wostore" % count)
	db_conn.commit()

def get_huawei_app_kc():
	count = 0
	url = "http://hispaceclt1.hicloud.com:8080/hwmarket/api/storeApi2"
	headers = {
				'Content-Type': 'text/plain;charset=UTF-8',
				'Postman-Token': '68cc02a1-4403-0c03-0e00-074e7b5eb866',
				
				}
	new_game_raw_data = """clientPackage=com.huawei.gamebox&cno=4010001&code=0500&hcrId=95C3DCD7358A462B8A235DD349C83E6F&isShake=0&iv=6LLe%2F8W1L2r2VfFxvdPRww%3D%3D&maxResults=25&method=client.getTabDetail&net=1&reqPageNum=1&salt=4944739978082606370&serviceType=5&shakeReqPageNum=0&sign=99001011cs11105820000000%403CB547495C4E9571A7B7D641932545CC&trace=97bf368fefad407593b6855b86b8a0c2&ts=1451441383342&uri=f7bdb327d25944009c49e85af1e57720%7C1451441340682&userId=F92BED683CBB555EB76EAC9C534C3C77&ver=1.1&nsp_key=D2N%2F9Keaf0NLsyy6KWzP2EP55jw%3D"""
	kc_raw_data = "clientPackage=com.huawei.gamebox&cno=4010001&code=0500&hcrId=95C3DCD7358A462B8A235DD349C83E6F&isShake=0&iv=ddI%2FExPpnAROsOh8TWli2g%3D%3D&maxResults=25&method=client.getTabDetail&net=1&reqPageNum=1&salt=5608873950279478640&serviceType=5&shakeReqPageNum=0&sign=99001011cs11105820000000%403CB547495C4E9571A7B7D641932545CC&trace=97bf368fefad407593b6855b86b8a0c2%3B4d68256c0cb04a1f8ae6c9a1aae68f8d%7C1451441340694&ts=1451441833594&uri=d055a11c37ee4f76a274b969e308da9c&userId=38C8FB95ACEB81C70973CBD3B53F6E5A&ver=1.1&nsp_key=dtg8h4hm1Fa88DhDPryG7w3mLjQ%3D"
	rds = [new_game_raw_data, kc_raw_data]
	try:
		for raw_data in rds:
			r = requests.post(url, data=raw_data, headers=headers,timeout=10)
			if r.status_code == 200:
				j = r.json()
				if 'layoutData' in j and j['layoutData'] is not None:
					layoutData = j['layoutData']
					if len(layoutData) % 2 == 0:
						for index in xrange(0, len(layoutData), 2):
							items = layoutData[index:index+2]
							title_card = items[0]
							normal_card = items[1]
							if title_card['dataList'] is not None and len(title_card['dataList']) == 1:
								dt = title_card['dataList'][0].get('name')
								if dt == u'今天':
									publish_date = unicode(datetime.date.today())	
									data_list = normal_card['dataList']
									if data_list is not None:
										for app in data_list:
											pkg_name = app.get('package', u'')
											if pkg_name:
												ins = db_conn.query(KC_LIST).filter(KC_LIST.pkg_name==pkg_name).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('huawei_app')).first()
												if ins is None:
													count += 1
													item = KC_LIST(**{
																	"title": app.get('name', u''),
																	"pkg_name": app.get('package', u''),
																	"publish_date": publish_date,
																	"img": app.get('icon', u''),
																	"popular": app.get('downCountDesc', u''),
																	"source": source_map.get('huawei_app')
																	})
													db_conn.merge(item)
								m = re.search(u'(\d+)月(\d+)日', dt)
								if m is not None:
									if m.group(1) == u'12':
										_date = u"2015-%s-%s" % (m.group(1), m.group(2))
									else:
										_date = u"%s-%s-%s" % (datetime.date.today().year, m.group(1), m.group(2))
									publish_date = datetime.datetime.strptime(_date, '%Y-%m-%d')
									publish_date = unicode(publish_date.date())
									data_list = normal_card['dataList']
									if data_list is not None:
										for app in data_list:
											pkg_name = app.get('package', u'')
											if pkg_name:
												ins = db_conn.query(KC_LIST).filter(KC_LIST.pkg_name==pkg_name).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('huawei_app')).first()
												if ins is None:
													count += 1
													item = KC_LIST(**{
																	"title": app.get('name', u''),
																	"pkg_name": app.get('package', u''),
																	"publish_date": publish_date,
																	"img": app.get('icon', u''),
																	"popular": app.get('downCountDesc', u''),
																	"source": source_map.get('huawei_app')
																	})
													db_conn.merge(item)
	except Exception, e:
		mylogger.error("## ## get huawei gamecenter kc \t%s" % (traceback.format_exc()))
	db_conn.commit()

def get_mmstore_detail(url):
	try:
		headers = {
				"appname": "MM5.3.0.001.01_CTAndroid_JT", 
				"ua":"android-19-720x1280-CHE2-UL00"}
		r = requests.get(url, timeout=50, headers=headers)
		if r.status_code == 200:
			return r.json()
	except Exception, e:
		if isinstance(url, unicode):
			url = url.encode('utf-8')
		mylogger.error("## %s ## get mmstore detail \t%s" % (url, traceback.format_exc()))
	return None


def get_mmstore_kc(page):
	count = 0
	url = "http://odp.mmarket.com/t.do?requestid=json_game_new_ranking_library&currentPage=%s&totalRows=5192" % page
	headers = {
				"appname": "MM5.3.0.001.01_CTAndroid_JT", 
				"ua":"android-19-720x1280-CHE2-UL00"}
	try:
		r = requests.get(url, timeout=20, headers=headers)
		if r.status_code == 200:
			j = r.json()
			if j['items'] is not None:
				for app in j['items']:
					detail_url = app.get('detailUrl', u'')
					publish_date = u''
					detail = get_mmstore_detail(app.get('detailUrl'))
					if detail is not None:
						publishtime = detail.get('updateTime', u'')
						publish_date = unicode(datetime.date.fromtimestamp(int(unicode(publishtime)[:10]))) if publishtime else u""
					if publish_date and detail_url:
						ins = db_conn.query(KC_LIST).filter(KC_LIST.url==detail_url).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('mmstore')).first()
						if ins is None:
							count += 1
							item = KC_LIST(**{
											"title": app.get('name', u''),
											"url": detail_url,
											"game_id": app.get('contentId', u''),
											"publish_date": publish_date,
											"img": app.get('iconUrl', u''),
											"popular": app.get('interested', u''),
											"source": source_map.get('mmstore')
											})
							db_conn.merge(item)

	except Exception, e:
		mylogger.error("get mmstore kc \t%s" % (traceback.format_exc()))
	mylogger.info("get %s records from mmstore" % count)
	db_conn.commit()

def get_viv_store_detail_by_id(game_id):
	try:
		prefix = "http://info.appstore.vivo.com.cn/port/package/?source=1&e=150100523832314d4200cf98e451625f&elapsedtime=2563957798&content_complete=1&screensize=1080_1920&density=3.0&pictype=webp&cs=0&av=22&an=5.1&app_version=612&imei=867570026068423&nt=WIFI&module_id=219&target=local&cfrom=103&need_comment=0&model=m2+note&s=2%7C0"
		url = prefix + "&id=%s" % game_id
		r = requests.get(url, timeout=15)
		if r.status_code == 200:
			return r.json()
	except Exception, e:
		mylogger.error("## % ## get vivo store detail \t%s" % (game_id, traceback.format_exc()))
	return None


def get_vivo_store_kc():
	count = 0
	url = "http://main.appstore.vivo.com.cn/topic/topics_soft?source=1&e=150100523832314d4200cf98e451625f&elapsedtime=2563900502&content_complete=0&screensize=1080_1920&density=3.0&pictype=webp&cs=0&req_id=219&av=22&an=5.1&app_version=612&imei=867570026068423&nt=WIFI&id=219&cfrom=32&model=m2+note&s=2%7C0"
	try:
		r = requests.get(url, timeout=20)
		if r.status_code == 200:
			j = r.json()
			if j['value'] is not None:
				for app in j['value']:
					game_id = app.get('id', -1)
					publish_date = u''
					detail = get_viv_store_detail_by_id(game_id)
					if detail is not None and detail['value'] is not None:
						publish_date = detail['value'].get('upload_time', u'')[:11]
					if publish_date and game_id != -1:
						ins = db_conn.query(KC_LIST).filter(KC_LIST.game_id==game_id).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('vivo_store')).first()
						if ins is None:
							count += 1
							item = KC_LIST(**{
											"title": app.get('title_zh', u''),
											"game_id": app.get('id'),
											"publish_date": publish_date,
											"img": app.get('icon_url', u''),
											"popular": app.get('download_count', u''),
											"source": source_map.get('vivo_store')
											})
							db_conn.merge(item)

	except Exception, e:
		mylogger.error("get vivo store kc \t%s" % (traceback.format_exc()))
	mylogger.info("get %s records from vivo_store" % count)
	db_conn.commit()

def get_oppo_kc(start):
	count = 0
	URL = "https://igame.oppomobile.com/gameapp/newGame/recommend?start=%s" % start
	headers = {'sign':'78c0aa34494643c21ed00cde1a703dac', 'param':'imei=868008021943653&model=Che2-UL00&osversion=19'}
	try:
		#response = requests.get(URL, timeout=10)
		response = requests.get(URL, headers=headers, timeout=10)
		if response.status_code == 200:
			rstData = response.json() 
			if rstData['firstGameList'] is not None:
				for rt in rstData['firstGameList']:
					#for k, v in rt.iteritems():
					#	print k, v
					publish_date = unicode(date.today())
					game_name = rt.get('gameName', u'')
					game_id = rt.get('gameId', u'')
					game_pkg_name = rt.get('gamePackageName', u'')
					game_type = rt.get('categoryName', u'')
					game_icon = rt.get('gameIcon', u'')
					game_popular = rt.get('gameDownloadNum', u'');
					game_detail_url = u"https://igame.oppomobile.com/gameapp/game/detail?gameId=%s" % game_id if game_id else u''
					
					if game_pkg_name and publish_date:
						ins = db_conn.query(KC_LIST).filter(KC_LIST.game_id==game_id).filter(KC_LIST.source==source_map.get('oppo_app')).filter(KC_LIST.publish_date==publish_date).first()
						if not ins:
							count += 1
							item = KC_LIST(**{
										'publish_date': publish_date,
										'title': game_name,
										'title2': game_name,
										'game_type': game_type,
										'pkg_name': game_pkg_name,
										'game_id': game_id,
										'img': game_icon,
										'source': source_map.get('oppo_app'),
										'popular' : game_popular,
										'url' : game_detail_url
											}) 
							db_conn.merge(item)
						else:
							ins.game_id = game_id
							ins.pkg_name = game_pkg_name
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from oppo_app " % (count))
	db_conn.commit()

def get_ipaddown_kc():
	count = 0
	URL = "http://www.ipadown.com/new/"
	try:
		response = s.get(URL, timeout=10)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			iconList = soup.find('div', id='content')
			if iconList is not None:
				for li in iconList.find_all('div',class_='app_block'):
					title = u''
					img = u''
					_url = u''
					app_icon = li.find('div', class_='app_icon')
					if app_icon is not None and app_icon.find('img') is not None:
						img = app_icon.find('img').get('src')
						title = app_icon.find('img').get('alt')
					app_info = li.find('div', class_='app_info')
					mydict = {}
					if app_info is not None:
						for info in app_info.find_all('p'):
							segs = info.text.split(u'：')
							if len(segs) == 2:
								mydict[segs[0]] = segs[1]
						if app_info.find('h4') is not None and app_info.find('h4').find('a') is not None:
							_url = app_info.find('h4').find('a').get('href')
					publish_date = mydict.get(u'上架时间', u'')
					if title and publish_date and mydict.get(u'分类', u'') == u'Games':
						ins = db_conn.query(KC_LIST).filter(KC_LIST.url==_url).filter(KC_LIST.source==source_map.get('ipaddown')).filter(KC_LIST.publish_date==publish_date).first()
						if not ins:
							count += 1
							item = KC_LIST(**{
											'publish_date':publish_date,
											'title':title,
											'img':img,
											'url':_url,
											'source':source_map.get('ipaddown'),
												})
							db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from ipaddown page" % count)
	db_conn.commit()

def get_tgbus_kc():
	count = 0
	URL = "http://iphone.tgbus.com/newgame/"
	try:
		r = requests.get(URL, timeout=20)		
		if r.status_code == 200:
			soup = BeautifulSoup(r.text)
			applist = soup.find('div', class_='clist_2 fz14')
			if applist is not None:
				for dl in applist.find_all('dl'):
					img = u''
					_url = u''
					publish_date = u''
					title = u''
					dt = dl.find('dt')
					dd = dl.find('dd')
					if dt is not None:
						img = dt.find('img').get('src')
						_url = dt.find('a').get('href')
					if dd is not None:
						ss = dd.find_all('strong')
						if len(ss) == 2:
							title = ss[1].text
						_date = dd.find('span', class_='txt_ccc fr1').text
						_date = re.sub('/', '-', _date)
						publish_date = unicode(datetime.datetime.strptime(_date, '%Y-%m-%d').date())
					if title and publish_date and publish_date >= u'2016-03-01':
						ins = db_conn.query(KC_LIST).filter(KC_LIST.url==_url).filter(KC_LIST.source==source_map.get('tgbus')).filter(KC_LIST.publish_date==publish_date).first()
						if not ins:
							count += 1
							item = KC_LIST(**{
											'publish_date':publish_date,
											'title':title,
											'img':img,
											'url':_url,
											'source':source_map.get('tgbus'),
												})
							db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from tgbus page" % count)
	db_conn.commit()


def get_4399_detail_by_id(gid):
	url = "http://a.4399.cn/%s" % gid
	mydict= {}
	try:
		r = requests.get(url, timeout=20)		
		if r.status_code == 200:
			soup = BeautifulSoup(r.text)
			m_prop_list = soup.find('ul', class_='m_prop_list')
			if m_prop_list is not None:
				for li in m_prop_list.find_all('li'):
					segs = li.text.split(u'：')
					if len(segs) == 2:
						mydict[segs[0]] = segs[1]
	except Exception,e:
		mylogger.error("%s\t%s" % (gid.encode('utf-8'), traceback.format_exc()))
	return mydict

from get_game_detail_by_day import version_check

def get_4399_kc():
	count = 0
	URL = "http://a.4399.cn/game-new.html"
	try:
		r = requests.get(URL, timeout=20)		
		if r.status_code == 200:
			soup = BeautifulSoup(r.text)
			game_new = soup.find('div', mark='game_new')
			if game_new is not None:
				for li in game_new.find_all('li'):
					title = u''
					img = u''
					img = li.find('img')
					if img is not None:
						title = img.get('alt')
						img = img.get('src')
					m_game = li.find('a', class_='m_game')
					if m_game is not None:
						href = m_game.get('href')
						game_detail = get_4399_detail_by_id(href)
						publish_date = game_detail.get(u'更新', u'')
						version = game_detail.get(u'版本', u'')
						if publish_date and title and version_check(version) and href:
							ins = db_conn.query(KC_LIST).filter(KC_LIST.url==href).filter(KC_LIST.source==source_map.get('4399')).filter(KC_LIST.publish_date==publish_date).first()
							if not ins:
								count += 1
								item = KC_LIST(**{
												'publish_date' 	: publish_date,
												'title'			: title,
												'img'			: img,
												'url'			: href,
												'source':source_map.get('4399'),
													})
								db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from 4399" % count)
	db_conn.commit()


def get_yxhi_info(url):
	try:
		response = requests.get(url, timeout=20)		
		r = response.text.encode('ISO-8859-1').decode('utf-8')
		if response.status_code == 200:
			soup = BeautifulSoup(r)
			for p in soup.find_all('p'):
				is_game = u'游戏' in p.text
				if is_game:
					if u'发布在' in p.text and u'分类' in p.text:
						m = re.search('\d{4}-\d{2}-\d{2}', p.text)
						if m is not None:
							return m.group()
	except Exception,e:
		mylogger.error("%s\t%s" % (url.encode('utf-8'), traceback.format_exc()))
	return None

def get_yxhi_kc():
	count = 0
	URL = "http://ranking.yxhi.com/cn/newlist"
	try:
		response = requests.get(URL, timeout=20)		
		r = response.text.encode('ISO-8859-1').decode('utf-8')
		if response.status_code == 200:
			soup = BeautifulSoup(r)
			tb = soup.find('table', class_='table table-striped')
			if tb is not None:
				for tr in tb.find_all('tr'):
					tr = tr.find('td', style='vertical-align:middle;')
					if tr is not None:
						_url = u''
						href = tr.find('a').get('href')
						game_id = re.search('\d+', href)
						if game_id is not None:
							_url = "https://itunes.apple.com/cn/app/id%s?mt=8" % game_id.group()
						publish_date = get_yxhi_info(href)
						if publish_date and _url:
							title = tr.find('a').text
							img = tr.find('img').get('data-original')
							ins = db_conn.query(KC_LIST).filter(KC_LIST.url==href).filter(KC_LIST.source==source_map.get('yxhi')).filter(KC_LIST.publish_date==publish_date).first()
							if not ins:
								count += 1
								item = KC_LIST(**{
												'publish_date' 	: publish_date,
												'title'			: title,
												'img'			: img,
												'url'			: _url,
												'source':source_map.get('yxhi'),
													})
								db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	mylogger.info("get %s records from yxhi" % count)
	db_conn.commit()

def main():
	mylogger.info("gogo")
	get_18183_kc()
	get_360_kc()
	get_appicsh_kc()
	get_360zhushou_kc()
	get_xiaomi_new_kc(1)
	get_xiaomi_rpg_kc(1)
	get_open_play_kc()
	get_vivo_kc(1)
	get_coolpad_kc()
	get_gionee_kc(1)
	get_lenovo_kc()
	get_iqiyi_kc(1)
	get_youku_kc()
	get_sogou_kc()
	get_dangle_kc()
	get_huawei_kc(1)
	get_kuaiyong_kc(1)
	get_wandoujia_kc()
	get_9game_today_kc()
	get_pp_kc(1)
	get_meizu_kc()
	get_i4_kc(1)
	get_xyzs_kc(1)
	get_xyzs_kc(2)
	get_91play_kc()
	get_360_gamebox_kc(0)
	get_muzhiwan_kc()
	get_lenovo_shop_kc(1)
	get_wostore_kc()
	get_mmstore_kc(1)
	get_vivo_store_kc()
	get_huawei_app_kc()
	get_oppo_kc(0)
	get_tgbus_kc()
	get_4399_kc()
	get_yxhi_kc()
	#get_ipaddown_kc()
	get_360_web_kc(1)
	get_360_web_kc(2)
	get_log_info('kc.log', subject='新品监控')

if __name__ == '__main__':
	main()

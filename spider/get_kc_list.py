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
			"vivo": 8,
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
				}

class T:
	
	def __init__(self, status_code):
		self.status_code = status_code

def get_9game_today_kc():
	URL = u"http://www.9game.cn/kc/"
	mylogger.info("9game gogo")
	try:
		r = s.get(URL, timeout=10)
		#page_ins = db_conn.query(PageSource).filter(PageSource.url==URL).filter(PageSource.source==1).filter(PageSource.create_date==date.today()).first()
		#if not page_ins:
		#	item = PageSource(**{"url":URL, "code":r.text, "source":1})
		#	db_conn.merge(item)
		#	db_conn.commit()
		soup = BeautifulSoup(r.text)
		todayopen = soup.find("div", id="todayOpen").find("span")
		publish_date 	= u"" if todayopen is None else u"2015-%s" %  todayopen.text[1:-1]
		time 		= u""
		title 		= u""
		title2 		= u""
		img 		= u""
		url 		= u""
		device 		= u""
		status 		= u""
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
							status 		= type_div[0].find("span").text
							#game_type 	= type_div[1].find('td')
							#print type_div
							#print re.split(u"：| ", time)[1], status, game_type
						
					if title != "" and status !="":
						ins = db_conn.query(KC_LIST).filter(KC_LIST.source==source_map.get('9game')).filter(KC_LIST.title==title).filter(KC_LIST.status==status).filter(KC_LIST.publish_date==publish_date).first()
						if not ins:
							item = KC_LIST(**{
								"time"		: re.split(u"：| ", time)[1],
								"title" 		: title,
								"title2" 		: title2, 
								"img" 		: img, 
								"url" 		: url, 		
								"device" 		: u",".join(device), 		
								"status" 		: status, 		
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
	URL = "http://xin.18183.com/ceshi/"
	try:
		response = s.get(URL, timeout=10)
		r = response.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(response.text)[0])
		soup = BeautifulSoup(r)
		publish_dates = soup.find("ul", class_="tab_menu").find_all("li")
		tabs = soup.find_all("div", class_="tab_main")
		count = 0
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
							status = t.find("div", class_="pt m6").find("code").text
						#print title, status
							ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.status==status).filter(KC_LIST.source==source_map.get('18183')).first()
							if not ins:
								item = KC_LIST(**{
										"title"		: 	title,
										"url"		: 	url,
										"img" 		:	img,
										"time" 		:	time,
										"device" 	:	",".join(devices),
										"status"	:	status,
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
						status	= u""
						game_type = u""
						tds = tr.find_all("td")
						if tds is not None:
							title = re.sub(u"\xa0", u"", tds[0].text)
							img = u"" if tds[0].find("img") is None else tds[0].find("img").get("src")
							url = u"" if tds[0].find("a") is None else tds[0].find("a").get("href")
							status = tds[1].text
							game_type = tds[3].text
						#print title, url, status, game_type
							ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.status==status).filter(KC_LIST.source==source_map.get('u360')).first()
							if not ins:
								count += 1								
								item = KC_LIST(**{
											"publish_date": publish_date,
											"time": time,
											"title": title,
											"url": url,
											"status": status,
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
	#r = s.get("http://appicsh.qq.com/cgi-bin/appstage/FirstPublishTab?type=3&index=0&pageSize=20")
	url = "http://m5.qq.com/app/applist.htm?listType=18&pageSize=150"
	try:
		r = requests.get(url, timeout=10)
		if r.status_code == 200:
			d = r.json()
			if d['msg'] == u'success':
				new_games_list = d['obj']['appList']
				for game in new_games_list:
					title = game.get('appName', u"")
					game_type = game.get('categoryName', u"")
					img = game.get('iconUrl', u"")
					publishtime = game.get('apkPublishTime', u"")
					publish_date = unicode(datetime.date.fromtimestamp(publishtime)) if publishtime else u""
					#print title, publish_date, img
					if title and publish_date :
						ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('appicsh')).first()
						if ins is None:
							count += 1
							item = KC_LIST(**{
										"title": title,
										"game_type": game_type,
										"publish_date": publish_date,
										"img": img,
										"source": source_map.get('appicsh')
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
		r = s.get(URL)
	except Exception,e:
		r = T(404)
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	if r.status_code == 200:
		soup = BeautifulSoup(r.text)
		item_list = soup.find("div", class_="app-item-list")
		if item_list is not None:
			#logo_list = item_list.find_all('div', class_='app-logo')
			#print logo_list
			app_list = item_list.find_all('div', class_='app-detail')
			for item in app_list:
				title = u""
				game_type = u""
				size = u""
				publish_date = u""
				status = u""
				time = u""
				img = u""
				#if len(logo_list) == len(app_list):
				#	img_div = logo_list[count].find('img')
				#	if img_div is not None:
				#		img = img_div.get('src')
				title_h3 = item.find('h3')
				if title is not None:
					title = title_h3.text
					meta = item.find('div', class_="app-meta text-over")
					if meta is not None:
						#m = re.search(u'\d+\.*\d*M', meta.text)
						#size = m.group() if m is not None else u''
						m2 = re.search(u'[\u4e00-\u9fa5\s]+', meta.text)
						game_type = m2.group() if m2 is not None else u''
						#print m2.group(), '-----', m.group()
						#game_type, size = meta.text.split(u' ')
					meta2 = item.find('div', class_="app-meta2 text-over")
					if meta2 is not None:
						spans = meta2.find_all('span')
						if len(spans) == 2:
							dt, status = [i.text for i in spans]
							publish_date, time = dt.split(u' ')
				if title and publish_date:
					ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('360zhushou')).first()
					if ins is None:
						count += 1
						item = KC_LIST(**{
											"title" : title,
											"game_type" : game_type,
											"publish_date" : publish_date,
											"time" : time,
											"img" : img,
											"status" : status,
											"source" : source_map.get('360zhushou'),
										})
						db_conn.merge(item)
	mylogger.info("get %s records from 360 zhushou" % count)
	db_conn.commit()

def get_xiaomi_new_kc(page):
	count = 0
	url = "http://app.migc.xiaomi.com/cms/interface/v5/subjectgamelist1.php?pageSize=20&page=%s&subId=138" % page
	try:
		r = requests.get(url)
	except Exception,e:
		r = T(404)
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
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
				if pubTime:
					t = unicode(pubTime)[:10]
					publish_date = unicode(datetime.date.fromtimestamp(int(t)))
				if title and publish_date :
					ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('xiaomi_new')).first()
					if ins is None:
						count += 1
						item = KC_LIST(**{
									"title": title,
									"game_type": game_type,
									"publish_date": publish_date,
									"img": img,
									"game_id": g.get('gameId', u''),
									"pkg_name": g.get('packageName', u''),
									"popular": popular,
									"source": source_map.get('xiaomi_new')
									})
						db_conn.merge(item)
					else:
						ins.game_id = g.get('gameId', u'')
						ins.pkg_name = g.get('packageName', u'')
	mylogger.info("get %s records from xiaomi_new" % count)
	db_conn.commit()

def get_xiaomi_rpg_kc(page):
	count = 0
	url = "http://app.migc.xiaomi.com/cms/interface/v5/subjectgamelist1.php?subId=203&pageSize=20&page=%s" % page
	try:
		r = requests.get(url)
	except Exception,e:
		r = T(404)
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
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
				status = u""
				publish_date = u""
				if pubTime:
					t = unicode(pubTime)[:10]
					publish_date = unicode(datetime.date.fromtimestamp(int(t)))
				if summary:
					dt, status = summary.split(u'|')
				if title and publish_date :
					ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('xiaomi_rpg')).first()
					if ins is None:
						count += 1
						item = KC_LIST(**{
									"title": title,
									"game_type": game_type,
									"publish_date": publish_date,
									"game_id": g.get('gameId', u''),
									"pkg_name": g.get('packageName', u''),
									"img": img,
									"popular": popular,
									"status": status,
									"source": source_map.get('xiaomi_rpg')
									})
						db_conn.merge(item)
					else:
						ins.game_id = g.get('gameId', u'')
						ins.pkg_name = g.get('packageName', u'')
	mylogger.info("get %s records from xiaomi_rpg" % count)
	db_conn.commit()

def get_open_play_kc():
	count = 0
	url = "http://open.play.cn/api/v2/mobile/channel/content.json?channel_id=702&terminal_id=18166&current_page=0&rows_of_page=20"
	try:
		r = requests.get(url)
	except Exception,e:
		r = T(404)
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
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
				if game_id and title:
					online_time = g.get('last_online_time', u'')
					if online_time:
						dt, time = online_time.split(u' ')
						publish_date = dt
					ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.title2==game_id).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('open_play')).first()
					if ins is None:
						count+=1
						item = KC_LIST(**{
									"title": title,
									"title2": game_id,
									"game_type": game_type,
									"publish_date": publish_date,
									"img": img,
									"popular": popular,
									"source": source_map.get('open_play')
									})
						db_conn.merge(item)
	mylogger.info("get %s records from open_play" % count)
	db_conn.commit()

def get_vivo_kc(page):
	count = 0
	#url = "http://gamecenter.vivo.com.cn/clientRequest/topicGame?id=214&page_index=1"
	url = "http://main.gamecenter.vivo.com.cn/clientRequest/startingGame?page_index=%s" % page
	try:
		r = requests.get(url)
	except Exception,e:
		r = T(404)
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
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
			try:
				_date = u"%s-%s-%s" % (datetime.date.today().year, m.group(1), m.group(2))
			except Exception, e:
				mylogger.error("%s" % (traceback.format_exc()))
			if _date:
				detail_url = "http://info.gamecenter.vivo.com.cn/clientRequest/gameDetail?id=%s&adrVerName=4.4.4&appVersion=37" % (ret.get('id'))
				publish_date = datetime.datetime.strptime(_date, '%Y-%m-%d')
				ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==unicode(publish_date.date())).filter(KC_LIST.source==source_map.get('vivo')).first()
				if ins is None:
					count+=1
					item = KC_LIST(**{
							"title": title,
							"title2": ret.get('id', u''),
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
					ins.title2 = ret.get('id', u'')
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
	except Exception,e:
		r = T(404)
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
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
					ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.title2==resid).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('coolpad')).first()
					if ins is None:
						count += 1
						item = KC_LIST(**{
									"title": title,
									"title2": resid,
									"game_type": game_type,
									"publish_date": publish_date,
									"img": img,
									"popular": popular,
									"source": source_map.get('coolpad')
									})
						db_conn.merge(item)
					#else:
					#	print title, publish_date
					#	ins.publish_date = publish_date
					#	ins.last_update = datetime.datetime.now()
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
	except Exception,e:
		r = T(404)
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
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
	return u''

def get_gionee_kc(page):
	count = 0
	url = "http://game.gionee.com/Api/Local_Rank/clientIndex?&page=%s" % page
	try:
		r = requests.get(url, timeout=10)
	except Exception,e:
		r = T(404)
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	if r.status_code == 200:
		d = r.json()
		for ret in d['data']['list']:
			title = ret.get('name', u'')
			img = ret.get('img', u'')
			score = ret.get('score', u'')
			gameid = ret.get('gameid', u'')
			game_type = ret.get('category', u'')
			dt = ret.get('date', u'')
			m = re.search(u'(\d+)月(\d+)日', dt)
			publish_date = u''
			try:
				publish_date = u"%s-%s-%s" % (datetime.date.today().year, m.group(1), m.group(2))
			except Exception, e:
				mylogger.error("### %s ###\t%s" % (dt.encode('utf-8'), traceback.format_exc()))
			if publish_date:
				ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.title2==gameid).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('gionee')).first()
				if ins is None:
					count += 1
					item = KC_LIST(**{
									"title": title,
									"title2": gameid,
									"game_type": game_type,
									"publish_date": publish_date,
									"img": img,
									"source": source_map.get('gionee')
									})
					db_conn.merge(item)
	mylogger.info("get %s records from gionee" % count)
	db_conn.commit()

def get_lenovo_kc():
	count = 0
	url = "http://yx.lenovomm.com/business/app!getNewest.action?width=1080&t=22&s=0&dpi=480&height=1920"
	try:
		r = requests.get(url, timeout=10)
	except Exception,e:
		r = T(404)
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	if r.status_code == 200:
		d = r.json()
		for ret in d['datalist']:
			title = ret.get('name', u'')
			game_type = ret.get('categoryName', u'')
			img = ret.get('iconAddr', u'')
			publishDate= ret.get('publishDate', u'')
			popular = ret.get('downloadCount', u'')
			if publishDate:
				publish_date = datetime.date.fromtimestamp(int(unicode(publishDate)[:-3]))
				#print title, game_type, publish_date, popular
				ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('lenovo')).first()
				if ins is None:
					count += 1
					item = KC_LIST(**{
									"title": title,
									"title2": ret.get('packageName', u''),
									"game_type": game_type,
									"publish_date": unicode(publish_date),
									"popular": popular,
									"img": img,
									"source": source_map.get('lenovo')
									})
					db_conn.merge(item)
				else:
					ins.title2 = ret.get('packageName', u'')
	mylogger.info("get %s records from lenovo" % count)
	db_conn.commit()
				

def get_iqiyi_kc(page):
	count = 0
	url = "http://store.iqiyi.com/gc/list?callback=rs&id=228&no=%s" % page
	try:
		r = requests.get(url, timeout=10)
	except Exception,e:
		r = T(404)
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
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
					#print title, game_type, publish_date
					if publish_date:
						ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.title2==qipu_id).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('iqiyi')).first()
						if ins is None:
							count += 1
							item = KC_LIST(**{
											"title": title,
											"title2": qipu_id,
											"game_type": game_type,
											"publish_date": publish_date,
											"popular": popular,
											"img": img,
											"source": source_map.get('iqiyi')
											})
							db_conn.merge(item)
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
		mylogger.error("### %s ###\t%s" % (qipu_id.encode('utf-8'), traceback.format_exc()))
	return u''	
	
def get_youku_kc():
	count = 0
	url = "http://api.gamex.mobile.youku.com/app/new_game_tab/get?pg=1&pz=40"
	try:
		r = requests.get(url, timeout=10)
	except Exception,e:
		r = T(404)
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	if r.status_code == 200:
		d = r.json()
		for ret in d['games']:
			publish_date = ret.get('apk_update_time', u'')
			popular = ret.get('total_downloads', u'')
			title = ret.get('appname', u'')
			game_type = ret.get('type', u'')
			img = ret.get('logo', u'')
			game_id = ret.get('id', u'')
			if publish_date:
				ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.title2==game_id).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('youku')).first()
				if ins is None:
					count += 1
					item = KC_LIST(**{
									"title": title,
									"title2": game_id,
									"game_type": game_type,
									"publish_date": publish_date,
									"popular": popular,
									"img": img,
									"source": source_map.get('youku')
									})
					db_conn.merge(item)
	mylogger.info("get %s records from youku" % count)
	db_conn.commit()

def get_wandoujia_kc():
	count = 0
	url = "http://apis.wandoujia.com/apps/v1/topics/smart438/list?start=0&max=15"
	try:
		r = requests.get(url, timeout=10)
	except Exception,e:
		r = T(404)
		mylogger.error("### %s ### %s" % (url, traceback.format_exc()))
	if r.status_code == 200:
		d = r.json()
		for ret in d['entity']:
			title = ret.get('title', u'')
			action = ret.get('action', u'')
			img = ret.get('icon', u'')
			if action:
				detail_url = action.get('url', u'')
				if detail_url:
					detail = get_wandoujia_detail(detail_url)	
					if detail is not None:
						game_type, popular, publish_date = detail
						#print title, game_type, publish_date
						if publish_date:
								ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('wandoujia')).first()
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
	mylogger.info("get %s records from wandoujia" % count)
	db_conn.commit()

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
				publishtime = detail.get('updatedDate', u'')
				publish_date = unicode(datetime.date.fromtimestamp(int(unicode(publishtime)[:10]))) if publishtime else u""
				return game_type, popular, publish_date
	return None
		

def get_sogou_kc():
	count = 0
	url = "http://mobile.zhushou.sogou.com/android/rank/toplist.html?limit=25&start=25&group=2&id=13"
	try:
		r = requests.get(url, timeout=10)
	except Exception,e:
		r = T(404)
		mylogger.error("### %s ### %s" % (url, traceback.format_exc()))
	if r.status_code == 200:
		d = r.json()
		for ret in d['recommend_app']:
			img = ret.get('icon', u'')
			title = ret.get('name', u'')
			popular = ret.get('downloadCount', u'')
			game_type = ret.get('category_name', u'')
			dt = ret.get('date', u'')
			if dt:
				publish_date = dt[:11]
				#print title, publish_date, ret.get('appid', u'')
				ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('sogou')).first()
				if ins is None:
					count += 1
					item = KC_LIST(**{
									"title": title,
									"title2": ret.get('appid', u''),
									"game_type": game_type,
									"publish_date": publish_date,
									"popular": popular,
									"img": img,
									"source": source_map.get('sogou')
									})
					db_conn.merge(item)
				else:
					ins.title2 = ret.get('appid', u'')
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
	except Exception,e:
		r = T(404)
		mylogger.error("### %s ### %s" % (url, traceback.format_exc()))
	if r.status_code == 200:
		d = r.json()
		for ret in d['list']:
			game_type = ret.get('categoryName', u'')
			status = ret.get('operationStatus', u'')
			title = ret.get('name', u'')
			publishtime = ret.get('activityDate', u'')
			publish_date = unicode(datetime.date.fromtimestamp(int(unicode(publishtime)[:10]))) if publishtime else u""
			img = ret.get('iconUrl', u'')
			if publish_date:
				ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('dangle')).first()
				if ins is None:
					count += 1
					item = KC_LIST(**{
									"title": title,
									"title2": ret.get('id', u''),
									"game_type": game_type,
									"status": status,
									"publish_date": publish_date,
									"img": img,
									"source": source_map.get('dangle')
									})
					db_conn.merge(item)
				else:
					ins.title2 = ret.get('id', u'')
	mylogger.info("get %s records from dangle" % count)
	db_conn.commit()
				
def get_i4_kc():
	count = 0
	url = "http://app3.i4.cn/controller/action/online.go?store=3&module=3&rows=100&sort=2&submodule=6&model=101&id=0&reqtype=3&page=1"
	try:
		r = requests.get(url)
	except Exception,e:
		r = T(404)
		mylogger.error("### %s ### %s" % (url, traceback.format_exc()))
	if r.status_code == 200:
		d = r.json()
		for ret in d['result']['list']:
			game_type = ret.get('typeName', u'')
			title = ret.get('appName', u'')
			dt = ret.get('updateTime', u'')
			popular = ret.get('downloadCount', u'')
			#dt = ret.get('createTime', u'')
			publish_date = unicode(datetime.date.fromtimestamp(int(unicode(dt)[:10]))) if dt else u""
			#print title, publish_date

def get_muzhiwan_kc(page):
	count = 0
	#URL = "http://www.muzhiwan.com/category/12/"
	URL = "http://www.muzhiwan.com/category/12/new-0-0-%s.html" % page
	try:
		response = s.get(URL, timeout=10)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		response = T(404)
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
						if u'发布' in info:
							publish_date = info.get(u'发布', u'')
							if publish_date:
								ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('muzhiwan')).first()
								if ins is None:
									count += 1
									item = KC_LIST(**{
											"title": title,
											"url": detail.get('href'),
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
	mylogger.info("get %s records from muzhiwan" % count)
	db_conn.commit()

def get_muzhiwan_detail(url):
	mydict = {}
	try:
		response = s.get(url, timeout=10)
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
		response = T(404)
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
	return mydict

def get_huawei_kc(page):
	count = 0
	URL = "http://appstore.huawei.com/game/list_2_1_%s" % page
	try:
		response = s.get(URL, timeout=10)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		response = T(404)
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
						img = img_div.get('src')
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
							ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('huawei')).first()
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
	mylogger.info("get %s records from huawei" % count)
	db_conn.commit()
				

def get_kuaiyong_kc(page):
	count = 0
	URL = "http://app.kuaiyong.com/list/index/appType/game/page/%s" % page
	try:
		response = s.get(URL, timeout=10)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		response = T(404)
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
						ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.publish_date==publish_date).filter(KC_LIST.source==source_map.get('kuaiyong')).first()
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
	mylogger.info("get %s records from kuaiyong" % count)
	db_conn.commit()
						

def get_kuaiyong_detail(URL):
	mydict = {}
	try:
		response = s.get(URL, timeout=10)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		response = T(404)
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
	return mydict

def get_itools_kc():
	count = 0
	URL = "http://ios.itools.cn/game/iphone/gameall_3_1"
	try:
		response = s.get(URL, timeout=10)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		response = T(404)
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
	mylogger.info("get %s records from itools" % count)
	db_conn.commit()

def get_itools_detail(URL):
	mydict = {}
	try:
		response = s.get(URL, timeout=10)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		response = T(404)
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
	return mydict

def get_anzhi_kc(page):
	count = 0
	URL = "http://www.anzhi.com/list_2_%s_new.html" % page
	try:
		response = s.get(URL, timeout=10)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		response = T(404)
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
	mylogger.info("get %s records from anzhi" % count)
	db_conn.commit()

def get_anzhi_detail(URL):
	mydict = {}
	try:
		response = s.get(URL, timeout=10)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		response = T(404)
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
	return mydict

def get_360_web_kc(page):
	count = 0
	URL = "http://zhushou.360.cn/list/index/cid/2/order/newest/?page=%s" % page
	try:
		response = s.get(URL, timeout=10)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		response = T(404)
	if response.status_code == 200:
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
						img  = li.find('a').find('img').get('src')
						_url = u"http://zhushou.360.cn%s" % li.find('a').get('href')
						ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.source==source_map.get('360zhushou_web')).filter(KC_LIST.publish_date==publish_date).first()
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
	mylogger.info("get %s records from 360 zhushou web page %s" % (count, page))
	db_conn.commit()
				

def get_pp_kc(page):
	count = 0
	headers = {'tunnel-command':4261421088}
	try:
		j = {"dcType":0, "resType":2, "listType":0, "catId":0, "clFlag":1, "perCount":32, "page": page}
		r = requests.post('http://jsondata.25pp.com/index.html', data=json.dumps(j), headers=headers)
	except Exception,e:
		mylogger.error("get pp kc list\t%s" % (traceback.format_exc()))
		r = T(404)
	if r.status_code == 200:
		content = re.sub(u'\ufeff', u'', r.text)
		d = json.loads(content)
		for g in d['content']:
			gid = g.get('id', u'')
			if gid:
				detail = get_pp_detail_by_id(gid)
				title = g.get('title', u'')
				updatetime = g.get('updatetime', u'')
				publish_date = unicode(datetime.date.fromtimestamp(updatetime))
				ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.source==source_map.get('pp')).filter(KC_LIST.publish_date==publish_date).first()
				if not ins:
					count += 1
					item = KC_LIST(**{
									'publish_date':publish_date,
									'title':title,
									'game_type': detail.get('catName', u''),
									'title2': gid,
									'img': g.get('thumb', u''),
									'source':source_map.get('pp'),
									'popular' : g.get('downloads', u'')
										})
					db_conn.merge(item)
	mylogger.info("get %s records from pp %s" % (count, page))
	db_conn.commit()


def get_pp_detail_by_id(gid):
	try:
		d = {"site":1, "id": gid}
		r = requests.post('http://pppc2.25pp.com/pp_api/ios_appdetail.php', data=d)
	except Exception,e:
		mylogger.error("get %s detail \t%s" % (gid, traceback.format_exc()))
		r = T(404)
	if r.status_code == 200:
		return r.json()
	return {}

def get_meizu_kc():
	count = 0
	URL = "http://api-game.meizu.com/games/public/new/layout?start=0&max=50"
	try:
		response = s.get(URL, timeout=10)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		response = T(404)
	if response.status_code == 200:
		j = response.json() 
		if j.get('code', 9527) == 200:
			blocks = j['value']['blocks']
			if blocks:
				for re in blocks[0]['data']:
					title = re.get('name', u'')
					gid = re.get('id', 0)
					detail = get_meizu_detail_by_id(gid)
					if title and gid and detail is not None:
						version_time = detail.get('version_time', u'')
						if version_time:
							publish_date = unicode(datetime.date.fromtimestamp(int(unicode(version_time)[:10])))
							ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.source==source_map.get('meizu')).filter(KC_LIST.publish_date==publish_date).first()
							if not ins:
								count += 1
								item = KC_LIST(**{
											'publish_date': publish_date,
											'title': re.get('name', u''),
											'game_type': re.get('category_name', u''),
											'title2': gid,
											'img': re.get('icon', u''),
											'source': source_map.get('meizu'),
											'popular' : re.get('download_count', u'')
												})
								db_conn.merge(item)
	mylogger.info("get %s records from meizu " % (count))
	db_conn.commit()
		

def get_meizu_detail_by_id(gid):
	URL = "http://api-game.meizu.com/games/public/detail/%s" % gid
	try:
		response = s.get(URL, timeout=10)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		response = T(404)
	if response.status_code == 200:
		j = response.json()
		if 'value' in j:
			return j['value']
	return None


def get_xyzs_kc(page):
	count = 0
	URL = "http://interface.xyzs.com/v2/ios/c01/game/latest?p=%s&ps=20" % page
	try:
		response = s.get(URL, timeout=10)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		response = T(404)
	if response.status_code == 200:
		j = response.json() 
		if j.get('code', 9527) == 200:
			if 'data' in j:
				for re in j['data'].get('result', []):
					#for k, v in re.iteritems():
					#	print k, v
					title = re.get('title', u'')
					addtime = re.get('addtime', u'')
					gid = re.get('itunesid', 0)
					detail = get_xyzs_detail_by_id(gid)
					if addtime and title:
						game_type = detail.get('apptypesno', u'') if detail is not None else u''
						publish_date = unicode(datetime.date.fromtimestamp(int(addtime)))
						print publish_date, title, game_type
#						ins = db_conn.query(KC_LIST).filter(KC_LIST.title==title).filter(KC_LIST.source==source_map.get('xyzs')).filter(KC_LIST.publish_date==publish_date).first()
#						if not ins:
#							count += 1
#							item = KC_LIST(**{
#											'publish_date': publish_date,
#											'title': re.get('title', u''),
#											'game_type': game_type,
#											'title2': gid,
#											'img': re.get('icon', u''),
#											'source': source_map.get('xyzs'),
#											'popular' : re.get('downloadnum', u'')
#												})
#							db_conn.merge(item)
#	mylogger.info("get %s records from xyzs " % (count))
#	db_conn.commit()
		


def get_xyzs_detail_by_id(gid):
	URL = "http://interface.xyzs.com/v2/ios/c01/app"
	d = {'itunesid': gid}
	try:
		response = s.get(URL, params=d, timeout=10)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		response = T(404)
	if response.status_code == 200:
		j = response.json()
		if 'data' in j:
			return j['data'].get('app')
	return None


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
	get_muzhiwan_kc(1)
	get_huawei_kc(1)
	get_kuaiyong_kc(1)
	get_360_web_kc(1)
	#get_anzhi_kc(1)
	get_wandoujia_kc()
	get_9game_today_kc()
	get_pp_kc(1)
	get_meizu_kc()

if __name__ == '__main__':
	main()
	#get_i4_kc()
	#get_itools_kc()
	#for i in xrange(6, 11):
	#	get_anzhi_kc(i)
	#get_xyzs_kc(1)

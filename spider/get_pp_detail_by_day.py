#!/usr/bin/env python
#encoding=utf-8

import sys
sys.path.append('/home/cyp/Utils/common')
from define import *
from model import *
import requests
import datetime
import json
import re
from bs4 import BeautifulSoup
from time import sleep
import traceback
from get_logger import *
import random
import xmltodict

db_conn = new_session()
s = requests.session()
mylogger = get_logger('get_game_detail')

class T:
	
	def __init__(self, status_code):
		self.status_code = status_code


def get_9game_detail():
	mylogger.info("get 9game detail start ...")
	count = 0
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==0).filter(KC_LIST.publish_date>=u'2015-10-01'):
		try:
			response = s.get(ret.url, timeout=10)
		except Exception,e:
			response = T(404)
			mylogger.error("%s\t%s" % (ret.url.encode('utf-8'), traceback.format_exc()))
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			spec_pic = soup.find('div', class_='spec-pic')
			imgs 	= u''
			rating 	= u''
			game_type = u''
			comments_num = u''
			topic_num_day = u''
			topic_num_total = u''
			dt = unicode(datetime.date.today())
			if spec_pic is not None:
				#for pic in spec_pic.find_all('span', class_='img'):
				#	print pic
				imgs = u','.join([pic.find('img').get('src') for pic in spec_pic.find_all('span', class_='img')])
			tips = soup.find('div', class_='tips')
			summary = tips.text.strip() if tips is not None else u''
			bbs = soup.find('li', class_='bbs')
			if bbs is not None:
				if bbs.find('a') is not None:
					info = get_9game_info_from_bbs(bbs.find('a').get('href'))
					if info is not None:
						topic_num_day, topic_num_total = info
			scores = soup.find('div', class_='view-scroe1')
			if scores is not None:
				rating =  scores.find('div', class_='big-s').text
			p_des = soup.find('div', class_='p-des')
			if p_des is not None:
				if p_des.find('p') is not None:
					content = re.sub(u'\r| |\xa0', u'', p_des.find('p').text)
					for seg in content.split('\n'):
						if u'类型' in seg:
							if  len(seg.split(u':')) == 2:
								game_type = seg.split(u':')[1].strip()
						elif u'评论' in seg:
							m = re.search('\d+', seg)
							comments_num = m.group() if m is not None else u''
			ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
			if not ins:
				count += 1
				item = GameDetailByDay(**{'kc_id': ret.id,
											'dt' : dt,
											'imgs' : imgs,
											'summary' : summary,
											'game_type' : game_type,
											'topic_num_day' : topic_num_day,
											'topic_num_total' : topic_num_total,
											'rating' : rating ,
											'comment_num' : comments_num,
											})
				db_conn.merge(item)
	mylogger.info("get 9game detail %s" % count)
	db_conn.commit()

def get_9game_info_from_bbs(url):
	try:
		response = s.get(url, timeout=10)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			topics = soup.find('span', 'xs1 xw0 i')	
			if topics is not None:
				nums = topics.find_all('strong')
				if len(nums) == 2:
					today_nums, total_nums = [i.text for i in nums]
					return today_nums, total_nums
	except Exception,e:
		mylogger.error("%s\t%s" % (url.encode('utf-8'), traceback.format_exc()))
	return None

def get_18183_detail():
	mylogger.info("get 18183 detail start ...")
	count = 0 
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.publish_date>=u'2015-10-01').filter(KC_LIST.url!=u'').filter(KC_LIST.source==2):
		try:
			response = s.get(ret.url, timeout=10)
		except Exception,e:
			response = T(404)
			mylogger.error("%s\t%s" % (ret.url.encode('utf-8'), traceback.format_exc()))
		if response.status_code == 200:
			topic_num_total = u''
			game_type = u''
			pkg_size = u''
			summary = u''
			imgs = u''
			dt = unicode(datetime.date.today())
			r = response.text.encode('ISO-8859-1').decode('utf-8')
			soup = BeautifulSoup(r)
			for li1 in soup.find_all('li', class_='li1'):
				codes = li1.find_all('code')
				spans = li1.find_all('span')
				for i in xrange(len(codes)):
					if codes[i].text == u'类型：':
						game_type = spans[i].text.strip()
					if codes[i].text == u'关注：':
						rs = requests.get(spans[i].find('script').get('src'))
						if rs.status_code == 200:
							m = re.search('\d+', rs.text)
							if m is not None:
								topic_num_total = m.group()
			dwnli = soup.find('li', class_='dwnli')
			if dwnli is not None:
				if dwnli.find('p') is not None:
					if dwnli.find('p') is not None:
						pkg_size = dwnli.find('p').text.split(u'：')[1]
			jianjie_txt = soup.find('div', class_='jianjie_txt')
			if jianjie_txt is not None:
				summary = jianjie_txt.text.strip()
			tabcen_ul = soup.find('ul', class_='tabcen_ul')
			if tabcen_ul is not None:
				icons = []
				for ss_body in tabcen_ul.find_all('li', class_='ss_body'):
					if ss_body.find('img') is not None:
						icons.append(ss_body.find('img').get('src'))
				if icons:
					imgs = u",".join(icons)
			ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
			if not ins:
				count += 1
				item = GameDetailByDay(**{'kc_id': ret.id,
											'dt' : dt,
											'imgs' : imgs,
											'summary' : summary,
											'pkg_size' : pkg_size,
											'game_type' : game_type,
											'topic_num_total' : topic_num_total,
											})
				db_conn.merge(item)
	mylogger.info("get 18183 detail %s" % count)
	db_conn.commit()


def get_360_web_detail():
	mylogger.info("get 360 detail start ...")
	count = 0
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.publish_date>=u'2015-10-01').filter(KC_LIST.source==22).filter(KC_LIST.url!=''):
		try:
			response = s.get(ret.url, timeout=10)
		except Exception,e:
			mylogger.error("%s\t%s" % (ret.url.encode('utf-8'), traceback.format_exc()))
			response = T(404)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
		#app_name = soup.find('h2', id='app-name')
		#if app_name is not None:
		#	name = app_name.find('span').get('title')
			imgs = u''
			rating = u''
			summary = u''
			comment_num = u''
			download_num = u''
			pkg_size = u''
			dt = unicode(datetime.date.today())
			pf = soup.find('div', class_='pf')
			if pf is not None:
				for li in pf.find_all('span'):
					if u'分' in li.text:
						if re.search('\d+', li.text) is not None:
							rating = re.search('\d+', li.text).group()
					elif u'评价' in li.text:
						if re.search('\d+', li.text) is not None:
							comment_num = re.search('\d+', li.text).group()
					elif u'下载' in li.text:
						if re.search('\d+', li.text) is not None:
							download_num = re.search('\d+', li.text).group()
					elif u'M' in li.text:
						pkg_size = li.text
			breif = soup.find('div', class_='breif')
			if breif is not None:
				summary = breif.text
			viewport = soup.find('div', class_='viewport')
			icons = []
			if viewport is not None:
				for icon in viewport.find_all('img'):
					icons.append(icon.get('src'))
			if icons:
				imgs = u','.join(icons)
			ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
			if not ins:
				count += 1
				item = GameDetailByDay(**{'kc_id': ret.id,
											'dt' : dt,
											'imgs' : imgs,
											'summary' : summary,
											'pkg_size' : pkg_size,
											'rating' : rating,
											'comment_num' : comment_num,
											'download_num' : download_num,
											})
				db_conn.merge(item)
				if count % 500 == 0:
					mylogger.info("360 detail %s commit" % count)
					db_conn.commit()
	mylogger.info("get 360 detail %s" % count)
	db_conn.commit()

def get_appicsh_detail():
	mylogger.info("get appicsh detail start ...")
	count = 0
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.source==3).filter(KC_LIST.url!=u''):
		try:
			response = s.get(ret.url, timeout=10)
		except Exception,e:
			mylogger.error("%s\t%s" % (ret.url.encode('utf-8'), traceback.format_exc()))
			response = T(404)
		if response.status_code == 200:
			d = response.json()
			dt = unicode(datetime.date.today())
			if d['obj'] is not None:
				if d['obj']['appInfo'] is not None:
					appinfo = d['obj']['appInfo']
					ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
					if not ins:
						count += 1
						publishtime = appinfo.get('apkPublishTime', u"")
						update_time = unicode(datetime.date.fromtimestamp(publishtime)) if publishtime else u""

						item = GameDetailByDay(**{'kc_id': ret.id,
													'dt' : dt,
													'imgs' : u','.join([i for i in appinfo['screenshots']]),
													'summary' : appinfo.get('description', u''),
													'pkg_size' : appinfo.get('fileSize', u''),
													'version' : appinfo.get('versionName', u''),
													'rating' : appinfo.get('averageRating', u''),
													'download_num' : appinfo.get('appDownCount', u''),
													'author' : appinfo.get('authorName', u''),
													'update_time' : update_time
													})
						db_conn.merge(item)
	mylogger.info("get appicsh detail %s" % count)
	db_conn.commit()
			

def get_xiaomi_new_id_map():
	mydict = {}
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==5):
		mydict[int(ret.game_id)] = ret.id
	return mydict


def get_xiaomi_new_detail():
	id_map = get_xiaomi_new_id_map()
	for page in xrange(1, 23):
		mylogger.info("get xiaomi_new detail page %s" % page)
		url = "http://app.migc.xiaomi.com/cms/interface/v5/subjectgamelist1.php?pageSize=20&page=%s&subId=138" % page
		try:
			r = requests.get(url, timeout=10)
		except Exception,e:
			mylogger.error("%s\t%s" % (url, traceback.format_exc()))
			response = T(404)
		if r.status_code == 200:
			d = r.json()
			if d['errCode'] == 200:
				new_games_list = d.get('gameList', [])
				for g in new_games_list:
					game_id = g.get('gameId', u'')
					update_time = u''
					updateTime = g.get('updateTime', u'')
					if updateTime:
						t = unicode(updateTime)[:10]
						update_time = unicode(datetime.date.fromtimestamp(int(t)))
					dt = unicode(datetime.date.today())
					if game_id in id_map:
						ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==id_map[game_id]).filter(GameDetailByDay.dt==dt).first()
						if not ins:
							item = GameDetailByDay(**{
													'kc_id': id_map.get(game_id),
													'summary' : g.get('introduction', u''),
													'author' : g.get('publisherName', u''),
													'game_type' : g.get('className', u''),
													'rating' : g.get('ratingScore', u''),
													'version' : g.get('versionName', u''),
													'pkg_size' : g.get('apkSize', u''),
													'download_num' : g.get('downloadCount', u''),
													'dt' : dt,
													'imgs' : u','.join([i.get('url') for i in g['screenShot']]),
													'topic_num_total' : g.get('ratingCount', u''),
													'update_time' : update_time,
														})
							db_conn.merge(item)
						else:
							ins.pkg_size = g.get('apkSize', u'')
	db_conn.commit()
							

def get_xiaomi_rpg_id_map():
	mydict = {}
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==6):
		mydict[int(ret.game_id)] = ret.id
	return mydict


def get_xiaomi_rpg_detail():
	id_map = get_xiaomi_rpg_id_map()
	for page in xrange(1, 2):
		mylogger.info("get xiaomi rpg detail %s" % page)
		url = "http://app.migc.xiaomi.com/cms/interface/v5/subjectgamelist1.php?subId=203&pageSize=150&page=%s" % page
		try:
			r = requests.get(url, timeout=10)
		except Exception,e:
			mylogger.error("%s\t%s" % (url, traceback.format_exc()))
			response = T(404)
		if r.status_code == 200:
			d = r.json()
			if d['errCode'] == 200:
				new_games_list = d.get('gameList', [])
				for g in new_games_list:
					game_id = g.get('gameId', u'')
					update_time = u''
					updateTime = g.get('updateTime', u'')
					if updateTime:
						t = unicode(updateTime)[:10]
						update_time = unicode(datetime.date.fromtimestamp(int(t)))
					dt = unicode(datetime.date.today())
					if game_id in id_map:
						ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==id_map[game_id]).filter(GameDetailByDay.dt==dt).first()
						if not ins:
							item = GameDetailByDay(**{
													'kc_id': id_map.get(game_id),
													'summary' : g.get('introduction', u''),
													'author' : g.get('publisherName', u''),
													'game_type' : g.get('className', u''),
													'rating' : g.get('ratingScore', u''),
													'version' : g.get('versionName', u''),
													'download_num' : g.get('downloadCount', u''),
													'dt' : dt,
													'pkg_size' : g.get('apkSize', u''),
													'imgs' : u','.join([i.get('url') for i in g['screenShot']]),
													'topic_num_total' : g.get('ratingCount', u''),
													'update_time' : update_time,
														})
							db_conn.merge(item)
						else:
							ins.pkg_size = g.get('apkSize', u'')
	db_conn.commit()
							

def get_open_play_detail():
	count = 0
	mylogger.info("get open play detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.title2!=u'').filter(KC_LIST.source==7):
		_url = u'http://open.play.cn/api/v2/mobile/game_detail.json?game_id=%s' % ret.title2
		try:
			response = s.get(_url, timeout=10)
		except Exception,e:
			mylogger.error("%s\t%s" % (_url.encode('utf-8'), traceback.format_exc()))
			response = T(404)
		if response.status_code == 200:
			d = response.json()
			if d['text'] == u'success':
				g = d['ext']['game_detail']
				#for k,v in d['ext']['game_detail'].iteritems():
				#	print k, v
				dt = unicode(datetime.date.today())
				ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
				if not ins:
					count += 1 
					topic_num_total = u''
					ref_vote_info = d['ext']['ref_vote_info']
					if ref_vote_info['vote_state'] == 1:
						topic_num_total = ref_vote_info['vote_up_count'] + ref_vote_info['vote_dn_count']
					item = GameDetailByDay(**{
											'kc_id': ret.id,
											'summary' : g.get('game_introduction', u''),
											'author' : g.get('cp_name', u''),
											'game_type' : g.get('game_class', u''),
											'version' : g.get('version', u''),
											'download_num' : g.get('game_download_count', u''),
											'pkg_size' : g.get('game_size' u''),
											'dt' : dt,
											'imgs' : u','.join(g['game_view_images']),
											'topic_num_total' : topic_num_total,
												})
					db_conn.merge(item)
	mylogger.info("get open play detail %s" % count)
	db_conn.commit()

def get_vivo_detail():
	count = 0
	mylogger.info("get vivo detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==8):
		try:
			response = s.get(ret.url, timeout=10)
		except Exception,e:
			mylogger.error("%s\t%s" % (ret.url.encode('utf-8'), traceback.format_exc()))
			response = T(404)
		if response.status_code == 200:
			d = response.json()
			if d is not None and 'result' in d and d['result']:
				dt = unicode(datetime.date.today())
				g = d['game']
				ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
				if not ins:
					count += 1 
					item = GameDetailByDay(**{
											'kc_id': ret.id,
											'summary' : g.get('desc', u''),
											'rating' : g.get('comment', u''),
											'author' : g.get('gameDeveloper', u''),
											'game_type' : g.get('type', u''),
											'version' : g.get('versonName', u''),
											'download_num' : g.get('download', u''),
											'comment_num' : g.get('commentNum', u''),
											'pkg_size' : g.get('size' u''),
											'dt' : dt,
											'update_time' : g.get('date', u''),
											'imgs' : u','.join(g['screenshot'].split(u'###')),
												})
					db_conn.merge(item)
				else:
					ins.author = g.get('gameDeveloper', u'')
	mylogger.info("get vivo play detail %s" % count)
	db_conn.commit()


def get_coolpad_detail():
	count = 0
	mylogger.info("get coolpad detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.title2!=u'').filter(KC_LIST.source==9):
		g =  get_coolpad_detail_by_id(ret.title2)
		if g is not None:
			dt = unicode(datetime.date.today())
			ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
			if not ins:
				count += 1 
				imgs = u''
				if g['pics'] is not None and g['pics']['picurl'] is not None:
					imgs =  u','.join([i for i in g['pics']['picurl'] if i is not None])
				item = GameDetailByDay(**{
											'kc_id': ret.id,
											'summary' : g.get('summary', u''),
											'rating' : g.get('score', u''),
											'game_type' : g.get('levelname', u''),
											'version' : g.get('version', u''),
											'download_num' : g.get('downloadtimes', u''),
											'comment_num' : g.get('commcount', u''),
											'pkg_size' : g.get('size' u''),
											'dt' : dt,
											'imgs' : imgs,
												})
				db_conn.merge(item)
	mylogger.info("get coolpad detail %s" % count)
	db_conn.commit()


def get_coolpad_detail_by_id(resid):
	url = "http://gamecenter.coolyun.com/gameAPI/API/getDetailResInfo?key=0"
	raw_data = """<?xml version="1.0" encoding="utf-8"?>
<request username="" cloudId="" openId="" sn="865931027730878" platform="1" platver="19" density="480" screensize="1080*1920" language="zh" mobiletype="MI4LTE" version="4" seq="0" appversion="3350" currentnet="WIFI" channelid="coolpad" networkoperator="46001" simserianumber="89860115851040101064">
  <resid>%s</resid>
</request>""" % resid
	msg = 'fail'
	try:
		r = requests.post(url, data=raw_data, headers={'Content-Type': 'application/xml'})
	except Exception,e:
		mylogger.error("%s\t%s" % (resid.encode('utf-8'), traceback.format_exc()))
		r = T(404)
	if r.status_code == 200:
		t = re.sub(u'\r|\n', '', r.text)
		doc = xmltodict.parse(t)
		d = doc['response']['reslist']['res']
		if d['@rid'] != u'':
			return d
		else:
			msg = 'expire'
	mylogger.info("get %s coolpad detail %s" % (resid, msg))
	return None

def get_gionee_detail():
	count = 0
	mylogger.info("get gionee detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.title2!=u'').filter(KC_LIST.source==10):
		_url = u"http://game.gionee.com/Api/Local_Gameinfo/getDetails?gameId=%s" % ret.title2
		try:
			response = s.get(_url, timeout=10)
		except Exception,e:
			response = T(404)
			mylogger.error("%s\t%s" % (_url.encode('utf-8'), traceback.format_exc()))
		if response.status_code == 200:
			d = response.json()
			if 'success' in d and d['success']:
				dt = unicode(datetime.date.today())
				g = d['data']
				ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
				if not ins:
					count += 1 
					item = GameDetailByDay(**{
											'kc_id': ret.id,
											'rating' : g.get('score', u''),
											'author' : g.get('publisher', u''),
											'game_type' : g.get('category', u''),
											'version' : g.get('versionName', u''),
											'pkg_size' : g.get('fileSize' u''),
											'dt' : dt,
											'imgs' : u','.join(g['bannerList']['fullPicture']),
												})
					db_conn.merge(item)
	mylogger.info("get gionee play detail %s" % count)
	db_conn.commit()



def get_leveno_detail():
	count = 0
	mylogger.info("get lenovo detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.title2!=u'').filter(KC_LIST.source==11):
		_url = u"http://yx.lenovomm.com/business/app!getAppDetail5.action?dpi=480&height=1920&dev=ph&width=1080&cpu=armeabi-v7a&pn=%s&uid=72DB07100FC223A2EDE82F4A44AE96B4&os=4.4.4&perf=hp&model=MI 4LTE&type=0&density=xx&mac=7A031DAB40535B3F5E204582EB961FC5" % ret.title2
		try:
			response = s.get(_url, timeout=10)
		except Exception,e:
			response = T(404)
			mylogger.error("%s\t%s" % (_url.encode('utf-8'), traceback.format_exc()))
		if response.status_code == 200:
			d = response.json()
			if 'app' in d:
				dt = unicode(datetime.date.today())
				g = d['app']
				ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
				if not ins:
					count += 1 
					item = GameDetailByDay(**{
											'kc_id': ret.id,
											'rating' : g.get('averageStar', u''),
											'game_type' : g.get('categoryName', u''),
											'version' : g.get('version', u''),
											'pkg_size' : g.get('size' u''),
											'dt' : dt,
											'download_num' : g.get('downloadCount', u''),
											'summary' : g.get('description', u''),
											'imgs' : g['snapList'],
												})
					db_conn.merge(item)
	mylogger.info("get lenovo detail %s" % count)
	db_conn.commit()


def get_iqiyi_detail():
	count = 0
	mylogger.info("get iqiyi detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.title2!=u'').filter(KC_LIST.source==12):
		d =  get_iqiyi_detail_by_id(ret.title2)
		if d is not None:
			g = d['app']
			dt = unicode(datetime.date.today())
			ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
			if not ins:
				count += 1 
				item = GameDetailByDay(**{
											'kc_id': ret.id,
											'summary' : g.get('desc', u''),
											'game_type' : g.get('cate_name', u''),
											'version' : g.get('version', u''),
											'download_num' : g.get('cnt', u''),
											'author' : g.get('author', u''),
											'pkg_size' : g.get('l_size' u''),
											'dt' : dt,
											'imgs' : u",".join([i.get('full_img', u'') for i in d['medias']]),
												})
				db_conn.merge(item)
			else:
				ins.author = g.get('author', u'')
	mylogger.info("get iqiyi detail %s" % count)
	db_conn.commit()


def get_iqiyi_detail_by_id(qipu_id):
	url = "http://store.iqiyi.com/gc/game/detail?callback=rs&id=%s" % qipu_id
	try:
		r = requests.get(url)
		if r.status_code == 200:
			m = re.search(u'rs\\(([\s\S]*)\\)\\;', r.text)
			if m is not None:
				return json.loads(m.group(1))
	except Exception, e:
		mylogger.error("### %s ###\t%s" % (qipu_id.encode('utf-8'), traceback.format_exc()))
	return None

def get_sogou_detail():
	count = 0
	mylogger.info("get sogou detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.title2!=u'').filter(KC_LIST.source==14):
		_url = u"http://mobile.zhushou.sogou.com/m/appDetail.html?id=%s" % ret.title2
		try:
			response = s.get(_url, timeout=10)
		except Exception,e:
			response = T(404)
			mylogger.error("%s\t%s" % (_url.encode('utf-8'), traceback.format_exc()))
		if response.status_code == 200:
			d = response.json()
			g = d['ainfo']
			dt = unicode(datetime.date.today())
			ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
			if not ins:
				count += 1 
				item = GameDetailByDay(**{
											'kc_id': ret.id,
											'rating' : g.get('score', u''),
											'summary' : g.get('desc', u''),
											'version' : g.get('vn', u''),
											'game_type' : d['tgroup'].get('name', u''),
											'download_num' : g.get('dc', u''),
											'author' : g.get('author', u''),
											'pkg_size' : g.get('size' u''),
											'dt' : dt,
											'imgs' : u",".join([i.get('url', u'') for i in d['images']]),
												})
				db_conn.merge(item)
	mylogger.info("get sogou detail %s" % count)
	db_conn.commit()


def get_dangle_detail():
	count = 0
	mylogger.info("get dangle detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.title2!=u'').filter(KC_LIST.source==15):
		g =  get_dangle_detail_by_id(ret.title2)
		if g is not None:
			dt = unicode(datetime.date.today())
			ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
			if not ins:
				count += 1 
				packageTOs = {}
				if 'packageTOs' in g:
					packageTOs = g['packageTOs'][0] if g['packageTOs'] else {}
				else:
					print ret.title2
				item = GameDetailByDay(**{
											'kc_id': ret.id,
											'summary' : g.get('description', u''),
											'game_type' : g.get('categoryName', u''),
											'version' : packageTOs.get('versionName', u''),
											'rating' : g.get('score', u''),
											'comment_num' : g.get('commentCnt', u''),
											'topic_num_total' : g.get('grade', {}).get('personCnt', u''),
											'download_num' : g.get('appInstalledCount', u''),
											'author' : g.get('author', u''),
											'pkg_size' : packageTOs.get('fileSize', u''),
											'dt' : dt,
											'imgs' : u','.join(g['snapshotUrls']),
												})
				db_conn.merge(item)
	mylogger.info("get dangle detail %s" % count)
	db_conn.commit()


def get_dangle_detail_by_id(gid):
	
	url = "http://api2014.digua.d.cn/newdiguaserver/res/detail?id=%s&resourceType=5"% gid
	headers = {"HEAD": {
    "stamp":1447747218496,
    "verifyCode":"78492ba9e8569f3b9d9173ac4e4b6cb9",
    "it":2,
    "resolutionWidth":1080,
    "imei":"865931027730878",
    "clientChannelId":"100327",
    "versionCode":750,
    "mac":"34:80:b3:4d:69:87",
    "vender":"Qualcomm",
    "vp":"",
    "version":"7.5",
    "sign":"cfd1b8d1b60f85c4",
    "dd":480,
    "sswdp":"360",
    "hasRoot":0,
    "glEsVersion":196608,
    "device":"MI_4LTE",
    "ss":2,
    "local":"zh_CN",
    "language":"2",
    "sdk":19,
    "resolutionHeight":1920,
    "osName":"4.4.4",
    "gpu":"Adreno (TM) 330"
	}}
	r = requests.post(url, headers=headers)
	if r.status_code == 200:
		d = r.json()
		return d
	return None

def get_muzhiwan_detail():
	count = 0
	mylogger.info("get muzhiwan detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==17):
		g = get_muzhiwan_detail_by_id(ret.url)
		if g:
			dt = unicode(datetime.date.today())
			m = re.search(u'(\d+)个', g.get(u'评论数', u''))
			comment_num = m.group(1) if m is not None else u''
			ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
			if not ins:
				count += 1 
				item = GameDetailByDay(**{
											'kc_id': ret.id,
											'summary' : g.get('description', u''),
											'version' : g.get(u'版本', u''),
											'game_type' : g.get(u'分类', u''),
											'comment_num' : comment_num,
											'pkg_size' : g.get(u'大小' u''),
											'dt' : dt,
											'imgs' : u','.join(g.get('imgs', [])),
												})
				db_conn.merge(item)
	mylogger.info("get muzhiwan detail %s" % count)
	db_conn.commit()


def get_muzhiwan_detail_by_id(url):
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
			for ret in info.find('div', class_='clearfix').find_all('li'):
				segs = ret.text.split(u'：')
				if len(segs) == 2:
					mydict[segs[0]] = segs[1]
		imgs = soup.find('div', class_="img_screen")	
		if imgs is not None:
			mydict['imgs'] = [i.find('img').get('src') for i in imgs.find_all('li')]
		summary = soup.find('p', itemprop="description")
		if summary is not None:
			mydict['description'] = summary.text
	return mydict


def get_huawei_detail():
	count = 0
	mylogger.info("get huawei detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==18):
		g = get_huawei_detail_by_id(ret.url)
		if g:
			dt = unicode(datetime.date.today())
			ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
			if not ins:
				count += 1 
				item = GameDetailByDay(**{
											'kc_id': ret.id,
											'summary' : g.get('description', u''),
											'version' : g.get(u'版本', u''),
											'game_type' : g.get(u'分类', u''),
											'download_num' : g.get('download_num', u''),
											'comment_num' : g.get('comment_num', u''),
											'pkg_size' : g.get(u'大小', u''),
											'author' : g.get('author', u''),
											'dt' : dt,
											'imgs' : u','.join(g.get('imgs', [])),
												})
				db_conn.merge(item)
				if count % 100 == 0:
					mylogger.info("huawei detail commit %s" % count)
					db_conn.commit()
	mylogger.info("get huawei detail %s" % count)
	db_conn.commit()

def get_huawei_detail_by_id(url):
	mydict = {}
	try:
		response = s.get(url, timeout=15)
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
		time.sleep(5)
		response = T(404)
	if response.status_code == 200:
		soup = BeautifulSoup(response.text)
		for d in soup.find_all('li', class_='ul-li-detail'):
			if u'开发者：' in d.text:
				mydict['author'] = d.find('span').get('title')
			else:
				segs = d.text.split(u'：')
				if len(segs) == 2:
					mydict[segs[0]] = segs[1]
		info = soup.find('ul', class_='app-info-ul nofloat')
		if info is not None:
			lis = info.find_all('li')
			if len(lis) >= 2:
				download_li = lis[1]
				download_span = download_li.find('span', class_='grey sub')
				if download_span is not None:
					m = re.search('\d+', download_span.text)
					if m is not None:
						mydict['download_num'] = m.group()
		imgs = soup.find('ul', class_="imgul")	
		if imgs is not None:
			mydict['imgs'] = [i.find('img').get('src') for i in imgs.find_all('li')]
		summary = soup.find('div', id="app_strdesc")
		if summary is not None:
			mydict['description'] = summary.text
		comment_list = soup.find('div', id='comment_list')
		if comment_list is not None:
			comment = comment_list.find('span', class_='title')
			if comment is not None:
				m = re.search('\d+', comment.text)
				if m is not None:
					mydict['comment_num'] = m.group()
	return mydict

def get_kuaiyong_detail():
	count = 0
	mylogger.info("get kuaiyong detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==19):
		g = get_kuaiyong_detail_by_id(ret.url)
		#for k, v in g.iteritems():
		#	print k, v
		if g:
			dt = unicode(datetime.date.today())
			ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
			if not ins:
				count += 1 
				item = GameDetailByDay(**{
											'kc_id': ret.id,
											'summary' : g.get('description', u''),
											'version' : g.get(u'版　　本', u''),
											'game_type' : g.get(u'类　　别', u''),
											'pkg_size' : g.get(u'大　　小', u''),
											'download_num' : g.get(u'下载', u''),
											'dt' : dt,
											'rating' : g.get('rating', u''),
											'imgs' : u','.join(g.get('imgs', [])),
												})
				db_conn.merge(item)
				if count % 100 == 0:
					mylogger.info("kuaiyong detail commit %s" % count)
					db_conn.commit()
	mylogger.info("get kuaiyong detail %s" % count)
	db_conn.commit()

def get_kuaiyong_detail_by_id(URL):
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
				app_star = base_list.find('p', class_='app-star') 
				if app_star is not None:
					mydict['rating'] = len(app_star.find_all('span', class_='highlight'))
		detail = soup.find('div', class_='detail')
		if detail is not None:
			preview_contents = detail.find('div', class_='preview-content')
			if preview_contents is not None:
				mydict['imgs'] = [p.get('src') for p in preview_contents.find_all('img')]
		detail_content = soup.find('div', class_='detail-content-inner')
		if detail_content is not None:
			mydict['description'] = detail_content.text
		#comment_span = soup.find('div', class_='comments')
		#if comment_span is not None:
	#		print comment_span.text, '*****'
	return mydict


def get_kuaiyong_detail():
	count = 0
	mylogger.info("get kuaiyong detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==19):
		g = get_kuaiyong_detail_by_id(ret.url)
		#for k, v in g.iteritems():
		#	print k, v
		if g:
			dt = unicode(datetime.date.today())
			ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
			if not ins:
				count += 1 
				item = GameDetailByDay(**{
											'kc_id': ret.id,
											'summary' : g.get('description', u''),
											'version' : g.get(u'版　　本', u''),
											'game_type' : g.get(u'类　　别', u''),
											'pkg_size' : g.get(u'大　　小', u''),
											'download_num' : g.get(u'下载', u''),
											'dt' : dt,
											'rating' : g.get('rating', u''),
											'imgs' : u','.join(g.get('imgs', [])),
												})
				db_conn.merge(item)
				if count % 100 == 0:
					mylogger.info("kuaiyong detail commit %s" % count)
					db_conn.commit()
	mylogger.info("get kuaiyong detail %s" % count)
	db_conn.commit()



def get_anzhi_detail_by_id(URL):
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
		stars_detail = soup.find('div', id='stars_detail')
		if stars_detail is not None:
			m = re.search('(\d+)px', stars_detail.get('style'))
			if m is not None:
				mydict['rating'] = round(m.group(1)/30.0, 1)
		app_detail_infor = soup.find('div', class_='app_detail_infor')
		if app_detail_infor is not None:
			mydict['description'] = app_detail_infor.text.strip()
		section_body = soup.find('div', class_='section-body')
		if section_body is not None:
			mydict['imgs'] = [u"http://www.anzhi.com%s" % i.get('src') for i in section_body.find_all('img')]
	return mydict

def get_wandoujia_detail():
	count = 0
	mylogger.info("get wandoujia detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==23):
		g = get_wandoujia_detail_by_id(ret.url)
		#for k, v in g.iteritems():
		#	print k, v
		if g is not None:
			dt = unicode(datetime.date.today())
			categories = g.get('categories', [])
			game_type = u",".join([c['name'] for c in categories if c['level']==2])
			apk = {}
			apk_list = g.get('apk', [])
			if len(apk_list) >= 1:
				apk = apk_list[0]
			ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
			if not ins:
				count += 1 
				item = GameDetailByDay(**{
											'kc_id': ret.id,
											'summary' : g.get('description', u''),
											'version' : apk.get('versionName', u''),
											'game_type' : game_type,
											'pkg_size' : apk.get('size', u''),
											'comment_num' : g.get('commentsCount', u''),
											'download_num' : g.get('downloadCount', u''),
											'author' : g['developer'].get('name', u''),
											'dt' : dt,
											'imgs' : u','.join(g.get('screenshots',{}).get('normal', [])),
												})
				db_conn.merge(item)
				if count % 100 == 0:
					mylogger.info("wandoujia detail commit %s" % count)
					db_conn.commit()
			else:
				ins.pkg_size = apk.get('size', u'')
				ins.version = apk.get('versionName', u'')
	mylogger.info("get wandoujia detail %s" % count)
	db_conn.commit()


def get_wandoujia_detail_by_id(url):
	try:
		r = requests.get(url, timeout=10)
	except Exception,e:
		r = T(404)
		mylogger.error("### %s ### %s" % (url.encode('utf-8'), traceback.format_exc()))
	if r.status_code == 200:
		d = r.json()
		entity = d['entity']
		if entity:
			detail = entity[0].get('detail', {})['appDetail']
			return detail
	return None


def get_pp_detail():
	count = 0
	mylogger.info("get pp detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.title2!=u'').filter(KC_LIST.source==24):
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			g = get_pp_detail_by_id(ret.title2)
			if g is not None:	
				comments_info = get_pp_comments_by_id(ret.title2)
				count += 1 
				item = GameDetailByDay(**{
											'kc_id': ret.id,
											'summary' : g.get('content', u''),
											'version' : g.get('ver', u''),
											'game_type' : g.get('catName', u''),
											'pkg_size' : g.get('fileSize', u''),
											'comment_num' : comments_info.get('commentCount', u''),
											'download_num' : g.get('downCount', u''),
											'topic_num_total' : g.get('collectCount', u''),
											'rating' : g.get('allVerStar', u''),
											'dt' : dt,
											'imgs' : g.get('ipadImgs', u''),
												})
				db_conn.merge(item)
				if count % 50 == 0:
					sleep(3)
					mylogger.info("pp detail commit %s" % count)
					db_conn.commit()
				if count % 20 == 0:
					sleep(1.23)
	mylogger.info("get pp detail %s" % count)
	db_conn.commit()


def get_pp_detail_by_id(gid):
	try:
		d = {"site":1, "id": gid}
		r = requests.post('http://pppc2.25pp.com/pp_api/ios_appdetail.php', data=d)
		return r.json()
	except Exception,e:
		mylogger.error("get %s detail \t%s" % (gid.encode('utf-8'), traceback.format_exc()))
	return None

def get_pp_comments_by_id(gid):
	try:
		d = {"s":1, "a":101, "i": gid, "p":1, "l":1}
		r = requests.post('http://pppc2.25pp.com/pp_api/comment.php', data=d)
	except Exception,e:
		mylogger.error("get %s comments \t%s" % (gid.encode('utf-8'), traceback.format_exc()))
		r = T(404)
	if r.status_code == 200:
		return r.json()
	return {}

def main():
	get_open_play_detail()
	get_xiaomi_new_detail()
	get_xiaomi_rpg_detail()
	get_9game_detail()
	get_18183_detail()
	get_appicsh_detail()
	get_vivo_detail()
	get_coolpad_detail()
	get_gionee_detail()
	get_leveno_detail()
	get_iqiyi_detail()
	get_sogou_detail()
	get_dangle_detail()
	get_muzhiwan_detail()
	get_huawei_detail()
	get_wandoujia_detail()

if __name__ == '__main__':
	get_pp_detail()

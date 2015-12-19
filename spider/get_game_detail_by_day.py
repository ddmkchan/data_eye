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
import xmltodict
import datetime

db_conn = new_session()
mylogger = get_logger('get_game_detail')


class EX:
	
	msg = ""


def get_9game_detail():
	mylogger.info("get 9game detail start ...")
	count = 0
	error_times = 0
	sess = requests.session()
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==0).filter(KC_LIST.publish_date>=u'2015-10-01'):
		if error_times >= 20:
			mylogger.info("9game reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			try:
				p = proxies[random.randrange(len(proxies))]
				response = sess.get(ret.url, timeout=20, proxies=p)
				if response.status_code == 200:
					count += 1
					soup = BeautifulSoup(response.text)
					spec_pic = soup.find('div', class_='spec-pic')
					imgs 	= u''
					rating 	= u''
					game_type = u''
					comments_num = u''
					topic_num_day = u''
					topic_num_total = u''
					if spec_pic is not None:
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
					if count % 50 == 0:
						sleep(3)
						mylogger.info("9game detail commit %s" % count)
						db_conn.commit()
			except Exception,e:
				error_times += 1
				mylogger.error("%s\t%s" % (ret.url.encode('utf-8'), traceback.format_exc()))

	mylogger.info("get 9game detail %s" % count)
	db_conn.commit()

def get_9game_info_from_bbs(url):
	try:
		p = proxies[random.randrange(len(proxies))]
		response = requests.get(url, timeout=10, proxies=p)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			topics = soup.find('span', 'xs1 xw0 i')	
			if topics is not None:
				nums = topics.find_all('strong')
				if len(nums) == 2:
					today_nums, total_nums = [i.text for i in nums]
					return today_nums, total_nums
	except Exception,e:
		mylogger.error("%s 9game bbs \t%s" % (url.encode('utf-8'), traceback.format_exc()))
	return None

def get_18183_detail():
	mylogger.info("get 18183 detail start ...")
	count = 0 
	error_times = 0
	sess = requests.session()
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.publish_date>=u'2015-10-01').filter(KC_LIST.url!=u'').filter(KC_LIST.source==2):
		if error_times >= 10:
			mylogger.info("18183 reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			try:
				response = sess.get(ret.url, timeout=10)
				count += 1
				topic_num_total = u''
				game_type = u''
				pkg_size = u''
				summary = u''
				imgs = u''
				r = response.text.encode('ISO-8859-1').decode('utf-8')
				soup = BeautifulSoup(r)
				for li1 in soup.find_all('li', class_='li1'):
					codes = li1.find_all('code')
					spans = li1.find_all('span')
					for i in xrange(len(codes)):
						if codes[i].text == u'类型：':
							game_type = spans[i].text.strip()
						if codes[i].text == u'关注：':
							try:
								rs = requests.get(spans[i].find('script').get('src'))
								if rs.status_code == 200:
									m = re.search('\d+', rs.text)
									if m is not None:
										topic_num_total = m.group()
							except Exception,e:
								mylogger.error("18183 topic page error and sleep 3s %s" % (traceback.format_exc()))
								sleep(3)
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
				item = GameDetailByDay(**{'kc_id': ret.id,
												'dt' : dt,
												'imgs' : imgs,
												'summary' : summary,
												'pkg_size' : pkg_size,
												'game_type' : game_type,
												'topic_num_total' : topic_num_total,
												})
				db_conn.merge(item)
				if count % 100 == 0:
					sleep(3)
					mylogger.info("18183 detail commit %s" % count)
					db_conn.commit()
			except Exception,e:
				error_times += 1
				mylogger.error("%s\t%s" % (ret.url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get 18183 detail %s" % count)
	db_conn.commit()


def get_appicsh_detail():
	mylogger.info("get appicsh detail start ...")
	count = 0
	error_times = 0
	sess = requests.session()
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.source==3).filter(KC_LIST.url!=u''):
		if error_times >= 10:
			mylogger.info("appicsh reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			try:
				response = sess.get(ret.url, timeout=10)
				d = response.json()
				if d['obj'] is not None and d['obj']['appInfo'] is not None:
					appinfo = d['obj']['appInfo']
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
			except Exception,e:
				error_times += 1
				mylogger.error("%s\t%s" % (ret.url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get appicsh detail %s" % count)
	db_conn.commit()
			

def get_xiaomi_new_id_map():
	mydict = {}
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==5):
		mydict[int(ret.game_id)] = ret.id
	return mydict


def get_xiaomi_new_detail():
	id_map = get_xiaomi_new_id_map()
	count = 0
	for page in xrange(1, 23):
		url = "http://app.migc.xiaomi.com/cms/interface/v5/subjectgamelist1.php?pageSize=20&page=%s&subId=138" % page
		try:
			r = requests.get(url, timeout=10)
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
								count += 1
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
		except Exception,e:
			mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	db_conn.commit()
	mylogger.info("get xiaomi_new detail %s" % count)
							

def get_xiaomi_rpg_id_map():
	mydict = {}
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==6):
		mydict[int(ret.game_id)] = ret.id
	return mydict


def get_xiaomi_rpg_detail():
	count = 0
	id_map = get_xiaomi_rpg_id_map()
	for page in xrange(1, 2):
		url = "http://app.migc.xiaomi.com/cms/interface/v5/subjectgamelist1.php?subId=203&pageSize=150&page=%s" % page
		try:
			r = requests.get(url, timeout=10)
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
								count += 1
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
		except Exception,e:
			mylogger.error("%s\t%s" % (url, traceback.format_exc()))
	db_conn.commit()
	mylogger.info("get xiaomi rpg detail %s" % count)
							

def get_open_play_detail():
	count = 0
	error_times = 0
	sess = requests.session()
	mylogger.info("get open play detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==7):
		if error_times >= 10:
			mylogger.info("open play detail reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			_url = u'http://open.play.cn/api/v2/mobile/game_detail.json?game_id=%s' % ret.game_id
			try:
				response = sess.get(_url, timeout=10)
				d = response.json()
				if d.get('text', u'') == u'success':
					count += 1 
					g = d['ext']['game_detail']
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
					if count % 100 == 0:
						sleep(3)
						mylogger.info("open play detail commit %s" % count)
						db_conn.commit()
			except Exception,e:
				error_times += 1
				mylogger.error("%s\t%s" % (_url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get open play detail %s" % count)
	db_conn.commit()

def get_vivo_detail():
	count = 0
	error_times = 0
	sess = requests.session()
	mylogger.info("get vivo detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==8):
		if error_times >= 10:
			mylogger.info("vivo reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			try:
				response = sess.get(ret.url, timeout=10)
				d = response.json()
				if d is not None and 'result' in d and d['result']:
					g = d.get('game')
					if g is not None:
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
			except Exception,e:
				error_times += 1
				mylogger.error("%s\t%s" % (ret.url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get vivo play detail %s" % count)
	db_conn.commit()


def get_coolpad_detail():
	count = 0
	error_times = 0
	mylogger.info("get coolpad detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==9):
		if error_times >= 20:
			mylogger.info("coolpad reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			g =  get_coolpad_detail_by_id(ret.game_id)
			if isinstance(g, EX):
				error_times += 1
			elif g is not None:
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
	try:
		r = requests.post(url, data=raw_data, headers={'Content-Type': 'application/xml'})
		if r.status_code == 200:
			t = re.sub(u'\r|\n', '', r.text)
			doc = xmltodict.parse(t)
			d = doc['response']['reslist']['res']
			if d['@rid'] != u'':
				return d
	except Exception,e:
		mylogger.error("%s\t%s" % (resid.encode('utf-8'), traceback.format_exc()))
		return EX()
	return None

def get_gionee_detail():
	count = 0
	error_times = 0
	sess = requests.session()
	mylogger.info("get gionee detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==10):
		if error_times >= 10:
			mylogger.info("gionee reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			_url = u"http://game.gionee.com/Api/Local_Gameinfo/getDetails?gameId=%s" % ret.game_id
			try:
				response = sess.get(_url, timeout=10)
				d = response.json()
				if 'success' in d and d['success']:
					g = d['data']
					count += 1 
					item = GameDetailByDay(**{
												'kc_id': ret.id,
												'rating' : g.get('score', u''),
												'download_num' : g.get('downloadCount', u''),
												'author' : g.get('publisher', u''),
												'game_type' : g.get('category', u''),
												'version' : g.get('versionName', u''),
												'pkg_size' : g.get('fileSize' u''),
												'dt' : dt,
												'imgs' : u','.join(g['bannerList']['fullPicture']),
													})
					db_conn.merge(item)
			except Exception,e:
				error_times += 1
				mylogger.error("%s\t%s" % (_url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get gionee play detail %s" % count)
	db_conn.commit()



def get_leveno_detail():
	count = 0
	error_times = 0
	sess = requests.session()
	mylogger.info("get lenovo detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.pkg_name!=u'').filter(KC_LIST.source==11):
		if error_times >= 10:
			mylogger.info("leveno reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			_url = u"http://yx.lenovomm.com/business/app!getAppDetail5.action?dpi=480&height=1920&dev=ph&width=1080&cpu=armeabi-v7a&pn=%s&uid=72DB07100FC223A2EDE82F4A44AE96B4&os=4.4.4&perf=hp&model=MI 4LTE&type=0&density=xx&mac=7A031DAB40535B3F5E204582EB961FC5" % ret.pkg_name
			try:
				p = proxies[random.randrange(len(proxies))]
				response = sess.get(_url, timeout=10, proxies=p)
				d = response.json()
				if 'app' in d:
					g = d['app']
					count += 1 
					item = GameDetailByDay(**{
												'kc_id': ret.id,
												'rating' : g.get('averageStar', u''),
												'game_type' : g.get('categoryName', u''),
												'version' : g.get('version', u''),
												'pkg_size' : g.get('size' u''),
												'dt' : dt,
												'download_num' : g.get('realDownCount', u''),
												'summary' : g.get('description', u''),
												'imgs' : g['snapList'],
													})
					db_conn.merge(item)
			except Exception,e:
				sleep(1.23)
				error_times += 1
				mylogger.error("%s\t%s" % (_url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get lenovo detail %s" % count)
	db_conn.commit()


def get_iqiyi_detail():
	count = 0
	error_times = 0
	mylogger.info("get iqiyi detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==12):
		if error_times >= 20:
			mylogger.info("iqiyi reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			d =  get_iqiyi_detail_by_id(ret.game_id)
			if isinstance(d, EX):
				error_times += 1
			elif d is not None:
				g = d['app']
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
		return EX()
	return None

def get_sogou_detail():
	count = 0
	error_times = 0
	sess = requests.session()
	mylogger.info("get sogou detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==14):
		if error_times >= 10:
			mylogger.info("sogou reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			_url = u"http://mobile.zhushou.sogou.com/m/appDetail.html?id=%s" % ret.game_id
			try:
				response = sess.get(_url, timeout=10)
				d = response.json()
				g = d['ainfo']
				count += 1 
				item = GameDetailByDay(**{
											'kc_id': ret.id,
											'rating' : g.get('score', u''),
											'summary' : g.get('desc', u''),
											'version' : g.get('vn', u''),
											'game_type' : d.get('tgroup', {}).get('name', u''),
											'download_num' : g.get('dc', u''),
											'author' : g.get('author', u''),
											'pkg_size' : g.get('size' u''),
											'dt' : dt,
											'imgs' : u",".join([i.get('url', u'') for i in d['images']]),
												})
				db_conn.merge(item)
			except Exception,e:
				error_times += 1
				mylogger.error("%s\t%s" % (_url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get sogou detail %s" % count)
	db_conn.commit()


def get_dangle_detail():
	count = 0
	error_times = 0
	mylogger.info("get dangle detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==15):
		if error_times >= 20:
			mylogger.info("dangle reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			g =  get_dangle_detail_by_id(ret.game_id)
			if isinstance(g, EX):
				error_times += 1
			elif g is not None:
				count += 1 
				packageTOs = {}
				if 'packageTOs' in g:
					packageTOs = g['packageTOs'][0] if g['packageTOs'] else {}
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
	url = u"http://api2014.digua.d.cn/newdiguaserver/res/detail?id=%s&resourceType=5"% gid
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
	try:
		r = requests.post(url, headers=headers, timeout=30)
		if r.status_code == 200:
			return r.json()
	except Exception,e:
		mylogger.error("%s\t%s" % (url.encode('utf-8'), traceback.format_exc()))
		return EX()
	return None

def get_muzhiwan_detail():
	count = 0
	error_times = 0
	mylogger.info("get muzhiwan detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==17):
		if error_times >= 20:
			mylogger.info("muzhiwan reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			g = get_muzhiwan_detail_by_id(ret.url)
			if isinstance(g, EX):
				error_times += 1
			elif g:
				#m = re.search(u'(\d+)个', g.get(u'评论数', u''))
				#comment_num = m.group(1) if m is not None else u''
				count += 1 
				item = GameDetailByDay(**{
												'kc_id': ret.id,
												'summary' : g.get('description', u''),
												'version' : g.get(u'版本', u''),
												'game_type' : g.get(u'分类', u''),
												'comment_num' : g.get('comments', u''),
												'pkg_size' : g.get(u'大小' u''),
												'dt' : dt,
												'imgs' : u','.join(g.get('imgs', [])),
													})
				db_conn.merge(item)
				if count % 100 == 0:
					sleep(1.23)
					mylogger.info("muzhiwan detail %s commit ... " % count)
	mylogger.info("get muzhiwan detail %s" % count)
	db_conn.commit()


def get_muzhiwan_comment_by_gid(gid):
	try:
		url = u'http://www.muzhiwan.com/index.php?action=game&opt=readHit&gid=%s' % gid
		r = requests.get(url)
		if r.status_code == 200:
			return r.text
	except Exception,e:
		mylogger.error("get muzhiwan comments %s\t%s" % (url, traceback.format_exc()))
	return None

def get_muzhiwan_detail_by_id(url):
	mydict = {}
	try:
		response = requests.get(url, timeout=10)
		soup = BeautifulSoup(response.text)
		info = soup.find('div', class_='detail_info')
		gid = soup.find('input', id='gid')
		if gid is not None:
			comments = get_muzhiwan_comment_by_gid(gid.get('value'))
			if comments is not None:
				mydict['comments'] = comments
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
	except Exception,e:
		mylogger.error("%s\t%s" % (url.encode('utf-8'), traceback.format_exc()))
		return EX()
	return mydict


def get_huawei_detail():
	count = 0
	error_times = 0
	mylogger.info("get huawei detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==18):
		if error_times >= 20:
			mylogger.info("huawei reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			g = get_huawei_detail_by_id(ret.url)
			if isinstance(g, EX):
				error_times += 1
			elif g:
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
		p = proxies[random.randrange(len(proxies))]
		response = requests.get(url, timeout=20, proxies=p)
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
	except Exception,e:
		mylogger.error("%s\t%s" % (url.encode('utf-8'), traceback.format_exc()))
		sleep(3)
		return EX()
	return mydict

def get_kuaiyong_detail():
	count = 0
	error_times = 0
	mylogger.info("get kuaiyong detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==19):
		if error_times >= 20:
			mylogger.info("kuaiyong reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			g = get_kuaiyong_detail_by_id(ret.url)
			if isinstance(g, EX):
				error_times += 1
			elif g:
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
		p = proxies[random.randrange(len(proxies))]
		response = requests.get(URL, timeout=15, proxies=p)
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
	except Exception,e:
		#sleep(3.21)
		mylogger.error("%s\t%s" % (URL.encode('utf-8'), traceback.format_exc()))
		return EX()
	return mydict


def get_anzhi_detail():
	
	count = 0
	mylogger.info("get kuaiyong detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==21):
		count += 1 
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			g = get_anzhi_detail_by_id(ret.url)
			if g:
				dt = unicode(datetime.date.today())
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
	except Exception,e:
		mylogger.error("%s\t%s" % (URL.encode('utf-8'), traceback.format_exc()))
	return mydict

def get_wandoujia_detail():
	count = 0
	error_times = 0
	mylogger.info("get wandoujia detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==23):
		if error_times >= 20:
			mylogger.info("wandoujia reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			g = get_wandoujia_detail_by_id(ret.url)
			if isinstance(g, EX):
				error_times += 1
			elif g is not None:
				count += 1 
				categories = g.get('categories', [])
				game_type = u",".join([c['name'] for c in categories if c['level']==2])
				apk = {}
				apk_list = g.get('apk', [])
				if len(apk_list) >= 1:
					apk = apk_list[0]
				developer = g.get('developer', {})
				item = GameDetailByDay(**{
											'kc_id': ret.id,
											'summary' : g.get('description', u''),
											'version' : apk.get('versionName', u''),
											'game_type' : game_type,
											'pkg_size' : apk.get('size', u''),
											'comment_num' : g.get('commentsCount', u''),
											'download_num' : g.get('downloadCount', u''),
											'author' : developer.get('name', u''),
											'dt' : dt,
											'imgs' : u','.join(g.get('screenshots',{}).get('normal', [])),
												})
				db_conn.merge(item)
				if count % 100 == 0:
					mylogger.info("wandoujia detail commit %s" % count)
					db_conn.commit()
	mylogger.info("get wandoujia detail %s" % count)
	db_conn.commit()


def get_wandoujia_detail_by_id(url):
	try:
		r = requests.get(url, timeout=10)
		if r.status_code == 200:
			d = r.json()
			entity = d['entity']
			if entity:
				detail = entity[0].get('detail', {})['appDetail']
				return detail
	except Exception,e:
		mylogger.error("### %s ### %s" % (url.encode('utf-8'), traceback.format_exc()))
		return EX()
	return None


def get_meizu_detail_by_id(gid):
	URL = u"http://api-game.meizu.com/games/public/detail/%s" % gid
	try:
		response = requests.get(URL, timeout=30)
		if response.status_code == 200:
			j = response.json()
			if 'value' in j:
				return j['value']
	except Exception,e:
		mylogger.error("%s\t%s" % (URL.encode('utf-8'), traceback.format_exc()))
		return EX()
	return None


def get_meizu_detail():
	count = 0
	error_times = 0
	mylogger.info("get meizu detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==25):
		if error_times >= 20:
			mylogger.info("meizu reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			g = get_meizu_detail_by_id(ret.game_id)
			if isinstance(g, EX):
				error_times += 1
			elif g is not None:	
				count += 1 
				item = GameDetailByDay(**{
									'kc_id': ret.id,
									'summary' : g.get('description', u''),
									'version' : g.get('version_name', u''),
									'game_type' : g.get('category_name', u''),
									'pkg_size' : g.get('size', u''),
									'comment_num' : g.get('evaluate_count', u''),
									'download_num' : g.get('download_count', u''),
									'author' : g.get('publisher', u''),
									'rating' : g.get('avg_score', u''),
									'dt' : dt,
									'imgs' : u','.join([i.get('image') for i in g.get('images', [])]),
										})
				db_conn.merge(item)
	mylogger.info("get meizu detail %s" % count)
	db_conn.commit()


def get_youku_detail_by_id(app_id):
	URL = u"http://api.gamex.mobile.youku.com/v2/app/detail?product_id=1&app_id=%s" % app_id
	try:
		response = requests.get(URL, timeout=10)
		if response.status_code == 200:
			j = response.json()
			return j['app']
	except Exception,e:
		mylogger.error("%s\t%s" % (URL.encode('utf-8'), traceback.format_exc()))
		return EX()
	return None

def get_youku_detail():
	count = 0
	error_times = 0
	mylogger.info("get youku detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==13):
		if error_times >= 20:
			mylogger.info("youku reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			g = get_youku_detail_by_id(ret.game_id)
			if isinstance(g, EX):
				error_times += 1
			elif g is not None:	
				count += 1 
				item = GameDetailByDay(**{
									'kc_id': ret.id,
									'summary' : g.get('desc', u''),
									'version' : g.get('version', u''),
									'game_type' : g.get('type', u''),
									'pkg_size' : g.get('size', u''),
									'rating' : g.get('score', u''),
									'download_num' : g.get('total_downloads', u''),
									'dt' : dt,
									'imgs' : u','.join(g.get('screenshot', [])),
										})
				db_conn.merge(item)
	mylogger.info("get youku detail %s" % count)
	db_conn.commit()

def get_360zhushou_app_detail():
	count = 0
	error_times = 0
	mylogger.info("get 360zhushou app detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.pkg_name!=u'').filter(KC_LIST.source==4):
		if error_times >= 10:
			mylogger.info("360zhushou reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			url = "http://125.88.193.234/mintf/getAppInfoByIds?pname=%s" % ret.pkg_name
			try:
				r = requests.get(url, timeout=10)
				if r.status_code == 200:
					j = r.json()
					if len(j['data'])>=1:
						g = j['data'][0]
						count += 1 
						comments_url = "http://comment.mobilem.360.cn/comment/getCommentTags?objid=%s" % ret.game_id
						comments_num = u''
						try:
							get_comments_r = requests.get(comments_url)
							if get_comments_r.status_code == 200:
								comments_j = get_comments_r.json()
								for tag in comments_j['data']['tag']:
									if tag.get('title', u'') == u'全部':
										comments_num = tag.get('num', u'')
						except Exception,e :
							mylogger.error("360zhushou app comments #### #### \t%s" % (traceback.format_exc()))
						item = GameDetailByDay(**{
									'kc_id': ret.id,
									'summary' : g.get('brief', u''),
									'version' : g.get('version_name', u''),
									'game_type' : g.get('category_name', u''),
									'pkg_size' : g.get('size', u''),
									'rating' : g.get('rating', u''),
									'author' : g.get('corp', u''),
									'comment_num' : comments_num,
									'download_num' : g.get('download_times', u''),
									'dt' : dt,
									'imgs' : u','.join(g.get('trumb', u'').split(u'|')),
										})
						db_conn.merge(item)
			except Exception,e:
				error_times += 1
				mylogger.error("360zhushou app #### %s #### \t%s" % (ret.pkg_name.encode('utf-8'), traceback.format_exc()))
				
	mylogger.info("get 360 app detail %s" % count)
	db_conn.commit()


def get_i4_app_detail():
	count = 0
	error_times = 0
	mylogger.info("get i4 app detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==16):
		if error_times >= 10:
			mylogger.info("i4 reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			url = u"http://app3.i4.cn/controller/action/online.go?store=3&module=1&id=%s&reqtype=5" % ret.game_id
			try:
				r = requests.get(url, timeout=10)
				if r.status_code == 200:

					j = r.json()
					if j['result']['list'] is not None and len(j['result']['list']) >= 1:
						g = j['result']['list'][0]
						count += 1 
						item = GameDetailByDay(**{
									'kc_id': ret.id,
									'summary' : g.get('shortNote', u''),
									'version' : g.get('shortVersion', u''),
									'game_type' : g.get('typeName', u''),
									'pkg_size' : g.get('sizeByte', u''),
									'author' : g.get('company', u''),
									'download_num' : g.get('downloadCount', u''),
									'dt' : dt,
									'imgs' : u','.join([u"http://d.image.i4.cn/image/%s" % img.get('url') for img in json.loads(g.get('image', []))]),
										})
						db_conn.merge(item)
			except Exception,e:
				error_times += 1
				mylogger.error("i4 app #### %s #### \t%s" % (ret.game_id.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get i4 app detail %s" % count)
	db_conn.commit()


def get_xyzs_app_detail():
	count = 0
	error_times = 0
	mylogger.info("get xyzs app detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==26):
		if error_times >= 10:
			mylogger.info("xyzs reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			try:
				url = "http://interface.xyzs.com/v2/ios/c01/app"
				d = {'itunesid': ret.game_id}
				r = requests.get(url, params=d, timeout=10)
				if r.status_code == 200:
					j = r.json()
					if j['code'] == 200:
						g = j['data']['app']
						count += 1 
						item = GameDetailByDay(**{
									'kc_id': ret.id,
									'summary' : g.get('content', u''),
									'version' : g.get('version', u''),
									'game_type' : g.get('apptypesno', u''),
									'pkg_size' : g.get('size', u''),
									'download_num' : g.get('downloadnum', u''),
									'dt' : dt,
									'imgs' : u','.join(g.get('iphoneimg', [])),
										})
						db_conn.merge(item)
			except Exception,e:
				error_times += 1
				mylogger.error("xyzs app #### %s #### \t%s" % (ret.game_id.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get xyzs app detail %s" % count)
	db_conn.commit()


def get_91play_detail():
	count = 0
	error_times = 0
	mylogger.info("get 91play app detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==27):
		if error_times >= 10:
			mylogger.info("91play reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			try:
				url = "http://play.91.com/api.php/Api/index"
				raw_data = {"id": int(ret.game_id),"firmware":"19","time":1449458211590,"device":1,"action":30005,"app_version":302,"action_version":4,"mac":"7b715ce093480b34d6987","debug":0}
				response = requests.post(url, data=raw_data, timeout=10)
				if response.status_code == 200:
					j = response.json() 
					if j['data'] is not None:
						g = json.loads(j['data'])
						count += 1 
						item = GameDetailByDay(**{
									'kc_id': ret.id,
									'summary' : g.get('content', u''),
									'rating' : g.get('score', u''),
									'version' : g.get('version', u''),
									'game_type' : g.get('type_name', u''),
									'pkg_size' : g.get('app_size', u''),
									'author' : g.get('developer', u''),
									'download_num' : g.get('download_count', u''),
									'dt' : dt,
									'imgs' : g.get('img_urls', u'')
										})
						db_conn.merge(item)
			except Exception,e:
				error_times += 1
				mylogger.error("91play app detail #### %s #### \t%s" % (ret.game_id.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get 91play app detail %s" % count)
	db_conn.commit()

def get_360_gamebox_detail():
	count = 0
	error_times = 0
	mylogger.info("get 360_gamebox app detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.pkg_name!=u'').filter(KC_LIST.source==28):
		if error_times >= 10:
			mylogger.info("360_gamebox reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			try:
				url = "http://next.gamebox.360.cn/7/xgamebox/getappintro?pname=%s" % ret.pkg_name
				response = requests.get(url, timeout=10)
				if response.status_code == 200:
					j = response.json() 
					if j['data'] is not None and j['data']['info'] is not None and j['data']['info']:
						g = j['data']['info']
						count += 1 
						#for k, v in g.iteritems():
						#	print k, v
						item = GameDetailByDay(**{
									'kc_id': ret.id,
									'summary' : g.get('brief', u''),
									'rating' : g.get('rating', u''),
									'version' : g.get('version_name', u''),
									'game_type' : g.get('category_name', u''),
									'pkg_size' : g.get('size', u''),
									'author' : g.get('corp', u''),
									'download_num' : g.get('download_times', u''),
									'dt' : dt,
									'imgs' : u",".join(g.get('trumb', u'').split(u'|'))
										})
						db_conn.merge(item)
			except Exception,e:
				error_times += 1
				mylogger.error("360_gamebox app detail #### %s #### \t%s" % (ret.pkg_name.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get 360_gamebox app detail %s" % count)
	db_conn.commit()


def get_lenovo_shop_detail():
	count = 0
	error_times = 0
	mylogger.info("get lenovo_shop app detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.pkg_name!=u'').filter(KC_LIST.source==30):
		if error_times >= 10:
			mylogger.info("lenovo_shop reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			try:
				headers = {"clientid": "141623-2-2-19-1-3-1_480_i865931027730878t19700201770903586_c20524d1p1"}
				url = "http://223.202.25.30/ams/api/appinfo?l=zh-CN&pn=%s&vc=100150928&woi=0&pa=ams5.0_141623-2-2-19-1-3-1_480-8" % ret.pkg_name
				response = requests.get(url, timeout=10, headers=headers)
				if response.status_code == 200:
					j = response.json() 
					if j['appInfo'] is not None:
						g = j['appInfo']
						count += 1 
						#for k, v in g.iteritems():
						#	print k, v
						item = GameDetailByDay(**{
									'kc_id': ret.id,
									'summary' : g.get('description', u''),
									'rating' : g.get('averageStar', u''),
									'version' : g.get('version', u''),
									'game_type' : g.get('typeName', u''),
									'pkg_size' : g.get('size', u''),
									'comment_num' : get_lenovo_shop_comment_by_pkg(ret.pkg_name),
									'author' : g.get('developerName', u''),
									'download_num' : g.get('realDownCount', u''),
									'dt' : dt,
									'imgs' : u",".join([img.get('APPIMG_PATH', u'') for img in g.get('snapList', [])])
										})
						db_conn.merge(item)
			except Exception,e:
				error_times += 1
				mylogger.error("lenovo_shop app detail #### %s #### \t%s" % (ret.pkg_name.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get lenovo_shop app detail %s" % count)
	db_conn.commit()

def get_lenovo_shop_comment_by_pkg(pkg_name):
	url = "http://223.202.25.30/comment/api/commentlist?bizCode=APP&bizIdentity=%s&startIndex=1&count=10&orderBy=DATE" % pkg_name
	headers = {"clientid": "141623-2-2-19-1-3-1_480_i865931027730878t19700201770903586_c20524d1p1"}
	try:
		r = requests.get(url, timeout=10, headers=headers)
		if r.status_code == 200:
			j = r.json()
			if j['data'] is not None:
				return j['data'].get('totalCount', u'')
	except Exception, e:
		mylogger.error("get lenovo shop comment %s" % traceback.format_exc())
	return u''


def get_wostroe_comment_by_product_id(product_id):
	headers = {
			"phoneAccessMode": "3",
			"version": "android_v5.0.3",
			"handphone": "00000000000"}
	url = "http://clientnew.wostore.cn:6106/appstore_agent/unistore/servicedata.do?serviceid=commentsList&productIndex=%s&pageNum=1&count=20" % product_id
	try:
		r = requests.get(url, timeout=10, headers=headers)
		if r.status_code == 200:
			j = r.json()
			if j is not None:
				return j.get('totalCount', u'')
	except Exception, e:
		mylogger.error("get wostore comment %s" % traceback.format_exc())
	return u''

def get_wostore_detail():
	count = 0
	mylogger.info("get wostore app detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==31):
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			try:
				headers = {"phoneAccessMode": "3",
						"mac" : "50:a7:2b:33:57:56",
						"version": "android_v4.2.1",
						"Androidversion": "android4.4.2",
						"companylogo": "10269",
						"settertype": "3",
						"handphone": "00000000000"}
				url = "http://clientnew.wostore.cn:6106/appstore_agent/unistore/servicedata.do?serviceid=productDetail&productIndex=%s&resource=null&referer=null" % ret.game_id
				r = requests.get(url, timeout=10, headers=headers)
				if r.status_code == 200 and r.text:
					g = r.json() 
					if g is not None:
						count += 1 
						#for k, v in g.iteritems():
						#	print k, v
						item = GameDetailByDay(**{
									'kc_id': ret.id,
									'summary' : g.get('desc', u''),
									'rating' : g.get('rate', u''),
									'version' : g.get('versionName', u''),
									'author' : g.get('supplier', u''),
									'pkg_size' : g.get('size', u''),
									'comment_num' : get_wostroe_comment_by_product_id(ret.game_id),
									'download_num' : g.get('downloadCount', u''),
									'dt' : dt,
									'imgs' : g.get('screenshots1', u''),
										})
						db_conn.merge(item)
			except Exception,e:
				mylogger.error("wostore app detail #### #### \t%s" % (traceback.format_exc()))
	mylogger.info("get wostore app detail %s" % count)
	db_conn.commit()

def get_mmstore_detail():
	count = 0
	error_times = 0
	mylogger.info("get mmstore app detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==32):
		if error_times >= 10:
			mylogger.info("mmstore reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			try:
				headers = {
					"appname": "MM5.3.0.001.01_CTAndroid_JT", 
					"ua":"android-19-720x1280-CHE2-UL00"}
				response = requests.get(ret.url, timeout=20, headers=headers)
				if response.status_code == 200:
					j = response.json() 
					if j is not None:
						g = j
						count += 1 
						item = GameDetailByDay(**{
									'kc_id': ret.id,
									'summary' : g.get('description', u''),
									'rating' : g.get('grade', u''),
									'version' : g.get('versionName', u''),
									'game_type' : g.get('category', u''),
									'pkg_size' : g.get('appSize', u''),
									'author' : g.get('provider', u''),
									'download_num' : g.get('interested', u''),
									'comment_num' : get_mmstore_comments_by_id(g.get('contentId', 0)),
									'dt' : dt,
									'imgs' : u",".join(g.get('previews', []))
										})
						db_conn.merge(item)
			except Exception,e:
				error_times += 1
				mylogger.error("mmstore app detail ### #### \t%s" % (traceback.format_exc()))
	mylogger.info("get mmstore app detail %s" % count)
	db_conn.commit()

def get_mmstore_comments_by_id(contentid):
	url = "http://odp.mmarket.com/t.do?requestid=query_comment_cs&contentid=%s" % contentid
	try:
		headers = {
			"appname": "MM5.3.0.001.01_CTAndroid_JT", 
			"ua":"android-19-720x1280-CHE2-UL00"}
		response = requests.get(url, timeout=20, headers=headers)
		if response.status_code == 200:
			j = response.json() 
			if j['pageInfo'] is not None:
				return j['pageInfo'].get('totalRows', u'')
	except Exception,e:
		mylogger.error("mmstore comments ### #### \t%s" % (traceback.format_exc()))
	return u''

def get_vivo_store_detail():
	count = 0
	error_times = 0
	mylogger.info("get vivo_store app detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==33):
		if error_times >= 10:
			mylogger.info("vivo_store reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			try:
				prefix = "http://info.appstore.vivo.com.cn/port/package/?source=1&e=150100523832314d4200cf98e451625f&elapsedtime=2563957798&content_complete=1&screensize=1080_1920&density=3.0&pictype=webp&cs=0&av=22&an=5.1&app_version=612&imei=867570026068423&nt=WIFI&module_id=219&target=local&cfrom=103&need_comment=0&model=m2+note&s=2%7C0"
				url = prefix + "&id=%s" % ret.game_id
				response = requests.get(url, timeout=20)
				if response.status_code == 200:
					j = response.json() 
					if j['value'] is not None:
						g = j['value']
						count += 1 
						item = GameDetailByDay(**{
									'kc_id': ret.id,
									'summary' : g.get('introduction', u''),
									'rating' : g.get('score', u''),
									'version' : g.get('version_name', u''),
									'pkg_size' : g.get('size', u''),
									'author' : g.get('developer', u''),
									'download_num' : g.get('download_count', u''),
									'comment_num' : g.get('raters_count', u''),
									'dt' : dt,
									'imgs' : u",".join(g.get('screenshotList', []))
										})
						db_conn.merge(item)
			except Exception,e:
				error_times += 1
				mylogger.error("vivo_store app detail ### #### \t%s" % (traceback.format_exc()))
	mylogger.info("get vivo_store app detail %s" % count)
	db_conn.commit()

def step1():
	get_xiaomi_new_detail()
	get_xiaomi_rpg_detail()
	get_open_play_detail()
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
	get_meizu_detail()
	get_9game_detail()

def step2():
	get_wandoujia_detail()
	get_youku_detail()
	get_360zhushou_app_detail()
	get_i4_app_detail()
	get_xyzs_app_detail()
	get_91play_detail()
	get_360_gamebox_detail()
	get_lenovo_shop_detail()
	get_wostore_detail()
	get_mmstore_detail()
	get_vivo_store_detail()
	get_huawei_detail()
	get_kuaiyong_detail()

if __name__ == '__main__':
	step1()

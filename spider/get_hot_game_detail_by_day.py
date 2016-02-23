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
import md5

db_conn = new_session()
mylogger = get_logger('get_hot_game_detail')

class T:
	
	def __init__(self, status_code):
		self.status_code = status_code

class EX:
	
	msg = ""


def get_urls_from_db_by_ids(ids):
	_sql = "select identifying from hot_games where identifying!='\t' and identifying!='' and dt!='' and source in (%s) group by identifying" % ",".join([str(i) for i in ids])
	mylogger.info(_sql)
	return [rt[0] for rt in db_conn.execute(_sql)]

def get_9game_detail(channel_id):
	mylogger.info("get 9game detail start ...")
	count = 0
	error_times = 0
	sess = requests.session()
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 10:
			mylogger.info("9game reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				p = proxies[random.randrange(len(proxies))]
				response = sess.get(url, timeout=15, proxies=p)
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

					item = HotGameDetailByDay(**{'channel': channel_id,
													'dt' : dt,
													'identifying' : url,
													'imgs' : imgs,
													'summary' : summary,
													'game_type' : game_type,
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
				mylogger.error("%s\t%s" % (url.encode('utf-8'), traceback.format_exc()))

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


def get_18183_detail(channel_id):
	mylogger.info("get 18183 detail start ...")
	count = 0 
	error_times = 0
	sess = requests.session()
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 10:
			mylogger.info("18183 reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				p = proxies[random.randrange(len(proxies))]
				response = sess.get(url, timeout=10, proxies=p)
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
				item = HotGameDetailByDay(**{'channel': channel_id,
												'identifying' : url,
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
				mylogger.error("%s\t%s" % (url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get 18183 detail %s" % count)
	db_conn.commit()


def get_appicsh_detail(channel_id):
	mylogger.info("get appicsh detail start ...")
	count = 0
	error_times = 0
	sess = requests.session()
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 10:
			mylogger.info("appicsh reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				r = sess.get(url, timeout=10)
				if r.status_code == 200:
					d = r.json()
					if d['obj'] is not None and d['obj']['appInfo'] is not None:
						appinfo = d['obj']['appInfo']
						count += 1
						publishtime = appinfo.get('apkPublishTime', u"")
						update_time = unicode(datetime.date.fromtimestamp(publishtime)) if publishtime else u""

						item = HotGameDetailByDay(**{'identifying': url,
													'channel' : channel_id,
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
						if count % 100 == 0:
							db_conn.commit()
			except Exception,e:
				error_times += 1
				mylogger.error("get appicsh detail %s\t%s" % (url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get appicsh detail %s" % count)
	db_conn.commit()
			

def get_xiaomi_game_detail(channel_id):
	count = 0
	xiaomi_app_map = get_xiaomi_app_list()
	mylogger.info("get xiaomi_game rank detail start ...")
	ids = channel_map.get(channel_id)
	for pkg_name in get_urls_from_db_by_ids(ids):
		if pkg_name in xiaomi_app_map:
			dt = unicode(datetime.date.today())
			ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==pkg_name).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
			if not ins:
				g = xiaomi_app_map.get(pkg_name)
				if g is not None:
					count += 1
					item = HotGameDetailByDay(**{
												'channel': channel_id,
												'identifying': pkg_name,
												'summary' : g.get('introduction', u''),
												'author' : g.get('publisherName', u''),
												'game_type' : g.get('className', u''),
												'version' : g.get('versionName', u''),
												'rating' : g.get('ratingScore', u''),
												'download_num' : g.get('downloadCount', u''),
												'pkg_size' : g.get('apkSize' u''),
												'dt' : dt,
												'imgs' : u','.join([i.get('url') for i in g['screenShot']]),
												'topic_num_total' : g.get('ratingCount', u''),
													})
					db_conn.merge(item)
	mylogger.info("get xiaomi game  detail %s" % count)
	db_conn.commit()


def get_xiaomi_app_list():
	mydict = {}
	xiaomi_app_download = "http://app.migc.xiaomi.com/cms/interface/v5/rankgamelist1.php?uid=20150905_132380697&platform=android&os=V6.7.1.0.KXDCNCH&stampTime=1449557687000&density=480&imei=865931027730878&pageSize=50&versionCode=1822&cid=gamecenter_100_1_android%7C865931027730878&clientId=40b53f3e316bda9f83c2e0c094d5b7f6&vn=MIGAMEAPPSTAND_1.8.22&co=CN&page=1&macWifi=3480B34D6987&la=zh&ua=Xiaomi%257CMI%2B4LTE%257C4.4.4%257CKTU84P%257C19%257Ccancro&carrier=unicom&rankId=17&mnc=46001&fuid=&mid=&imsi=460015776509846&sdk=19&mac3g=&bid=701"
	xiaomi_app_hot = "http://app.migc.xiaomi.com/cms/interface/v5/rankgamelist1.php?uid=20150905_132380697&platform=android&os=V6.7.1.0.KXDCNCH&stampTime=1449557980000&density=480&imei=865931027730878&pageSize=50&versionCode=1822&cid=gamecenter_100_1_android%7C865931027730878&clientId=40b53f3e316bda9f83c2e0c094d5b7f6&vn=MIGAMEAPPSTAND_1.8.22&co=CN&page=1&macWifi=3480B34D6987&la=zh&ua=Xiaomi%257CMI%2B4LTE%257C4.4.4%257CKTU84P%257C19%257Ccancro&carrier=unicom&rankId=18&mnc=46001&fuid=&mid=&imsi=460015776509846&sdk=19&mac3g=&bid=701"
	try:
		for url  in [xiaomi_app_download, xiaomi_app_hot]:
			r = requests.get(url)
			if r.status_code == 200:
				j = r.json()
				for game in j['gameList']:
					packageName = game.get('packageName', u'')
					if packageName:
						mydict[packageName] = game
	except Exception,e:
		mylogger.error("get xiaomi app list\t%s" % (traceback.format_exc()))
	return mydict

							

def get_open_play_detail(channel_id):
	count = 0
	error_times = 0
	sess = requests.session()
	mylogger.info("get open play detail start ...")
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("open play detail reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				response = sess.get(url, timeout=10)
				if response.status_code == 200:
					d = response.json()
					if d.get('text', u'') == u'success':
						count += 1 
						g = d['ext']['game_detail']
						topic_num_total = u''
						ref_vote_info = d['ext']['ref_vote_info']
						if ref_vote_info['vote_state'] == 1:
							topic_num_total = ref_vote_info['vote_up_count'] + ref_vote_info['vote_dn_count']
						item = HotGameDetailByDay(**{
													'channel': channel_id,
													'identifying': url,
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
				mylogger.error("%s\t%s" % (url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get open play detail %s" % count)
	db_conn.commit()

def get_vivo_detail(channel_id):
	count = 0
	error_times = 0
	sess = requests.session()
	mylogger.info("get vivo detail start ...")
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 10:
			mylogger.info("vivo reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				r = sess.get(url, timeout=10)
				if r.status_code == 200:
					d = r.json()
					if d is not None and 'result' in d and d['result']:
						g = d.get('game')
						if g is not None:
							count += 1 
							item = HotGameDetailByDay(**{
													'channel': channel_id,
													'identifying': url,
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
						if count % 50 == 0:
							sleep(3)
							mylogger.info("vivo detail commit %s" % count)
							db_conn.commit()
			except Exception,e:
				error_times += 1
				mylogger.error("%s\t%s" % (url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get vivo play detail %s" % count)
	db_conn.commit()


def get_coolpad_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get coolpad detail start ...")
	ids = channel_map.get(channel_id)
	for pkg_id in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("coolpad reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==pkg_id).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			g =  get_coolpad_detail_by_id(pkg_id)
			if isinstance(g, EX):
				error_times += 1
			elif g is not None:
				count += 1 
				imgs = u''
				if g['pics'] is not None and g['pics']['picurl'] is not None:
					imgs =  u','.join([i for i in g['pics']['picurl'] if i is not None])
				item = HotGameDetailByDay(**{
											'identifying': pkg_id,
											'channel': channel_id,
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

def get_gionee_detail(channel_id):
	count = 0
	error_times = 0
	sess = requests.session()
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("gionee reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				r = sess.get(url, timeout=10)
				if r.status_code == 200:
					d = r.json()
					if d['success']:
						g = d['data']
						count += 1 
						item = HotGameDetailByDay(**{
													'identifying': url,
													'channel': channel_id,
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
				mylogger.error("%s\t%s" % (url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get gionee play detail %s" % count)
	db_conn.commit()



def get_leveno_detail(channel_id):
	count = 0
	error_times = 0
	sess = requests.session()
	mylogger.info("get lenovo detail start ...")
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("leveno reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				p = proxies[random.randrange(len(proxies))]
				r = sess.get(url, timeout=10, proxies=p)
				if r.status_code == 200:
					d = r.json()
					if 'app' in d:
						g = d['app']
						count += 1 
						item = HotGameDetailByDay(**{
													'identifying': url,
													'channel': channel_id,
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
				mylogger.error("get %s lenovo detail \t%s" % (url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get lenovo detail %s" % count)
	db_conn.commit()


def get_iqiyi_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get iqiyi detail start ...")
	ids = channel_map.get(channel_id)
	for qipu_id in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("iqiyi reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==qipu_id).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			d =  get_iqiyi_detail_by_id(qipu_id)
			if isinstance(d, EX):
				error_times += 1
			elif d is not None:
				g = d['app']
				count += 1 
				item = HotGameDetailByDay(**{
											'channel': channel_id,
											'identifying': qipu_id,
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

def get_sogou_detail(channel_id):
	count = 0
	error_times = 0
	sess = requests.session()
	mylogger.info("get sogou detail start ...")
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("sogou reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				r = sess.get(url, timeout=10)
				if r.status_code == 200:
					d = r.json()
					g = d['ainfo']
					count += 1 
					item = HotGameDetailByDay(**{
												'identifying': url,
												'channel': channel_id,
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
			except Exception,e:
				#error_times += 1
				mylogger.error("%s\t%s" % (url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get sogou detail %s" % count)
	db_conn.commit()


def get_dangle_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get dangle detail start ...")
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("dangle reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			resourceType, gid = url.split('\t')
			g =  get_dangle_detail_by_id(resourceType, gid)
			if isinstance(g, EX):
				error_times += 1
			elif g is not None:
				count += 1 
				packageTOs = {}
				if 'packageTOs' in g:
					packageTOs = g['packageTOs'][0] if g['packageTOs'] else {}
					item = HotGameDetailByDay(**{
												'channel': channel_id,
												'identifying': url,
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


def get_dangle_detail_by_id(resourceType, gid):
	payload = {'id': gid, 'resourceType': resourceType}
	url = "http://api2014.digua.d.cn/newdiguaserver/res/detail"
	#url = "http://api2014.digua.d.cn/newdiguaserver/res/detail?id=%s&resourceType=5"% gid
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
		r = requests.post(url, data=payload, headers=headers, timeout=20)
		if r.status_code == 200:
			d = r.json()
			return d
	except Exception,e:
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
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
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.kc_id==ret.id).filter(HotGameDetailByDay.dt==dt).first()
		if not ins:
			g = get_muzhiwan_detail_by_id(ret.url)
			if g:
				#m = re.search(u'(\d+)个', g.get(u'评论数', u''))
				#comment_num = m.group(1) if m is not None else u''
				count += 1 
				item = HotGameDetailByDay(**{
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
			if 'ex_msg' in g:
				error_times += 1
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
		mydict = {'ex_msg': u'Exception'}
		mylogger.error("get muzhiwan detail \t%s" % (traceback.format_exc()))
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
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.kc_id==ret.id).filter(HotGameDetailByDay.dt==dt).first()
		if not ins:
			g = get_huawei_detail_by_id(ret.url)
			if 'ex_msg' in g:
				error_times += 1
			if g:
				count += 1 
				item = HotGameDetailByDay(**{
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
		mydict = {'ex_msg': u'Exception'}
		mylogger.error("%s\t%s" % (url, traceback.format_exc()))
		sleep(5)
	return mydict

def get_kuaiyong_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get kuaiyong detail start ...")
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("kuaiyong reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			g = get_kuaiyong_detail_by_id(url)
			if isinstance(g, EX):
				error_times += 1
			elif g:
				count += 1 
				item = HotGameDetailByDay(**{
											'channel': channel_id,
											'identifying': url,
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
		response = requests.get(URL, timeout=20)
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
		sleep(1.21)
		mylogger.error("get kuaiyong detail\t%s" % (traceback.format_exc()))
		return EX()
	return mydict


def get_anzhi_detail():
	count = 0
	mylogger.info("get kuaiyong detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.url!=u'').filter(KC_LIST.source==19):
		count += 1 
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.kc_id==ret.id).filter(HotGameDetailByDay.dt==dt).first()
		if not ins:
			g = get_anzhi_detail_by_id(ret.url)
			if g:
				dt = unicode(datetime.date.today())
			item = HotGameDetailByDay(**{
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

def get_wandoujia_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get wandoujia detail start ...")
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("wandoujia reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				r = requests.get(url, timeout=10)
				if r.status_code == 200:
					d = r.json()
					if d['entity'] is not None and len(d['entity'])>=1:
						g = d['entity'][0]['detail']['appDetail']
						count += 1 
						categories = g.get('categories', [])
						game_type = u",".join([c['name'] for c in categories if c['level']==2])
						apk = {}
						apk_list = g.get('apk', [])
						if len(apk_list) >= 1:
							apk = apk_list[0]
						developer = g.get('developer', {})
						item = HotGameDetailByDay(**{
													'identifying': url,
													'channel': channel_id,
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
			except Exception,e:
				error_times += 1
				mylogger.error("### %s ### %s" % (url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get wandoujia detail %s" % count)
	db_conn.commit()



def get_meizu_detail_by_id(url):
	try:
		response = requests.get(url, timeout=20)
		if response.status_code == 200:
			j = response.json()
			if 'value' in j:
				return j['value']
	except Exception,e:
		mylogger.error("get meizu detial \t%s" % (traceback.format_exc()))
		return EX()
	return None


def get_meizu_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get meizu detail start ...")
	sess = requests.session()
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("meizu reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			g = get_meizu_detail_by_id(url)
			if isinstance(g, EX):
				error_times += 1
			elif g is not None:	
				count += 1 
				item = HotGameDetailByDay(**{
									'identifying': url,
									'channel': channel_id,
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
	URL = "http://api.gamex.mobile.youku.com/v2/app/detail?product_id=1&app_id=%s" % app_id
	try:
		response = requests.get(URL, timeout=10)
		if response.status_code == 200:
			j = response.json()
			return j['app']
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		return EX()
	return None

def get_youku_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get youku detail start ...")
	ids = channel_map.get(channel_id)
	for pkg_id in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("youku reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==pkg_id).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			g = get_youku_detail_by_id(pkg_id)
			if isinstance(g, EX):
				error_times += 1
			elif g is not None:	
				count += 1 
				item = HotGameDetailByDay(**{
									'channel': channel_id,
									'identifying': pkg_id,
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

def get_360_app_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get 360 app hot game detail start ...")
	ids = channel_map.get(channel_id)
	for pkg in get_urls_from_db_by_ids(ids):
		if error_times >= 10:
			mylogger.info("360 reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==pkg).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				pkg_name, pkg_id = pkg.split('\t')
				url = "http://125.88.193.234/mintf/getAppInfoByIds?pname=%s" % pkg_name
				r = requests.get(url, timeout=10)
				if r.status_code == 200:
					j = r.json()
					if j['data'] is not None and len(j['data'])>=1:
						g = j['data'][0]
						count += 1 
						comments_url = "http://comment.mobilem.360.cn/comment/getCommentTags?objid=%s" % pkg_id
						comments_num = u''
						try:
							get_comments_r = requests.get(comments_url)
							if get_comments_r.status_code == 200:
								comments_j = get_comments_r.json()
								for tag in comments_j['data']['tag']:
									if tag.get('title', u'') == u'全部':
										comments_num = tag.get('num', u'')
						except Exception,e :
							mylogger.error("360 app comments #### %s #### \t%s" % (comments_url, traceback.format_exc()))
						item = HotGameDetailByDay(**{
									'identifying': pkg,
									'summary' : g.get('brief', u''),
									'version' : g.get('version_name', u''),
									'game_type' : g.get('category_name', u''),
									'pkg_size' : g.get('size', u''),
									'rating' : g.get('rating', u''),
									'author' : g.get('corp', u''),
									'comment_num' : comments_num,
									'download_num' : g.get('download_times', u''),
									'dt' : dt,
									'channel' : channel_id,
									'imgs' : u','.join(g.get('trumb', u'').split(u'|')),
										})
						db_conn.merge(item)
						if count % 50 == 0:
							db_conn.commit()
			except Exception,e:
				error_times += 1
				mylogger.error("360 app detail #### %s #### \t%s" % (pkg.encode('utf-8'), traceback.format_exc()))
				
	mylogger.info("get 360 app detail %s" % count)
	db_conn.commit()


def get_i4_app_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get i4 app detail start ...")
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("i4 reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				r = requests.get(url, timeout=10)
				if r.status_code == 200:
					j = r.json()
					if j['result']['list'] is not None and len(j['result']['list']) >= 1:
						g = j['result']['list'][0]
						count += 1 
						item = HotGameDetailByDay(**{
									'channel': channel_id,
									'identifying': url,
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
				mylogger.error("i4 app detail #### #### \t%s" % (traceback.format_exc()))
	mylogger.info("get i4 app detail %s" % count)
	db_conn.commit()


def get_xyzs_app_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get xyzs app detail start ...")
	ids = channel_map.get(channel_id)
	for itunesid in get_urls_from_db_by_ids(ids):
		if error_times >= 10:
			mylogger.info("xyzs reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==itunesid).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				url = "http://interface.xyzs.com/v2/ios/c01/app"
				d = {'itunesid': int(itunesid)}
				r = requests.get(url, params=d, timeout=10)
				if r.status_code == 200:
					j = r.json()
					if j['code'] == 200:
						g = j['data']['app']
						count += 1 
						item = HotGameDetailByDay(**{
									'identifying': itunesid,
									'channel': channel_id,
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
				mylogger.error("xyzs app detail ####  #### \t%s" % (traceback.format_exc()))
	mylogger.info("get xyzs app detail %s" % count)
	db_conn.commit()


def get_91play_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get 91play app detail start ...")
	ids = channel_map.get(channel_id)
	for pkg_id in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("91play reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==pkg_id).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				url = "http://play.91.com/api.php/Api/index"
				raw_data = {"id": int(pkg_id),"firmware":"19","time":1449458211590,"device":1,"action":30005,"app_version":302,"action_version":4,"mac":"7b715ce093480b34d6987","debug":0}
				response = requests.post(url, data=raw_data, timeout=10)
				if response.status_code == 200:
					j = response.json() 
					if j['code']==0 and j['data'] is not None and json.loads(j['data']) !=u'没有更多数据了':
						g = json.loads(j['data'])
						#break
						count += 1 
						item = HotGameDetailByDay(**{
									'identifying': pkg_id,
									'channel': channel_id,
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
				mylogger.error("91play app detail #### %s #### \t%s" % (url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get 91play app detail %s" % count)
	db_conn.commit()

def get_360_gamebox_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get 360_gamebox app detail start ...")
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 10:
			mylogger.info("360 gamebox reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				response = requests.get(url, timeout=10)
				if response.status_code == 200:
					j = response.json() 
					if j['data'] is not None and j['data']['info'] is not None and j['data']['info']:
						g = j['data']['info']
						count += 1 
						item = HotGameDetailByDay(**{
									'channel': channel_id,
									'identifying': url,
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
				mylogger.error("360_gamebox app detail #### %s #### \t%s" % (url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get 360_gamebox app detail %s" % count)
	db_conn.commit()

def get_m_baidu_detail(channel_id):
	count = 0
	error_times = 0
	sess = requests.session()
	mylogger.info("get baidu zhushou app detail start ...")
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("baidu zhoushou app detail reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				r = sess.get(url, timeout=10)
				if r.status_code == 200:
					d = r.json()
					if d['error_no'] == 0:
						if d['result'] is not None and d['result']['data'] is not None:
							g = d['result']['data']
							count +=1
							item = HotGameDetailByDay(**{
										'channel': channel_id,
										'identifying': url,
										'summary' : g.get('brief', u''),
										'rating' : g.get('display_score', u''),
										'version' : g.get('versionname', u''),
										'game_type' : g.get('catename', u''),
										'pkg_size' : g.get('packagesize', u''),
										'author' : g.get('sourcename', u''),
										'download_num' : g.get('all_download_pid', u''),
										'download_num_day' : g.get('today_download_pid', u''),
										'comment_num' : g.get('display_count', u''),
										'dt' : dt,
										'imgs' : u",".join(g.get('screenshots', []))
											})
							db_conn.merge(item)
							if count % 50:
								db_conn.commit()
			except Exception,e:
				error_times += 1
				mylogger.error("%s\t%s" % (url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get baidu zhushou app detail %s" % count)
	db_conn.commit()

def get_pp_detail_by_id(gid):
	try:
		d = {"site":1, "id": gid}
		p = proxies[random.randrange(len(proxies))]
		r = requests.post('http://pppc2.25pp.com/pp_api/ios_appdetail.php', data=d, proxies=p)
		return r.json()
	except Exception,e:
		mylogger.error("get %s detail \t%s" % (gid.encode('utf-8'), traceback.format_exc()))
		return EX()
	return None

def get_pp_comments_by_id(gid):
	try:
		d = {"s":1, "a":101, "i": gid, "p":1, "l":1}
		p = proxies[random.randrange(len(proxies))]
		r = requests.post('http://pppc2.25pp.com/pp_api/comment.php', data=d, proxies=p)
		if r.status_code == 200:
			return r.json()
	except Exception,e:
		mylogger.error("get %s comments \t%s" % (gid.encode('utf-8'), traceback.format_exc()))
	return {}

def get_pp_detail(channel_id):
	count = 0
	error_times = 0
	sess = requests.session()
	mylogger.info("get pp detail start ...")
	ids = channel_map.get(channel_id)
	for pkg_id in get_urls_from_db_by_ids(ids):
		if error_times >= 10:
			mylogger.info("pp detail reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==pkg_id).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			g = get_pp_detail_by_id(int(pkg_id))
			if isinstance(g, EX):
				error_times += 1
			elif g is not None:	
				if g.get('ipadImgs', u''):
					imgs = g.get('ipadImgs')
				else:
					imgs = g.get('iphoneImgs', u'')
				comments_info = get_pp_comments_by_id(int(pkg_id))
				count += 1 
				item = HotGameDetailByDay(**{
											'identifying': pkg_id,
											'channel': channel_id,
											'summary' : g.get('content', u''),
											'version' : g.get('ver', u''),
											'game_type' : g.get('catName', u''),
											'pkg_size' : g.get('fileSize', u''),
											'comment_num' : comments_info.get('commentCount', u''),
											'download_num' : g.get('downCount', u''),
											'topic_num_total' : g.get('collectCount', u''),
											'rating' : g.get('allVerStar', u''),
											'dt' : dt,
											'imgs' : imgs,
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


def get_lenovo_shop_detail(channel_id):
	count = 0
	error_times = 0
	sess = requests.session()
	mylogger.info("get lenovo_shop app detail start ...")
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("lenovo_shop reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				headers = {"clientid": "141623-2-2-19-1-3-1_480_i865931027730878t19700201770903586_c20524d1p1"}
				response = requests.get(url, timeout=20, headers=headers)
				m = re.search(u'pn=(\w+\S+)&vc', url)
				pkg_name = m.group(1) if m is not None else u''
				if response.status_code == 200:
					j = response.json() 
					if j['appInfo'] is not None:
						g = j['appInfo']
						count += 1 
						item = HotGameDetailByDay(**{
									'identifying': url,
									'channel': channel_id,
									'summary' : g.get('description', u''),
									'rating' : g.get('averageStar', u''),
									'version' : g.get('version', u''),
									'game_type' : g.get('typeName', u''),
									'pkg_size' : g.get('size', u''),
									'comment_num' : get_lenovo_shop_comment_by_pkg(pkg_name),
									'author' : g.get('developerName', u''),
									'download_num' : g.get('realDownCount', u''),
									'dt' : dt,
									'imgs' : u",".join([img.get('APPIMG_PATH', u'') for img in g.get('snapList', [])])
										})
						db_conn.merge(item)
			except Exception,e:
				error_times += 1
				mylogger.error("lenovo_shop app detail #### %s #### \t%s" % (url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get lenovo_shop app detail %s" % count)
	db_conn.commit()

def get_lenovo_shop_comment_by_pkg(pkg_name):
	if pkg_name:
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

def get_wogame_detail(channel_id):
	count = 0
	error_times = 0
	sess = requests.session()
	mylogger.info("get wogame detail start ...")
	ids = channel_map.get(channel_id)
	for pkg_id in get_urls_from_db_by_ids(ids):
		if error_times >= 10:
			mylogger.info("wogame detail reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==pkg_id).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				_d = {"product_id": pkg_id}
				jsondata = {"jsondata": json.dumps(_d)}
				r = requests.get("http://wogame4.wostore.cn/wogame/gameDetail.do", timeout=10, params=jsondata)
				if r.status_code == 200:
					count += 1 
					j = r.json()
					if j['data'] is not None:
						g = j['data']
						item = HotGameDetailByDay(**{
													'identifying': pkg_id,
													'channel': channel_id,
													'summary' : g.get('description', u''),
													'version' : g.get('version_code', u''),
													'game_type' : ",".join([i.get('name', u'') for i in g.get('categories', [])]),
													'pkg_size' : g.get('apk_size', u''),
													'download_num' : g.get('download_count', u''),
													'author' : g.get('sp_name', u''),
													'dt' : dt,
													'imgs' : ",".join(g.get('pics', [])),
														})
						db_conn.merge(item)
						if count % 50 == 0:
							mylogger.info("wogame detail commit %s" % count)
							db_conn.commit()
			except Exception,e:
				mylogger.error("get wogame detail %s \t%s" % (pkg_id.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get wogame detail %s" % count)
	db_conn.commit()

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

def get_wostore_download_count_by_id(game_id, dt):
	ins = db_conn.query(HotGames).filter(HotGames.source.in_((77,78))).filter(HotGames.identifying==game_id).filter(HotGames.dt==dt).first()
	if ins is not None:
		return ins.download_count
	return u''

def get_wostore_detail(channel_id):
	count = 0
	error_times = 0
	sess = requests.session()
	mylogger.info("get wostore detail start ...")
	ids = channel_map.get(channel_id)
	for pkg_id in get_urls_from_db_by_ids(ids):
		dt = unicode(datetime.date.today())
		try:
			ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==pkg_id).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
			if not ins:
				headers = {"phoneAccessMode": "3",
						"mac" : "50:a7:2b:33:57:56",
						"version": "android_v4.2.1",
						"Androidversion": "android4.4.2",
						"companylogo": "10269",
						"settertype": "3",
						"handphone": "00000000000"}
				p = proxies[random.randrange(len(proxies))]
				url = "http://clientnew.wostore.cn:6106/appstore_agent/unistore/servicedata.do?serviceid=productDetail&productIndex=%s&resource=null&referer=null" % pkg_id
				r = requests.get(url, timeout=40, headers=headers)
				if r.status_code == 200 and r.text:
					g = r.json() 
					if g is not None:
						count += 1 
						item = HotGameDetailByDay(**{
									'identifying': pkg_id,
									'channel': channel_id,
									'summary' : g.get('desc', u''),
									'rating' : g.get('rate', u''),
									'version' : g.get('versionName', u''),
									'author' : g.get('supplier', u''),
									'pkg_size' : g.get('size', u''),
									'comment_num' : get_wostroe_comment_by_product_id(pkg_id),
									'download_num' : get_wostore_download_count_by_id(pkg_id, dt),
									'dt' : dt,
									'imgs' : g.get('screenshots1', u''),
										})
						db_conn.merge(item)
			else:
				ins.download_num = get_wostore_download_count_by_id(pkg_id, dt)
		except Exception,e:
			mylogger.error("wostore app detail #### %s #### \t%s" % (pkg_id.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get wostore app detail %s" % count)
	db_conn.commit()


def get_mmstore_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get mmstore app detail start ...")
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 10:
			mylogger.info("mmstore reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).first()
		if not ins:
			try:
				headers = {
					"appname": "MM5.3.0.001.01_CTAndroid_JT", 
					"ua":"android-19-720x1280-CHE2-UL00"}
				response = requests.get(url, timeout=20, headers=headers)
				if response.status_code == 200:
					g = response.json() 
					if g is not None:
						count += 1 
						item = HotGameDetailByDay(**{
									'identifying': url,
									'channel':	channel_id,
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

def get_vivo_store_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get vivo_store app detail start ...")
	ids = channel_map.get(channel_id)
	for game_id in get_urls_from_db_by_ids(ids):
		if error_times >= 10:
			mylogger.info("vivo_store reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==game_id).filter(HotGameDetailByDay.dt==dt).first()
		if not ins:
			try:
				prefix = "http://info.appstore.vivo.com.cn/port/package/?source=1&e=150100523832314d4200cf98e451625f&elapsedtime=2563957798&content_complete=1&screensize=1080_1920&density=3.0&pictype=webp&cs=0&av=22&an=5.1&app_version=612&imei=867570026068423&nt=WIFI&module_id=219&target=local&cfrom=103&need_comment=0&model=m2+note&s=2%7C0"
				url = prefix + "&id=%s" % game_id
				response = requests.get(url, timeout=20)
				if response.status_code == 200:
					j = response.json() 
					if j['value'] is not None:
						g = j['value']
						count += 1 
						item = HotGameDetailByDay(**{
									'channel': channel_id,
									'identifying': game_id,
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

def get_myaora_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get myaora app detail start ...")
	ids = channel_map.get(channel_id)
	for game_id in get_urls_from_db_by_ids(ids):
		if error_times >= 10:
			mylogger.info("myaora reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==game_id).filter(HotGameDetailByDay.dt==dt).first()
		if not ins:
			try:
				payload = {"TAG":"INTRODUCTION_CATEGORY","API_VERSION":9,"MARKET_IMEI":"867570026068423","MARKET_KEY":"5bed9c59b8d64b24d35eedf7b8065115","ID": game_id}
				response = requests.post("http://adres.myaora.net:81/api.php", timeout=20, data=json.dumps(payload))
				if response.status_code == 200:
					g = response.json() 
					if g is not None:
						count += 1 
						item = HotGameDetailByDay(**{
									'channel': channel_id,
									'identifying': game_id,
									'summary' : g.get('DESCRIBE', u''),
									'rating' : g.get('ALL_START', {}).get('average', u''),
									'game_type' : g.get('CATALOG_NAME', u''),
									'version' : g.get('VERSION', u''),
									'pkg_size' : g.get('SIZE', u''),
									'author' : g.get('DEVELOPER', u''),
									'download_num' : g.get('DOWNLOAD_REGION', u''),
									'comment_num' : g.get('COMMENT_COUNT', u''),
									'dt' : dt,
									'imgs' : u",".join(g.get('ALL_SCREENSHOT_URLS', []))
										})
						db_conn.merge(item)
			except Exception,e:
				error_times += 1
				mylogger.error("myaora app detail ### #### \t%s" % (traceback.format_exc()))
	mylogger.info("get myaora app detail %s" % count)
	db_conn.commit()

def get_xiaomi_web_game_list():
	mydict = {}
	count = 0
	from get_hot_game import get_xiaomi_game_rank
	type_list = [2,3,12,13]
	for rank_id in type_list:
		for x in range(1,4):
			game_list = get_xiaomi_game_rank(x, rank_id)
			if game_list is not None:
				for g in game_list:
					count += 1
					mydict[g.get("ext_id")] = g
	mylogger.info("get xiaomi web game list %s" % count)
	return mydict

def get_xiaomi_web_page_info(url):
	mydict = {}
	try:
		p = proxies[random.randrange(len(proxies))]
		r = requests.get(url, timeout=15, proxies=p)
		if r.status_code == 200:
			soup = BeautifulSoup(r.text)
			info_star = soup.find('div', class_='info-star')
			if info_star is not None:
				start_rank = info_star.find('div').get('class')
				if len(start_rank) == 2:
					if start_rank[1] == u's10':
						rating = u'5'
					elif start_rank[1] == u's8':
						rating = u'4'
					elif start_rank[1] == u's8':
						rating = u'3'
					elif start_rank[1] == u's8':
						rating = u'2'
					elif start_rank[1] == u's8':
						rating = u'1'
					else:
						rating = u''
					mydict['rating'] = rating
			imgs = soup.find('div', class_='thumbnail-wrap')
			if imgs is not None:
				mydict['imgs'] = ",".join([img.get('src') for img in imgs.find_all('img')])
			appinfo = soup.find('div',class_='appinfo')
			if appinfo is not None:
				mydict['summary'] = appinfo.text 
	except Exception,e:
		mylogger.error("get ## %s ## xiaomi web page info %s" % (url.encode('utf-8'),traceback.format_exc()))
	return mydict
	

def get_xiaomi_web_detail(channel_id):
	count = 0
	error_times = 0
	id2category = get_xiaomi_web_game_list()
	mylogger.info("get xiaomi_web app detail start ...")
	ids = channel_map.get(channel_id)
	for url in get_urls_from_db_by_ids(ids):
		if error_times >= 20:
			mylogger.info("xiaomi_web reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==url).filter(HotGameDetailByDay.dt==dt).first()
		if not ins:
			try:
				game_type = u''
				m =  re.search('(\d+).html', url)
				if m is not None:
					ext_id = m.group(1)
					g = id2category.get(ext_id)
					if g is not None:
						page_info = get_xiaomi_web_page_info(url)
						count += 1 
						item = HotGameDetailByDay(**{
									'channel': channel_id,
									'identifying': url,
									'summary' : page_info.get('summary', u''),
									'rating' : page_info.get('rating', u''),
									'game_type' : g.get('level2_category_name', u''),
									'version' : g.get('version_code', u''),
									'pkg_size' : g.get('apk_size', u''),
									'download_num' : g.get('download_count', u''),
									'dt' : dt,
									'imgs' : page_info.get('imgs', u'')
										})
						db_conn.merge(item)
						if count % 50 == 0:
							mylogger.info("xiaomi web game detail commit %s" % count)
							db_conn.commit()
			except Exception,e:
				error_times += 1
				mylogger.error("xiaomi_web app detail ### #### \t%s" % (traceback.format_exc()))
	mylogger.info("get xiaomi_web app detail %s" % count)
	db_conn.commit()

def get_oppo_hot_game_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get oppo app detail start ...")
	req_headers = {'sign':'', 'param':'imei=868008021943653&model=Che2-UL00&osversion=19'}
	md5_suffix = 'MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBANYFY/UJGSzhIhpx6YM5KJ9yRHc7YeURxzb9tDvJvMfENHlnP3DtVkOIjERbpsSd76fjtZnMWY60TpGLGyrNkvuV40L15JQhHAo9yURpPQoI0eg3SLFmTEI/MUiPRCwfwYf2deqKKlsmMSysYYHX9JiGzQuWiYZaawxprSuiqDGvAgMBAAECgYEAtQ0QV00gGABISljNMy5aeDBBTSBWG2OjxJhxLRbndZM81OsMFysgC7dq+bUS6ke1YrDWgsoFhRxxTtx/2gDYciGp/c/h0Td5pGw7T9W6zo2xWI5oh1WyTnn0Xj17O9CmOk4fFDpJ6bapL+fyDy7gkEUChJ9+p66WSAlsfUhJ2TECQQD5sFWMGE2IiEuz4fIPaDrNSTHeFQQr/ZpZ7VzB2tcG7GyZRx5YORbZmX1jR7l3H4F98MgqCGs88w6FKnCpxDK3AkEA225CphAcfyiH0ShlZxEXBgIYt3V8nQuc/g2KJtiV6eeFkxmOMHbVTPGkARvt5VoPYEjwPTg43oqTDJVtlWagyQJBAOvEeJLno9aHNExvznyD4/pR4hec6qqLNgMyIYMfHCl6d3UodVvC1HO1/nMPl+4GvuRnxuoBtxj/PTe7AlUbYPMCQQDOkf4sVv58tqslO+I6JNyHy3F5RCELtuMUR6rG5x46FLqqwGQbO8ORq+m5IZHTV/Uhr4h6GXNwDQRh1EpVW0gBAkAp/v3tPI1riz6UuG0I6uf5er26yl5evPyPrjrD299L4Qy/1EIunayC7JYcSGlR01+EDYYgwUkec+QgrRC/NstV'

	ids = channel_map.get(channel_id)
	_sql = "select name, url from hot_games where source in (%s) and url!='' group by name, url" % ",".join([str(i) for i in ids])
	mylogger.info(_sql)
	for ret in db_conn.execute(_sql):
		game_name, game_url = ret
		if error_times >= 10:
			mylogger.info("oppo reach max error times ... ")
			break
		dt = unicode(date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==game_url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				game_url_query = game_url.split('?')[-1]
				if game_url_query:
					if isinstance(game_url_query, unicode) :
						game_url_query = game_url_query.encode('utf-8')
					game_url_query = '&' + game_url_query
				
				md5_str = req_headers.get('param') + game_url_query + md5_suffix
				hash = md5.new()
				hash.update(md5_str)
				req_headers['sign'] =  hash.hexdigest()

				response = requests.get(game_url, headers=req_headers, timeout=10)
				if response.status_code == 200:
					json_result = response.json() 
					game_content = json_result['game']
					if game_content is not None :
						count += 1 
						detail_game_name = game_content.get('gameName', u'');
						detail_download_num = game_content.get('gameDownloadNum', u'');
						detail_game_categoryName = game_content.get('categoryName', u'');
						detail_game_size = game_content.get('gameSize', u'');

						detail_game_desc = json_result.get('gameDesc', u'')
						detail_game_ver = json_result.get('gameVerName', u'')
						#detail_game_pic = json_result.get('gamePicture0', u'')
						imgs = []
						for i in xrange(5):
							_key = 'gamePicture%s' %i
							p = json_result.get(_key, u'')
							if p is not None and p:
								imgs.append(p)
						
						#pic_str = []
						#pic_str.append(json_result.get('gamePicture1', u''));
						#pic_str.append(json_result.get('gamePicture2', u''));
						#pic_str.append(json_result.get('gamePicture3', u''));
						#pic_str.append(json_result.get('gamePicture4', u''));						
						#
						#for i in range(len(pic_str)) :
						#	if pic_str[i] is not None :
						#		detail_game_pic += (u',' + pic_str[i])
							
						detail_game_commentNum = json_result.get('commentNum', u'')
						item = HotGameDetailByDay(**{
									'channel': channel_id,
									'identifying': game_url,
									'summary' : detail_game_desc,
									'version' : detail_game_ver,
									'game_type' : detail_game_categoryName,
									'pkg_size' : detail_game_size,
									'download_num' : detail_download_num,
									'comment_num' : detail_game_commentNum,
									'dt' : dt,
									'imgs' : u','.join(imgs),
									'create_date' : dt,
									'last_update' : dt
										})
						db_conn.merge(item)
			except Exception,e:
				error_times += 1
				mylogger.error("oppo app detail #### %s #### \t%s" % (game_url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get oppo app detail %s" % count)
	db_conn.commit()


def get_oppo_hot_game_detail(channel_id):
	count = 0
	error_times = 0
	mylogger.info("get oppo app detail start ...")
	req_headers = {'sign':'', 'param':'imei=868008021943653&model=Che2-UL00&osversion=19'}
	md5_suffix = 'MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBANYFY/UJGSzhIhpx6YM5KJ9yRHc7YeURxzb9tDvJvMfENHlnP3DtVkOIjERbpsSd76fjtZnMWY60TpGLGyrNkvuV40L15JQhHAo9yURpPQoI0eg3SLFmTEI/MUiPRCwfwYf2deqKKlsmMSysYYHX9JiGzQuWiYZaawxprSuiqDGvAgMBAAECgYEAtQ0QV00gGABISljNMy5aeDBBTSBWG2OjxJhxLRbndZM81OsMFysgC7dq+bUS6ke1YrDWgsoFhRxxTtx/2gDYciGp/c/h0Td5pGw7T9W6zo2xWI5oh1WyTnn0Xj17O9CmOk4fFDpJ6bapL+fyDy7gkEUChJ9+p66WSAlsfUhJ2TECQQD5sFWMGE2IiEuz4fIPaDrNSTHeFQQr/ZpZ7VzB2tcG7GyZRx5YORbZmX1jR7l3H4F98MgqCGs88w6FKnCpxDK3AkEA225CphAcfyiH0ShlZxEXBgIYt3V8nQuc/g2KJtiV6eeFkxmOMHbVTPGkARvt5VoPYEjwPTg43oqTDJVtlWagyQJBAOvEeJLno9aHNExvznyD4/pR4hec6qqLNgMyIYMfHCl6d3UodVvC1HO1/nMPl+4GvuRnxuoBtxj/PTe7AlUbYPMCQQDOkf4sVv58tqslO+I6JNyHy3F5RCELtuMUR6rG5x46FLqqwGQbO8ORq+m5IZHTV/Uhr4h6GXNwDQRh1EpVW0gBAkAp/v3tPI1riz6UuG0I6uf5er26yl5evPyPrjrD299L4Qy/1EIunayC7JYcSGlR01+EDYYgwUkec+QgrRC/NstV'

	ids = channel_map.get(channel_id)
	_sql = "select name, url from hot_games where source in (%s) and url!='' group by name, url" % ",".join([str(i) for i in ids])
	mylogger.info(_sql)
	for ret in db_conn.execute(_sql):
		game_name, game_url = ret
		if error_times >= 10:
			mylogger.info("oppo reach max error times ... ")
			break
		dt = unicode(date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.identifying==game_url).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				game_url_query = game_url.split('?')[-1]
				if game_url_query:
					if isinstance(game_url_query, unicode) :
						game_url_query = game_url_query.encode('utf-8')
					game_url_query = '&' + game_url_query
				
				md5_str = req_headers.get('param') + game_url_query + md5_suffix
				hash = md5.new()
				hash.update(md5_str)
				req_headers['sign'] =  hash.hexdigest()

				response = requests.get(game_url, headers=req_headers, timeout=10)
				if response.status_code == 200:
					json_result = response.json() 
					game_content = json_result['game']
					if game_content is not None :
						count += 1 
						detail_game_name = game_content.get('gameName', u'');
						detail_download_num = game_content.get('gameDownloadNum', u'');
						detail_game_categoryName = game_content.get('categoryName', u'');
						detail_game_size = game_content.get('gameSize', u'');

						detail_game_desc = json_result.get('gameDesc', u'')
						detail_game_ver = json_result.get('gameVerName', u'')
						detail_game_pic = json_result.get('gamePicture0', u'')
						imgs = []
						for i in xrange(5):
							_key = 'gamePicture%s' %i
							p = json_result.get(_key, u'')
							if p is not None and p:
								imgs.append(p)
						detail_game_commentNum = json_result.get('commentNum', u'')
						item = HotGameDetailByDay(**{
									'channel': channel_id,
									'identifying': game_url,
									'summary' : detail_game_desc,
									'version' : detail_game_ver,
									'game_type' : detail_game_categoryName,
									'pkg_size' : detail_game_size,
									'download_num' : detail_download_num,
									'comment_num' : detail_game_commentNum,
									'dt' : dt,
									'imgs' : u",".join(imgs),
									'create_date' : dt,
									'last_update' : dt
										})
						db_conn.merge(item)
			except Exception,e:
				error_times += 1
				mylogger.error("oppo app detail #### %s #### \t%s" % (game_url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get oppo app detail %s" % count)
	db_conn.commit()

channel_map = {
			2	: [46, 47], #18183
			4 	: [5, 6, 7, 48], #360助手app
			22	: [2, 52, 53, 54, 55, 56, 57, 58, 59],	#360助手web
			1	: [],	#360游戏大厅web
			28	: [41, 42],	#360游戏大厅app
			0	: [3, 4], #9游web
			20	: [38], #itools
			24	: [36], # pp
			8	: [16, 17, 18],# vivo
			26	: [39], # xyzs
			13	: [31, 32], # youku
			18	: [], # huawei
			21	: [], # anzhi
			6	: [], # 小米游戏app
			5	: [60, 61], #小米游戏app
			3	: [8, 9, 10, 43], # 应用宝PC
			15	: [14, 67], #dangle
			19	: [37], # kuaiyong
			17	: [], #muzhiwan
			14	: [33, 34, 51], #sougou
			12	: [29, 30], # aiqiyi
			16	: [35], # i4
			7	: [24, 25, 26, 45], #爱游戏
			29 	: [11, 12, 13, 44], #百度手机助手app
			11	: [68, 69, 70], # lenovo
			23	: [27, 28], # wandoujia
			9	: [21, 22, 23], # coolpad
			27	: [40], #91play
			10	: [19,20], # 金立
			25	: [75, 76], # meizu
			999	: [1, 15, 49, 50], #小米官方
			998	: [65, 66], # wogame
			30	: [71, 72, 73, 74], # lenovo shop
			31	: [77,78], # wostore
			32	: [79], # mmstore
			33	: [80, 81], # mmstore
			34	: [84, 85, 86, 87], # huawei app
			997	: [82, 83], # 易用汇榜单
			50	: [100, 101, 102], #oppo
			996	: [], #金山手机助手
				}

def main():
	get_18183_detail(2)
	get_360_app_detail(4)
	get_360_gamebox_detail(28)
	get_9game_detail(0)
	get_pp_detail(24)
	get_vivo_detail(8)
	get_xyzs_app_detail(26)
	get_youku_detail(13)
	get_appicsh_detail(3)
	get_dangle_detail(15)
	get_mmstore_detail(32)
	get_vivo_store_detail(33)
	get_myaora_detail(997)
	get_oppo_hot_game_detail(50)
	get_kuaiyong_detail(19)
	get_log_info('get_hot_game_detail.log', subject='榜单详情监控')

def step2():
	get_iqiyi_detail(12)
	get_i4_app_detail(16)
	get_sogou_detail(14)
	get_open_play_detail(7)
	get_m_baidu_detail(29)
	get_wandoujia_detail(23)
	get_coolpad_detail(9)
	get_91play_detail(27)
	get_gionee_detail(10)
	get_xiaomi_game_detail(5)
	get_wogame_detail(998)
	get_leveno_detail(11)
	get_lenovo_shop_detail(30)
	get_meizu_detail(25)
	get_wostore_detail(31)
	get_xiaomi_web_detail(999)
	get_log_info('get_hot_game_detail.log', subject='榜单详情监控')

def get_muzhiwan_detail():
	pass	

def get_itools_detail():
	#详情页面信息质量不高
	pass

def get_360_gamebox_web_detail():
	pass

if __name__ == '__main__':
	main()

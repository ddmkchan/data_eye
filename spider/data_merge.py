#!/usr/bin/env python
#encoding=utf-8

import sys
import requests
import json
import urllib
import traceback
from config import *
import re
from bs4 import BeautifulSoup
import time
import datetime

db_conn = new_session()

mylogger = get_logger('merge_data')

def main():
	count = 0
	mydict = {}
	from sqlalchemy import not_
	for ret in new_session().query(KC_LIST).filter(KC_LIST.title!=u'').filter(not_(KC_LIST.source.in_((21, 22)))).filter(KC_LIST.publish_date>=u'2015-10-01'):
		segs = re.split(u'-|\(|\)|（|）|：|:|[\s]*-|－', ret.title)
		if len(segs)>=2:
			if ret.title.startswith('(') or ret.title.startswith(u'（'): 
				mydict[ret.id] = segs[2]
			else:
				mydict[ret.id] = segs[0]
		else:
			mydict[ret.id] = ret.title
	out = {}
	titles = set(mydict.values())
	for t in titles:
		out[t] = []
	for k, v in mydict.iteritems():	
		if v in out:
			out[v].append(str(k))
	for title, ids in out.iteritems():
		publish_status = get_publish_status(ids)	
		detail =  get_game_detail(ids)
		if detail is not None:
			imgs, game_type, summary, download_num, comment_num, rating, pkg_size, author, version, topic_num_total = detail
			ins = db_conn.query(PublishGame).filter(PublishGame.name==title).first()
			#print title, ids, '*******', publish_status.get('logo', u'')
			if ins is None:
				count += 1
				item = PublishGame(**{
									'name': title,
									'logo': publish_status.get('logo', u''),
									'imgs': imgs,
									'game_type': game_type,
									'summary': summary,
									'download_num': download_num,
									'comment_num': comment_num,
									'rating': rating,
									'pkg_size': pkg_size,
									'author': author,
									'version': version,
									'topic_num': topic_num_total,
									'kc_list_ids': publish_status.get('kc_list_ids', u''),
									'channels': publish_status.get('channel_list', u''),
									'publish_dates': publish_status.get('publish_date_list', u''),
									})
				db_conn.merge(item)
				if count % 500 == 0:
					db_conn.commit()
					mylogger.info("merge data %s commit ..." % count)		
			else:
				#ins.imgs = imgs
				#ins.game_type = game_type
				#ins.summary = summary
				ins.download_num = download_num
				ins.comment_num = comment_num
				ins.rating = rating
				#ins.pkg_size = pkg_size
				#ins.author = author
				#ins.version = version
				ins.topic_num = topic_num_total
				ins.logo  = publish_status.get('logo', u'')
				ins.channels = publish_status.get('channel_list', u'')
				ins.publish_dates = publish_status.get('publish_date_list', u'')
				ins.kc_list_ids = publish_status.get('kc_list_ids', u'')
				ins.last_update = datetime.datetime.now()
	db_conn.commit()

def get_publish_status(ids):
	out = {}
	l1 = []
	l2 = []
	logos = []
	_sql = "select b.name,publish_date, url from (select * from kc_list where id in (%s)) a join channel b on a.source=b.id order by publish_date" % ",".join(ids)
	for ret in db_conn.execute(_sql):
		channel, publish_date, img = ret
		l1.append(publish_date)
		l2.append(channel)
		if img:
			logos.append(img)
	out['publish_date_list'] = ",".join(l1)
	out['channel_list'] = ",".join(l2)
	out['kc_list_ids'] = ",".join(ids)
	if logos:
		out['logo'] = logos[0]
	return out

def get_game_detail(ids):
	imgs, game_type, summary, download_num, comment_num, rating, pkg_size, author, version, topic_num_total = [u''] * 10
	_sql =  "select max(dt) as dt, kc_id from game_detail_by_day where kc_id in (%s) group by kc_id" % (",".join(ids))
	for re in db_conn.execute(_sql):
		dt, kc_id = re
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.dt==dt).filter(GameDetailByDay.kc_id==kc_id).first()
		if ins is not None:
			if not imgs:
				imgs = ins.imgs
			if not game_type:
				game_type = ins.game_type
			if not summary:
				summary = ins.summary
			if not download_num or download_num == u'0':
				download_num = ins.download_num
			if not comment_num or comment_num == u'0':
				comment_num = ins.comment_num
			if not rating or rating == u'0':
				rating = ins.rating
			if not pkg_size:
				size = ins.pkg_size
				if ins.pkg_size and u'M' not in ins.pkg_size.upper() and u'G' not in ins.pkg_size.upper():
					size = "%sM" % round(int(ins.pkg_size)/1024.0/1024.0, 2)
				pkg_size = size
			if not author:
				author = ins.author
			if not version:
				version = ins.version
			if not topic_num_total or rating == u'0':
				topic_num_total = ins.topic_num_total
			return (imgs, game_type, summary, download_num, comment_num, rating, pkg_size, author, version, topic_num_total)
	return None


	#ids = (int(id) for id in ids)
	#for ret in db_conn.query(GameDetailByDay).filter(GameDetailByDay.dt==unicode(datetime.date.today()+datetime.timedelta(-1))).filter(GameDetailByDay.kc_id.in_(ids)):
	#	print ret.kc_id, ret.dt
		
def remove_duplicate_record():
	for rt in db_conn.execute("select source,title, publish_date, count(1) from kc_list where source=0 group by source, title, publish_date having count(1)>1;"):
		source, title, publish_date, count = rt
		print title, publish_date
		ins = db_conn.execute("select min(id) from kc_list where source=%s and publish_date=\'%s\' and title=\'%s\'" % (source, publish_date, title)).first()
		print 'delete %s' % ins[0]
		delete_record = db_conn.query(KC_LIST).filter(KC_LIST.id==ins[0]).one()
		db_conn.delete(delete_record)
	db_conn.commit()


def func():
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.title2!=u'').filter(KC_LIST.source.in_((7, 9, 10, 12, 14, 15, 25, 13, 16, 26, 27, 24))):
		ret.game_id = ret.title2
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.title2!=u'').filter(KC_LIST.source.in_((4, 11, 28))):
		ret.pkg_name = ret.title2
	db_conn.commit()

def get_urls_from_db_by_ids(ids, name):
    ids = (int(id) for id in ids)
    return [re.url for re in db_conn.query(HotGames.url).filter(HotGames.url!=u'').filter(HotGames.source.in_(ids)).filter(HotGames.url!='\t').filter(HotGames.name==name).distinct()]


def func2():
	from get_hot_game_detail_by_day import channel_map
	#for rt in db_conn.execute("select channel, identifying from hot_game_detail_by_day where channel=29 group by channel, identifying"):
	#	channel, name = rt
	#	ids = channel_map.get(channel)
	#	urls = get_urls_from_db_by_ids(ids, name)
	#	if len(urls)>=2:
	#		print channel, name, ids
	#		if len(urls[0].split('\t')) >= 2:
	#			pkg_name, pkg_id = urls[0].split('\t')
	#			db_conn.execute("update table hot_game_detail_by_day set identifying=\'%s\' where channel=%s and name=\'%s\'" % (pkg_name, channel, name))
	#for rt in db_conn.execute("select channel, identifying from hot_game_detail_by_day where channel=10 group by channel, identifying"):
	#	channel, name = rt
	#	ids = channel_map.get(channel)
	#	urls = get_urls_from_db_by_ids(ids, name)
	#	if len(urls)>=2:
	#		print channel, name, ids
	#		if len(urls[0].split('\t')) >= 2:
	#			pkg_name, pkg_id = urls[0].split('\t')
	#			db_conn.execute("update table hot_game_detail_by_day set identifying=\'%s\' where channel=%s and name=\'%s\'" % (pkg_name, channel, name))


	ids = channel_map.get(2)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if rt.url and rt.url!=u'\t':
			rt.identifying = ret.url
	
	ids = channel_map.get(4)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if len(rt.url.split('\t'))>=2:
			pkg_name, pkg_id = rt.url.split('\t')
			rt.identifying = u"http://125.88.193.234/mintf/getAppInfoByIds?pname=%s" % pkg_name
	
	ids = channel_map.get(28)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if len(rt.url.split('\t'))>=2:
			pkg_name, pkg_id = rt.url.split('\t')
			rt.identifying = u"http://next.gamebox.360.cn/7/xgamebox/getappintro?pname=%s" % pkg_name
	
	ids = channel_map.get(0)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if rt.url and rt.url!=u'\t':
			rt.identifying = ret.url
	
	ids = channel_map.get(24)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if len(rt.url.split('\t'))>=2:
			pkg_name, pkg_id = rt.url.split('\t')
			rt.identifying = pkg_id
	
	ids = channel_map.get(8)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if len(rt.url.split('\t'))>=2:
			pkg_name, pkg_id = rt.url.split('\t')
			rt.identifying = u"ttp://info.gamecenter.vivo.com.cn/clientRequest/gameDetail?id=%s&adrVerName=4.4.4&appVersion=37" % pkg_id
	
	ids = channel_map.get(26)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if len(rt.url.split('\t'))>=2:
			pkg_name, pkg_id = rt.url.split('\t')
			rt.identifying = pkg_id
	
	ids = channel_map.get(13)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if rt.url and rt.url!=u'\t':
			rt.identifying = rt.url
	
	ids = channel_map.get(3)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if len(rt.url.split('\t'))>=2:
			pkg_name, pkg_id = rt.url.split('\t')
			rt.identifying = u"http://m5.qq.com/app/getappdetail.htm?pkgName=%s&sceneId=0" % pkg_name
	
	ids = channel_map.get(15)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if len(rt.url.split('\t'))>=2:
			pkg_name, pkg_id = rt.url.split('\t')
			rt.identifying = rt.url
	
	ids = channel_map.get(19)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if rt.url and rt.url!=u'\t':
			rt.identifying = rt.url

	
	ids = channel_map.get(12)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if rt.url and rt.url!=u'\t':
			rt.identifying = rt.url

	ids = channel_map.get(16)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if len(rt.url.split('\t'))>=2:
			pkg_name, pkg_id = rt.url.split('\t')
			rt.identifying = u"http://app3.i4.cn/controller/action/online.go?store=3&module=1&id=%s&reqtype=5" % pkg_id

	ids = channel_map.get(14)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if len(rt.url.split('\t'))>=2:
			pkg_name, pkg_id = rt.url.split('\t')
			rt.identifying = u"http://mobile.zhushou.sogou.com/m/appDetail.html?id=%s" % pkg_id

	ids = channel_map.get(7)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if rt.url and rt.url!=u'\t':
			rt.identifying = rt.url

	ids = channel_map.get(29)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if len(rt.url.split('\t'))>=2:
			pkg_name, pkg_id = rt.url.split('\t')
			rt.identifying = u"http://m.baidu.com/appsrv?native_api=1&psize=3&pkname=%s&action=detail&docid=%s" % (pkg_name, pkg_id)

	ids = channel_map.get(23)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if rt.url and rt.url!=u'\t':
			rt.identifying = rt.url

	ids = channel_map.get(9)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if len(rt.url.split('\t'))>=2:
			pkg_name, pkg_id = rt.url.split('\t')
			rt.identifying = pkg_id

	ids = channel_map.get(27)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if len(rt.url.split('\t'))>=2:
			pkg_name, pkg_id = rt.url.split('\t')
			rt.identifying = pkg_id

	ids = channel_map.get(10)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if len(rt.url.split('\t'))>=2:
			pkg_name, pkg_id = rt.url.split('\t')
			rt.identifying = u"http://game.gionee.com/Api/Local_Gameinfo/getDetails?gameId=%s" % pkg_id

	ids = channel_map.get(5)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if rt.url:
			rt.identifying = rt.url

	ids = channel_map.get(998)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if len(rt.url.split('\t'))>=2:
			pkg_name, pkg_id = rt.url.split('\t')
			rt.identifying = pkg_id

	ids = channel_map.get(11)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if rt.url:
			rt.identifying = u"http://yx.lenovomm.com/business/app!getAppDetail5.action?dpi=480&height=1920&dev=ph&width=1080&cpu=armeabi-v7a&pn=%s&uid=72DB07100FC223A2EDE82F4A44AE96B4&os=4.4.4&perf=hp&model=MI 4LTE&type=0&density=xx&mac=7A031DAB40535B3F5E204582EB961FC5" % rt.url

	ids = channel_map.get(30)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if rt.url:
			rt.identifying = u"http://223.202.25.30/ams/api/appinfo?l=zh-CN&pn=%s&vc=100150928&woi=0&pa=ams5.0_141623-2-2-19-1-3-1_480-8" % rt.url

	ids = channel_map.get(25)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if rt.url:
			rt.identifying = rt.url

	ids = channel_map.get(31)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if rt.url:
			rt.identifying = rt.url

	db_conn.commit()

if __name__ == '__main__':
	#main()
	#print get_publish_status([2516,2671,2941,3375,3389,3414,3518,3559,8131,8548,11442,11657,13088,13231,13516,13658,14067])
	#get_game_detail(['19084'])
	#remove_duplicate_record()
	func2()

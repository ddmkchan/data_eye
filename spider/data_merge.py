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

mylogger = get_logger('data_merge')

def main():
	count = 0
	mydict = {}
	from sqlalchemy import not_
	for ret in new_session().query(KC_LIST).filter(KC_LIST.title!=u'').filter(not_(KC_LIST.source.in_((21, 22)))).filter(KC_LIST.status==0).filter(KC_LIST.publish_date>=u'2015-10-01'):
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
	mylogger.info("merge new publish game %s" % len(titles))
	for t in titles:
		out[t.lower()] = []
	for k, v in mydict.iteritems():	
		title = v.lower()
		if title in out:
			out[title].append(str(k))
	for title, ids in out.iteritems():
		publish_status = get_publish_status(ids)	
		detail =  get_game_detail(ids)
		if detail is not None:
			imgs, game_type, summary, download_num, comment_num, rating, pkg_size, author, version, topic_num_total = detail
		else:
			imgs, game_type, summary, download_num, comment_num, rating, pkg_size, author, version, topic_num_total = [u''] * 10
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
			if count % 1000 == 0:
				db_conn.commit()
				mylogger.info("merge data %s commit ..." % count)	
		else:
			ins.imgs = imgs
			ins.game_type = game_type
			ins.summary = summary
			ins.download_num = download_num
			ins.comment_num = comment_num
			ins.rating = rating
			ins.pkg_size = pkg_size
			ins.author = author
			ins.version = version
			ins.topic_num = topic_num_total
			ins.logo  = publish_status.get('logo', u'')
			ins.channels = publish_status.get('channel_list', u'')
			ins.publish_dates = publish_status.get('publish_date_list', u'')
			ins.kc_list_ids = publish_status.get('kc_list_ids', u'')
			ins.last_update = datetime.datetime.now()
	db_conn.commit()
	mylogger.info("merge data done !!!")	

def get_publish_status(ids):
	out = {}
	l1 = []
	l2 = []
	logos = []
	_sql = "select b.name,publish_date, img from (select * from kc_list where id in (%s)) a join channel b on a.source=b.id order by publish_date" % ",".join(ids)
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
			if not topic_num_total or topic_num_total == u'0':
				topic_num_total = ins.topic_num_total
			return (imgs, game_type, summary, download_num, comment_num, rating, pkg_size, author, version, topic_num_total)
	return None


	#ids = (int(id) for id in ids)
	#for ret in db_conn.query(GameDetailByDay).filter(GameDetailByDay.dt==unicode(datetime.date.today()+datetime.timedelta(-1))).filter(GameDetailByDay.kc_id.in_(ids)):
	#	print ret.kc_id, ret.dt

if __name__ == '__main__':
	main()

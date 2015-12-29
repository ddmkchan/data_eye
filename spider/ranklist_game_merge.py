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

def hot_games_merge():
	count = 0
	mydict = {}
	from sqlalchemy import not_
	for ret in db_conn.execute("select identifying, name from hot_games where status=0 and identifying!='' group by identifying, name"):
		identifying, name = ret
		segs = re.split(u'-|\(|\)|（|）|：|:|[\s]*-|－', name)
		if len(segs)>=2:
			if name.startswith('(') or name.startswith(u'（'): 
				mydict[identifying] = segs[2]
			else:
				mydict[identifying] = segs[0]
		else:
			mydict[identifying] = name
	out = {}
	titles = set(mydict.values())
	for t in titles:
		out[t] = []
	mylogger.info("merge hot games %s" % len(titles))
	for k, v in mydict.iteritems():	
		if v in out:
			out[v].append(k)
	for title, ids in out.iteritems():
		channel_info = get_channel_info_by_ids(ids)
		ranking_ids = channel_info.get('ranking_ids')
		logos = channel_info.get('logos')
		channel_ids = channel_info.get('channel_ids')
		if ranking_ids:
			ins = db_conn.query(RanklistGame).filter(RanklistGame.name==title).first()
			logo = logos[0] if len(logos)>=1 else u''
			if ins is None:
				count += 1
				item = RanklistGame(**{
										"name": title,
										"logo": logo, 
										"channel_ids": u",".join(channel_ids), 
										"ranklists": u",".join(ranking_ids),
										})
				db_conn.merge(item)
				if count % 500 == 0:
					mylogger.info("hot games merge %s commit" % count)
					db_conn.commit()
			else:
				ins.logo = logo
				ins.channel_ids = u",".join(channel_ids)
				ins.ranklists = u",".join(ranking_ids)
				ins.last_update = datetime.datetime.now()
	db_conn.commit()
	
def get_channel_info_by_ids(ids):
	ranking_2_channel = get_ranking_2_channel()
	logos = []
	ranking_ids = []
	channel_ids = set([])
	ids = ["\'%s\'" %i for i in ids]
	for ret in db_conn.execute("select source, identifying from hot_games where identifying in (%s) group by source, identifying" % ",".join(ids)):
		source, identifying = ret
		ranking_ids.append("%s^%s" % (source, identifying))
		ins = db_conn.query(HotGames).filter(HotGames.source==source).filter(HotGames.identifying==identifying).first()
		if ins is not None:
			logos.append(ins.img)
		channel_id = ranking_2_channel.get(str(source), -1)
		if channel_id != -1:
			channel_ids.add(unicode(channel_id))
		#else:
		#	mylogger.info("source id # %s # has no channel_id" % source)
	return {'ranking_ids' : ranking_ids, 'logos': logos, 'channel_ids': channel_ids}

def get_ranking_2_channel():
	mydict = {}
	for ret in db_conn.execute("select * from channel_to_ranking"):
		channel_id, ranking_id= ret
		mydict[str(ranking_id)] = channel_id
	return mydict

def get_game_detail(ranklists):
	ranking_2_channel = get_ranking_2_channel()
	imgs, game_type, summary, download_num, comment_num, rating, pkg_size, author, version, topic_num_total = [u''] * 10
	for seg in ranklists.split(','):
		source, identifying = seg.split('^')
		channel = ranking_2_channel.get(source, -1)
		if channel != -1:
			_sql =  "select max(dt) as dt, identifying, channel from hot_game_detail_by_day where identifying=\'%s\' and channel=%s group by identifying, channel" % (identifying, channel)
			rs = db_conn.execute(_sql).fetchone()
			if rs is not None:
				dt, identifying, channel = rs
				ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.identifying==identifying).filter(HotGameDetailByDay.channel==channel).first()
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
						#size = ins.pkg_size
						#if ins.pkg_size and u'M' not in ins.pkg_size.upper() and u'G' not in ins.pkg_size.upper():
						#	size = "%sM" % round(int(ins.pkg_size)/1024.0/1024.0, 2)
						pkg_size = ins.pkg_size
					if not author:
						author = ins.author
					if not version:
						version = ins.version
					if not topic_num_total or topic_num_total == u'0':
						topic_num_total = ins.topic_num_total
	return (imgs, game_type, summary, download_num, comment_num, rating, pkg_size, author, version, topic_num_total)


def get_hot_game_info():
	count =0
	for ret in db_conn.query(RanklistGame):
		detail = get_game_detail(ret.ranklists)
		imgs, game_type, summary, download_num, comment_num, rating, pkg_size, author, version, topic_num_total = detail
		ins = db_conn.query(RanklistGameDetail).filter(RanklistGameDetail.id==ret.id).first()
		if ins is None:
			count += 1
			item = RanklistGameDetail(**{
								'id': ret.id,
								'name': ret.name,
								'logo': ret.logo,
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
			ins.logo = ret.logo
			ins.last_update = datetime.datetime.now()
	db_conn.commit()
	mylogger.info("merge ranklist game data done !!!")	

		
if __name__ == '__main__':
	hot_games_merge()
	get_hot_game_info()

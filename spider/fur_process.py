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

def remove_duplicate_record():
	for rt in db_conn.execute("select source,title, publish_date, count(1) from kc_list where source=0 group by source, title, publish_date having count(1)>1;"):
		source, title, publish_date, count = rt
		print title, publish_date
		ins = db_conn.execute("select min(id) from kc_list where source=%s and publish_date=\'%s\' and title=\'%s\'" % (source, publish_date, title)).first()
		print 'delete %s' % ins[0]
		delete_record = db_conn.query(KC_LIST).filter(KC_LIST.id==ins[0]).one()
		delete_record.status = -1
		#db_conn.delete(delete_record)
	db_conn.commit()


def func():
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.title2!=u'').filter(KC_LIST.source.in_((7, 9, 10, 12, 14, 15, 25, 13, 16, 26, 27, 24))):
		ret.game_id = ret.title2
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.title2!=u'').filter(KC_LIST.source.in_((4, 11, 28))):
		ret.pkg_name = ret.title2
	db_conn.commit()

def func2():
	ids = channel_map.get(2)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if rt.url and rt.url!=u'\t':
			rt.identifying = ret.url
	
	ids = channel_map.get(4)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if len(rt.url.split('\t'))>=2:
			pkg_name, pkg_id = rt.url.split('\t')
			rt.identifying = u"http://125.88.193.234/mintf/getAppInfoByIds?pname=%s" % pkg_name

	ids = channel_map.get(22)
	for rt in db_conn.query(HotGames).filter(HotGames.source.in_(ids)):
		if rt.url and rt.url!=u'\t':
			rt.identifying = ret.url

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


def get_urls_from_db_by_ids(ids, name):
	return [re.identifying for re in db_conn.query(HotGames.identifying).filter(HotGames.identifying!=u'').filter(HotGames.source.in_(ids)).filter(HotGames.name==name).filter(HotGames.status==0).distinct()]

def func3():
	from get_hot_game_detail_by_day import channel_map
	for rt in db_conn.execute("select channel, identifying from hot_game_detail_by_day where channel=29 group by channel, identifying"):
		channel, name = rt
		ids = channel_map.get(channel)
		urls = get_urls_from_db_by_ids(ids, name)
		print channel, name, ids
		if len(urls)>=2:
			print urls, '******'
			if len(urls[0].split('\t')) >= 2:
				pkg_name, pkg_id = urls[0].split('\t')
		elif len(urls)==1:
			print urls, '---------------'
			items  = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.channel==channel).filter(HotGameDetailByDay.identifying==name)
			for re in items:
				re.identifying = urls[0]
				re.last_update = datetime.datetime.now()

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
	mylogger.info("merge hot games %s" % len(mydict))
	for t in titles:
		out[t] = []
	for k, v in mydict.iteritems():	
		if v in out:
			out[v].append(k)
	for title, ids in out.iteritems():
		ranking_ids = get_channel_info_by_ids(ids)
		if ranking_ids:
			ins = db_conn.query(RankListGame).filter(RankListGame.name==title).first()
			if ins is None:
				count += 1
				item = RankListGame(**{
										"name": title,
										"ranklists": u",".join(ranking_ids),
										})
				db_conn.merge(item)
				if count % 500 == 0:
					mylogger.info("hot games merge %s commit" % count)
					db_conn.commit()
			else:
				ins.ranklists = u",".join(ranking_ids)
	db_conn.commit()
	
def get_ranking_name_map():
	mydict = {}
	for re in db_conn.query(ChannelToRanking):
		mydict[re.id] = re.name
	return mydict

def get_channel_info_by_ids(ids):
	ranking_ids = []
	#print "select source, identifying from hot_games where identifying in (\'%s\') group by source, identifying" % ",".join(ids)
	for ret in db_conn.execute("select source, identifying from hot_games where identifying in (\'%s\') group by source, identifying" % ",".join(ids)):
		source, identifying = ret
		ranking_ids.append("%s^%s" % (source, identifying))
	return ranking_ids


def get_hot_game_detail(identifying):
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

def get_error_record():
	for ret in db_conn.execute("select kc_id from game_detail_by_day where author!='' group by kc_id having count(distinct author)>=2"):
		_sql = "select kc_id, author, count(1) as total from game_detail_by_day where kc_id=%s group by kc_id, author order by total" % ret[0]
		for re in db_conn.execute(_sql):
			kc_id, author, total = re
			if total == 1:
				print kc_id, author, total 
				delete_record = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==kc_id).filter(GameDetailByDay.author==author).first()	
				if delete_record.dt < '2015-12-01': 
					print delete_record.dt, '***'
					db_conn.delete(delete_record)
					break
	db_conn.commit()

def get_game_author_by_ids(ids):
	mydict = {}
	ids = [str(i) for i in ids]
	_sql =  "select kc_id, author from game_detail_by_day where kc_id in (%s) group by kc_id, author" % (",".join(ids))
	for re in db_conn.execute(_sql):
		kc_id, author = re
		if author:
			mydict[kc_id] = author
	return mydict

def publish_games_merge():
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
		out[t] = []
	for k, v in mydict.iteritems():	
		if v in out:
			out[v].append(str(k))
	for title, ids in out.iteritems():
		unknown_ids = []
		author_to_ids = {}
		author_map = get_game_author_by_ids(ids)
		for kc_id in ids:
			author = author_map.get(int(kc_id), u'')
			if author:
				if author in author_to_ids:
					author_to_ids[author].append(kc_id)
				else:
					is_match = False
					for key in author_to_ids.keys():
						if author and key and (author in key or key in author):
							is_match =  True
							author_to_ids[key].append(kc_id)
					if not is_match:
						author_to_ids[author] = [kc_id]
			else:
				unknown_ids.append(kc_id)
		if len(unknown_ids) >= 2:
			count += 1
		if len(unknown_ids) == 1:
			count4 += 1
		if author_to_ids:
			#print title, ",".join(author_to_ids.keys())
			#print title, '****************'
			#for k, v in author_to_ids.iteritems():
			#	print k, v
			if len(author_to_ids.keys()) == 1:
				count2+=1
			if len(author_to_ids.keys()) > 1:
				count3+=1
		#print title, "check list: ", unknown_ids
	print count
	print count4
	print count2
	print count3

if __name__ == '__main__':
	#remove_duplicate_record()
	main()

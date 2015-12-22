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

def main():
	count = 0
	mydict = {}
	from sqlalchemy import not_
	for ret in new_session().query(HotGames).filter(HotGames.status==0):
		segs = re.split(u'-|\(|\)|（|）|：|:|[\s]*-|－', ret.name)
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
		print title, ids

if __name__ == '__main__':
	#remove_duplicate_record()
	main()

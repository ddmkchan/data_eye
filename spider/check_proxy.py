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

mylogger = get_logger('proxy_list')

s = requests.session()
db_conn = new_session()

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'}


def get_proxies():
	return [{rc.type: u"%s:%s" % (rc.ip, rc.port)} for rc in db_conn.query(ProxyList)]
		

def check_proxy(proxy):
	start = time.time()
	try:
		r = requests.get("http://www.sogou.com/", headers=headers)
		#r = requests.get("http://www.douban.com/", headers=headers, proxies = proxy)
		if r.status_code == 200:
			end = time.time()
			print proxy, end - start
	except Exception,e:
		mylogger.error("%s" % (traceback.format_exc()))
		

def test():
	count = 0
	URL = "http://zhushou.360.cn/list/index/cid/2/order/newest/?page=1"
	for p in get_proxies():
		r = s.get(URL, timeout=10)
		#r = s.get(URL, timeout=10, proxies=p)
		print p, r.status_code

def f():
	for re in db_conn.query(HotGames):
		re.dt = unicode(re.create_date.date())
	db_conn.commit()

if __name__ == '__main__':
	source_map = {
			u"百度手机助手web"	: 0,
			u"小米游戏活跃榜": 1,
			u"360助手web"	: 2,
			u"9游新游热榜"	: 3,
			u"9游新游期待榜"	: 4,
			u"360助手app单机榜"	: 5,
			u"360助手app网游榜"	: 6,
			u"360助手app新游榜"	: 7,
			u"应用宝pc端单机榜"	: 8,#应用宝
			u"应用宝pc端网游榜"	: 9,#应用宝
			u"应用宝pc端新游榜"	: 10,#应用宝
			u"百度手机助手app单机榜"	: 11,
			u"百度手机助手app网游榜"	: 12,
			u"百度手机助手app新游榜"	: 13,
			u"当乐新游榜"	: 14,
			u"小米游戏新品榜"	: 15,
			u"vivo单机榜"	: 16,
			u"vivo网游榜"	: 17,
			u"vivo新游榜"	: 18,
			u"金立活跃榜"	: 19,
			u"金立飙升榜"	: 20,
			u"酷派总榜"	: 21,
			u"酷派网游榜"	: 22,
			u"酷派新游榜"	: 23,
			u"爱游戏下载榜"	: 24,#爱游戏榜单
			u"爱游戏免费榜"	: 25,#爱游戏榜单
			u"爱游戏网游榜"	: 26,#爱游戏榜单
			u"豌豆荚单机榜"	: 27,
			u"豌豆荚网游榜"	: 28,
			u"爱奇艺下载榜"	: 29,
			u"爱奇艺飙升榜"	: 30,
			u"优酷单机榜"	: 31,
			u"优酷网游榜"	: 32,
			u"搜狗单机榜"	: 33,
			u"搜狗网游榜"	: 34,
			u"爱思助手排行榜"	: 35,
			u"pp助手排行榜"	: 36,
			u"快用助手排行榜"	: 37,
			u"itools排行榜"	: 38,
			u"xy助手"	: 39,
			u"酷玩汇下载榜"	: 40,
			u"360游戏大厅单机榜"	: 41,
			u"360游戏大厅网游榜"	: 42,
			u"应用宝pc端下载榜"	: 43,
			u"百度手机助手app精品榜"	: 44,
			u"爱游戏飙升榜"	: 45,
			u"18183新游期待榜"	: 46,
			u"18183热门手游榜"	: 47,
			u"360助手app期待榜"	: 48,
			u"小米游戏下载榜"	: 49,
			u"小米游戏新网游"	: 50,
				}
	for k,v in source_map.iteritems():
		ins = db_conn.query(RankingChannel).filter(RankingChannel.id==v).first()
		if not ins:
			item = RankingChannel(**{'id': v, 'name':k})
			db_conn.merge(item)
		else:
			ins.name = k
	db_conn.commit()


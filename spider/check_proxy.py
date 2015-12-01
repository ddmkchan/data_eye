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
	#test()
	f()

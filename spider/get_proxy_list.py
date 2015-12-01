#!/usr/bin/env python
#encoding=utf-8

import sys
import requests
import json
import urllib
import traceback
import re
import sys
from bs4 import BeautifulSoup
import time

from config import *
mylogger = get_logger('proxy_list')

s = requests.session()
db_conn = new_session()

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'}


def get_xici_nn_proxy_list(page):
	URL = "http://www.xicidaili.com/nn/%s" % page
	try:
		response = s.get(URL, timeout=10, headers=headers)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			tb = soup.find('table', id='ip_list')
			if tb is not None:
				for tr in tb.find_all('tr')[1:]:
					tds = [i.text.strip() for i in tr.find_all('td')]
					if len(tds) == 10:
						a, b, ip, port, location, is_anonymity, type, c, d, check_time = tds
						#print ip, port
						ins = db_conn.query(ProxyList).filter(ProxyList.ip==ip).filter(ProxyList.port==port).first()
						if not ins:
							item = ProxyList(**{
											"ip": ip,
											"port": port,
											"location": location,
											"is_anonymity": is_anonymity,
											"type": type,
											"check_time": u"20" + check_time,
										})
							db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	db_conn.commit()

def get_kd_proxy_list(page):
	URL = "http://www.kuaidaili.com/free/intr/%s/" % page
	try:
		response = s.get(URL, timeout=10, headers=headers)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text)
			tb = soup.find('table', class_='table table-bordered table-striped')
			if tb is not None:
				for tr in tb.find_all('tr')[1:]:
					tds = [i.text.strip() for i in tr.find_all('td')]
					if len(tds) == 7:
						ip, port, is_anonymity, type, location, _, check_time = tds
						ins = db_conn.query(ProxyList).filter(ProxyList.ip==ip).filter(ProxyList.port==port).first()
						if not ins:
							item = ProxyList(**{
											"ip": ip,
											"port": port,
											"location": location,
											"is_anonymity": is_anonymity,
											"type": type,
											"check_time": check_time,
										})
							db_conn.merge(item)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
	db_conn.commit()

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
	try:
		response = s.get(URL, timeout=10)
	except Exception,e:
		mylogger.error("%s\t%s" % (URL, traceback.format_exc()))
		response = T(404)

if __name__ == '__main__':
	mylogger.info('get proxy start ...')
	get_xici_nn_proxy_list(1)
	get_kd_proxy_list(1)
	#for p in get_proxies():
	#	check_proxy(p)

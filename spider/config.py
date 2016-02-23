#!/usr/bin/env python
#encoding=utf-8

import sys
import socket

localIP = socket.gethostbyname(socket.gethostname())#这个得到本地ip

if localIP == u'192.168.1.215':
	sys.path.append('/root/yanpengchen/data_eye/common')
	sys.path.append('/data2/yanpengchen/data_eye/common')
	EXECUTABLE_PATH = '/data2/yanpengchen/phantomjs-2.0.0/bin/phantomjs'
	LOG_PATH = '/data2/yanpengchen/logs'
else:
	sys.path.append('/home/cyp/data_eye/common')
	EXECUTABLE_PATH = '/home/cyp/phantomjs-2.0.0/bin/phantomjs'
	LOG_PATH = '/home/cyp/logs'

from get_logger import *
from define import *
from model import *

check_date = date.today()+timedelta(-3)

db_conn = new_session()

proxies = [{rc.type: u"%s:%s" % (rc.ip, rc.port)} for rc in db_conn.query(ProxyList).filter(ProxyList.status==0).filter(ProxyList.check_time>=unicode(check_date))]


def set_proxy_invalid(proxy):
	for http_type, v in proxy.iteritems():
		ip, port = v.split(u':')
		ins = db_conn.query(ProxyList).filter(ProxyList.ip==ip).filter(ProxyList.port==port).filter(ProxyList.type==http_type).first()
		if ins is not None:
			ins.status = -1
	db_conn.commit()

from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

def get_page_source_by_phantomjs(url, delay=0.5, proxy={}):
	from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

	service_args = []
	#if proxy:
	#	service_args = [
    #	'--proxy=%s' % proxy.values()[0],
    #	'--proxy-type=%s' % proxy.keys()[0].lower(),
    #	]
	user_agent = (
	    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " +
	    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36"
	)
	
	dcap = dict(DesiredCapabilities.PHANTOMJS)
	dcap["phantomjs.page.settings.userAgent"] = user_agent
	dcap["phantomjs.page.settings.resourceTimeout"] = ("5000")


	driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=service_args, executable_path=EXECUTABLE_PATH)  #这要可能需要制定phatomjs可执行文件的位置
	driver.get(url)
	sleep(delay)
	pg = driver.page_source
	driver.quit
	return pg

def get_log_info(log_file, rows=-150, subject='监控'):
	import os
	from email_client import send_email
	try:
		logfile = "%s/%s" % (LOG_PATH, log_file)
		os.system("sed -i /InsecurePlatformWarning/d %s" % logfile)
		os.system("sed -i /SAWarning/d %s" % logfile)
		os.system("sed -i /util.ellipses_string/d %s" % logfile)
		with open(logfile) as f:
			send_email(SUBJECT=subject, TEXT="".join(f.readlines()[rows:]))
	except Exception,e:
		pass

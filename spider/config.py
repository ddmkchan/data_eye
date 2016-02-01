#!/usr/bin/env python
#encoding=utf-8

import sys
import socket

localIP = socket.gethostbyname(socket.gethostname())#这个得到本地ip

if localIP == u'192.168.1.215':
	sys.path.append('/root/yanpengchen/data_eye/common')
	sys.path.append('/data2/yanpengchen/data_eye/common')
else:
	sys.path.append('/home/cyp/data_eye/common')

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


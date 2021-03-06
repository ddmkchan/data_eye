#!/usr/bin/env python
#encoding=utf-8

import sys
import socket

localIP = socket.gethostbyname(socket.gethostname())#这个得到本地ip

if localIP == u'192.168.1.215':
	sys.path.append('/root/yanpengchen/data_eye/common')
else:
	sys.path.append('/home/cyp/data_eye/common')

from get_logger import *
from define import *
from model import *

check_date = date.today()+timedelta(-3)

proxies = [{rc.type: u"%s:%s" % (rc.ip, rc.port)} for rc in new_session().query(ProxyList).filter(ProxyList.check_time>=unicode(check_date))]

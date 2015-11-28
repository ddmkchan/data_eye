#!/usr/bin/env python
#encoding=utf-8

import sys
sys.path.append('/home/cyp/Utils/common')
from define import *
from model import *
import requests
import datetime
import json
import re
from bs4 import BeautifulSoup
from time import sleep
import traceback
from get_logger import *
import random
import xmltodict

import random
db_conn = new_session()
s = requests.session()
mylogger = get_logger('get_game_detail')

proxies = [{rc.type: u"%s:%s" % (rc.ip, rc.port)} for rc in db_conn.query(ProxyList)]

class T:
	
	def __init__(self, status_code):
		self.status_code = status_code


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'}

def get_proxies():
	return [{rc.type: u"%s:%s" % (rc.ip, rc.port)} for rc in db_conn.query(ProxyList)]

def get_360_web_detail():
	mylogger.info("get 360 detail start ...")
	count = 0
	err_times = 0
	dt = unicode(datetime.date.today())
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.publish_date>=u'2015-10-01').filter(KC_LIST.source==22).filter(KC_LIST.url!=''):
		if err_times >= 10:
			mylogger.error("reach max error_times")
			break
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			try:
				p = proxies[random.randrange(len(proxies))]
				r = s.get(ret.url, timeout=10, headers=headers, proxies=p)
			except Exception,e:
				r = T(404)
				err_times += 1
				sleep(3.21)
				mylogger.error("%s\t%s" % (ret.url.encode('utf-8'), traceback.format_exc()))
			if r.status_code == 200:
				soup = BeautifulSoup(r.text)
				imgs = u''
				rating = u''
				summary = u''
				comment_num = u''
				download_num = u''
				pkg_size = u''
				pf = soup.find('div', class_='pf')
				if pf is not None:
					for li in pf.find_all('span'):
						if u'分' in li.text:
							if re.search('\d+', li.text) is not None:
								rating = re.search('\d+', li.text).group()
						elif u'评价' in li.text:
							if re.search('\d+', li.text) is not None:
								comment_num = re.search('\d+', li.text).group()
						elif u'下载' in li.text:
							if re.search('\d+', li.text) is not None:
								download_num = re.search('\d+', li.text).group()
						elif u'M' in li.text:
							pkg_size = li.text
				breif = soup.find('div', class_='breif')
				if breif is not None:
					summary = breif.text
				viewport = soup.find('div', class_='viewport')
				icons = []
				if viewport is not None:
					for icon in viewport.find_all('img'):
						icons.append(icon.get('src'))
				if icons:
					imgs = u','.join(icons)

				count += 1
				item = GameDetailByDay(**{'kc_id': ret.id,
											'dt' : dt,
											'imgs' : imgs,
											'summary' : summary,
											'pkg_size' : pkg_size,
											'rating' : rating,
											'comment_num' : comment_num,
											'download_num' : download_num,
											})
				db_conn.merge(item)
				if count % 100 == 0:
					mylogger.info("360 detail %s commit" % count)
					db_conn.commit()
	mylogger.info("get 360 detail %s" % count)
	db_conn.commit()


if __name__ == '__main__':
	get_360_web_detail()

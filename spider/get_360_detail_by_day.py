#!/usr/bin/env python
#encoding=utf-8

import requests
import json
import re
from bs4 import BeautifulSoup
from time import sleep
import traceback
from config import *
import random
import xmltodict
import datetime

import random
db_conn = new_session()

from get_hot_game_detail_by_day import channel_map, mylogger


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'}


def get_360zhushou_web_detail(channel_id):
	count = 0
	error_times = 0
	sess = requests.session()
	mylogger.info("get 360zhushou web detail start ...")
	ids = channel_map.get(channel_id)
	_sql = "select name, url from hot_games where source in (%s) and url!='' group by name, url" % ",".join([str(i) for i in ids])
	mylogger.info("### %s ###" % _sql)
	for ret in db_conn.execute(_sql):
		name, url = ret
		if error_times >= 20:
			mylogger.info("360zhushou web  detail reach max error times ... ")
			break
		dt = unicode(datetime.date.today())
		ins = db_conn.query(HotGameDetailByDay).filter(HotGameDetailByDay.name==name).filter(HotGameDetailByDay.dt==dt).filter(HotGameDetailByDay.channel==channel_id).first()
		if not ins:
			try:
				p = proxies[random.randrange(len(proxies))]
				r = sess.get(url, timeout=20, headers=headers, proxies=p)
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
								if re.search('\d+\.*\d+', li.text) is not None:
									rating = re.search('\d+\.*\d+', li.text).group()
							#elif u'评价' in li.text:
							#	if re.search('\d+', li.text) is not None:
							#		comment_num = re.search('\d+', li.text).group()
							elif u'下载' in li.text:
								#if re.search('\d+', li.text) is not None:
								download_num = li.text
							elif u'M' in li.text:
								pkg_size = li.text
					breif = soup.find('div', class_='html-brief')
					icons = []
					if breif is not None:
						summary = breif.text
						icons = [img.get('src') for img in breif.find_all('img')]
					if icons:
						imgs = u','.join(icons)
					mydict = {}
					base_info = soup.find('div', class_="base-info")
					if base_info is not None:
						for td in base_info.find_all('td'):
							segs = td.text.split(u'：')
							if len(segs) == 2:
								mydict[segs[0]] = segs[1]
					count += 1
					item = HotGameDetailByDay(**{
												'name': name,
												'channel': channel_id,
												'dt' : dt,
												'imgs' : imgs,
												'summary' : summary,
												'pkg_size' : pkg_size,
												'rating' : rating,
												'author' : mydict.get(u'作者', u''),
												'comment_num' : comment_num,
												'download_num' : download_num,
												})
					db_conn.merge(item)
					if count % 100 == 0:
						mylogger.info("360 detail %s commit" % count)
						db_conn.commit()
			except Exception,e:
				error_times += 1
				sleep(3.21)
				mylogger.error("%s\t%s" % (url.encode('utf-8'), traceback.format_exc()))
	mylogger.info("get 360zhushou web detail %s" % count)
	db_conn.commit()


if __name__ == '__main__':
	get_360zhushou_web_detail(22)

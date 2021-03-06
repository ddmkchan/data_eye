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

db_conn = new_session()

from get_game_detail_by_day import mylogger, step2

import random

class T:
	
	def __init__(self, status_code):
		self.status_code = status_code

class EX:
	
	msg = ""

def get_pp_detail():
	count = 0
	mylogger.info("get pp detail start ...")
	for ret in db_conn.query(KC_LIST).filter(KC_LIST.game_id!=u'').filter(KC_LIST.source==24):
		dt = unicode(datetime.date.today())
		ins = db_conn.query(GameDetailByDay).filter(GameDetailByDay.kc_id==ret.id).filter(GameDetailByDay.dt==dt).first()
		if not ins:
			g = get_pp_detail_by_id(ret.game_id)
			if g is not None:	
				comments_info = get_pp_comments_by_id(ret.game_id)
				count += 1 
				item = GameDetailByDay(**{
											'kc_id': ret.id,
											'summary' : g.get('content', u''),
											'version' : g.get('ver', u''),
											'game_type' : g.get('catName', u''),
											'pkg_size' : g.get('fileSize', u''),
											'comment_num' : comments_info.get('commentCount', u''),
											'download_num' : g.get('downCount', u''),
											'topic_num_total' : g.get('collectCount', u''),
											'rating' : g.get('allVerStar', u''),
											'dt' : dt,
											'imgs' : g.get('ipadImgs', u''),
												})
				db_conn.merge(item)
				if count % 50 == 0:
					sleep(3)
					mylogger.info("pp detail commit %s" % count)
					db_conn.commit()
				if count % 20 == 0:
					sleep(1.23)
	mylogger.info("get pp detail %s" % count)
	db_conn.commit()


def get_pp_detail_by_id(gid):
	try:
		d = {"site":1, "id": gid}
		p = proxies[random.randrange(len(proxies))]
		r = requests.post('http://pppc2.25pp.com/pp_api/ios_appdetail.php', data=d, proxies=p)
		return r.json()
	except Exception,e:
		mylogger.error("get %s detail \t%s" % (gid.encode('utf-8'), traceback.format_exc()))
	return None

def get_pp_comments_by_id(gid):
	try:
		d = {"s":1, "a":101, "i": gid, "p":1, "l":1}
		p = proxies[random.randrange(len(proxies))]
		r = requests.post('http://pppc2.25pp.com/pp_api/comment.php', data=d, proxies=p)
		if r.status_code == 200:
			return r.json()
	except Exception,e:
		mylogger.error("get %s comments \t%s" % (gid.encode('utf-8'), traceback.format_exc()))
	return {}

if __name__ == '__main__':
	get_pp_detail()
	step2()

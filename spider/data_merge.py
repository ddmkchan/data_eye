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

def main():
	mydict = {}
	for ret in new_session().query(KC_LIST):
		segs = re.split(u'-|\(|（|：|:|[\s]*-|－', ret.title)
		if len(segs)>=2:
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
		get_publish_status(ids)	

def get_publish_status(ids):
	_sql = "select publish_date, status, device from kc_list where id in (%s)" % ",".join(ids)
	
	print _sql


def get_game_detail(ids):
	pass
		
def remove_duplicate_record():
	for rt in db_conn.execute("select source,title, publish_date, count(1) from kc_list where source=0 group by source, title, publish_date having count(1)>1;"):
		source, title, publish_date, count = rt
		print title, publish_date
		ins = db_conn.execute("select min(id) from kc_list where source=%s and publish_date=\'%s\' and title=\'%s\'" % (source, publish_date, title)).first()
		print 'delete %s' % ins[0]
		delete_record = db_conn.query(KC_LIST).filter(KC_LIST.id==ins[0]).one()
		db_conn.delete(delete_record)
	db_conn.commit()

if __name__ == '__main__':
	main()
	#remove_duplicate_record()
